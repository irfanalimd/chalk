"""Word-timed captions from ASR, spell-corrected against the script, burned in with libass.

    python captions.py build/master.mp4 build/final.mp4

1. faster-whisper transcribes the finished mix with word timestamps (timing comes from what is
   actually heard, not from what was planned).
2. ASR words are aligned to the script with difflib; matched words take the script's spelling
   (names like Besicovitch, Zahl, Sogge), while ASR tokens with digits ("1917") are kept as numerals.
3. Words are grouped into short single lines and written as ASS events: the spoken word is gold,
   words already said are white, words still to come are dimmed.
Also writes build/captions.srt for platforms that take sidecar subtitles.
"""
import difflib, json, re, subprocess, sys
from pathlib import Path

import numpy as np

from asr import transcribe

from common import ROOT, beats, ffmpeg, load_narration, load_project

FFMPEG = ffmpeg()
CAP = load_project().get("captions", {})  # {"font": "Avenir Next", "fontsdir": "/System/Library/Fonts"}
MAX_CHARS, MAX_WORDS, GAP_BREAK = 34, 7, 0.45
FONT_PX, CHAR_PX = 54, 25            # caption size and rough average glyph width at 1080p
SLOTS = [40, 110, 180, 250]               # candidate bottom margins (px), preferred first
BG_LUMA = 13                         # house background (#0B0D12)
GOLD, WHITE, DIM = "&H005AD4FF", "&H00FFFFFF", "&H70FFFFFF"  # ASS colours are &HAABBGGRR


def norm(w):
    return re.sub(r"[^\w']", "", w.lower().replace("’", "'"))


def asr_words(media):
    out = []
    for seg in transcribe(media, model="small.en", words=True):
        for w in seg.words:
            t = w.word.strip()
            if out and t.startswith("-"):  # whisper splits hyphenated words: "three" "-pointed"
                out[-1]["word"] += t
                out[-1]["end"] = w.end
            else:
                out.append({"word": t, "start": w.start, "end": w.end})
    return out


def planned_words():
    """Script words with their planned times (TTS alignment + beat offsets), or None if unavailable."""
    tp = ROOT / "build/timing.json"
    if not tp.exists():
        return None
    timing = json.loads(tp.read_text())
    out = []
    for b in beats():
        if "audio" in b:
            out += [{"word": w["word"], "start": b["voice_start"] + w["start"], "end": b["voice_start"] + w["end"]}
                    for w in timing["sections"][b["id"]]["words"]]
    return out


def correct(asr, script_text, planned=None):
    """Replace ASR spellings with script spellings wherever the alignment is confident, drop words the
    script never says (whisper hallucinates phrases like "Thank you." in silence), and fill script words
    whisper skipped (it occasionally drops a whole segment) from the planned TTS timings."""
    script = script_text.split()
    if planned is not None and len(planned) != len(script):
        planned = None  # tokenisation differs; can't map by index
    a, s = [norm(w["word"]) for w in asr], [norm(w) for w in script]
    out, filled = [], 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, s, autojunk=False).get_opcodes():
        if op == "delete":
            continue
        if op == "insert" or (op == "replace" and (j2 - j1) - (i2 - i1) >= 3):
            if planned is not None:
                out += [dict(planned[j], word=script[j]) for j in range(j1, j2)]
                filled += j2 - j1
            continue
        for k in range(i2 - i1):
            w = dict(asr[i1 + k])
            if (op == "equal" or i2 - i1 == j2 - j1) and not re.search(r"\d", w["word"]):
                w["word"] = script[j1 + k]
            out.append(w)
    if filled:
        print(f"filled {filled} words whisper skipped from planned timings")
    out.sort(key=lambda w: w["start"])
    return out


def lines(words):
    cur, out = [], []
    for i, w in enumerate(words):
        cur.append(w)
        text = " ".join(x["word"] for x in cur)
        nxt = words[i + 1] if i + 1 < len(words) else None
        brk = (nxt is None or len(text) + 1 + len(nxt["word"]) > MAX_CHARS or len(cur) >= MAX_WORDS
               or nxt["start"] - w["end"] > GAP_BREAK or (re.search(r"[.?!:;]$", w["word"]) and len(cur) >= 2)
               or (w["word"].endswith(",") and len(text) > MAX_CHARS * 0.55))
        if brk:
            out.append(cur)
            cur = []
    # No orphans: fold a one-word line back into the line before it when that stays readable.
    merged = []
    for g in out:
        if merged and len(g) == 1 and g[0]["start"] - merged[-1][-1]["end"] < GAP_BREAK \
                and len(" ".join(x["word"] for x in merged[-1] + g)) <= MAX_CHARS + 10:
            merged[-1] = merged[-1] + g
        else:
            merged.append(g)
    return merged


def content_map(video, fps=5, w=480, h=270):
    """Low-res luma frames of the clean master, to see where the picture has content."""
    raw = subprocess.check_output([FFMPEG, "-v", "error", "-i", str(video), "-vf", f"fps={fps},scale={w}:{h},format=gray",
                                   "-f", "rawvideo", "-"])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w), fps


def place(groups, frames, fps):
    """Pick, per caption line, the margin whose caption box overlaps the least picture content."""
    n, h, w = frames.shape
    sx = w / 1920
    margins = []
    for g in groups:
        text_w = len(" ".join(x["word"] for x in g)) * CHAR_PX + 160  # box plus breathing room
        x0, x1 = int((960 - text_w / 2) * sx), int((960 + text_w / 2) * sx)
        i0, i1 = int(g[0]["start"] * fps), int(g[-1]["end"] * fps) + 1
        clip = frames[max(0, i0):min(n, i1 + 1)]
        best, best_score = SLOTS[0], None
        for k, m in enumerate(SLOTS):
            y1 = int((1080 - m + 22) * sx)                 # clearance below the box
            y0 = int((1080 - m - FONT_PX - 50) * sx)       # and above it, so labels never touch
            region = clip[:, max(0, y0):y1, max(0, x0):x1].astype(np.int16)
            score = float((np.abs(region - BG_LUMA) > 30).mean()) if region.size else 0.0
            score += 0.004 * k  # mild preference for the lowest slot
            if best_score is None or score < best_score:
                best, best_score = m, score
        margins.append(best)
    return margins


def ts_ass(t):
    cs = max(0, round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def ts_srt(t):
    ms = max(0, round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_ass(groups, path, margins=None):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{CAP.get("font", "Avenir Next")},{FONT_PX},{WHITE},{WHITE},&H8C07090C,&H8C07090C,1,0,0,0,100,100,0.4,0,3,9,0,2,200,200,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    margins = margins or [SLOTS[0]] * len(groups)
    for gi, (g, mv) in enumerate(zip(groups, margins)):
        nxt = groups[gi + 1][0]["start"] - 0.1 if gi + 1 < len(groups) else 1e9
        for k, w in enumerate(g):
            start = w["start"] if k else w["start"] - 0.08
            end = g[k + 1]["start"] if k + 1 < len(g) else min(w["end"] + 0.35, nxt)  # never stack two lines
            parts = []
            for j, x in enumerate(g):
                col = GOLD if j == k else (WHITE if j < k else DIM)
                parts.append(f"{{\\1c{col[:2]}{col[4:]}&\\1a&H{col[2:4]}&}}{x['word']}")
            fad = "{\\fad(140,0)}" if k == 0 else ("{\\fad(0,160)}" if k == len(g) - 1 else "")
            ev.append(f"Dialogue: 0,{ts_ass(start)},{ts_ass(end)},Cap,,0,0,{mv},,{fad}{' '.join(parts)}")
    Path(path).write_text(head + "\n".join(ev) + "\n")


def write_srt(groups, path):
    blocks = [f"{i}\n{ts_srt(g[0]['start'])} --> {ts_srt(g[-1]['end'] + 0.2)}\n{' '.join(w['word'] for w in g)}\n"
              for i, g in enumerate(groups, 1)]
    Path(path).write_text("\n".join(blocks))


def main(src, dst):
    cfg = load_narration()
    script = " ".join(s["text"] for s in cfg["sections"])
    words = correct(asr_words(src), script, planned_words())
    (ROOT / "build/captions_words.json").write_text(json.dumps(words, indent=1))
    groups = lines(words)
    ass, srt = ROOT / "build/captions.ass", ROOT / "build/captions.srt"
    frames, fps = content_map(src)
    margins = place(groups, frames, fps)
    moved = sum(m != SLOTS[0] for m in margins)
    write_ass(groups, ass, margins)
    write_srt(groups, srt)
    vf = f"subtitles={ass}:fontsdir={CAP.get('fontsdir', '/System/Library/Fonts')}"
    subprocess.run([FFMPEG, "-v", "error", "-stats", "-y", "-i", src, "-vf", vf, "-c:v", "libx264", "-preset", "slow",
                    "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", dst], check=True)
    print(f"{len(words)} words, {len(groups)} caption lines ({moved} raised to avoid on-screen content) -> {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
