"""Narration: ElevenLabs TTS per section (cached raw takes), then a deterministic audio edit.

    python tts.py                 # synthesize sections whose text/voice changed, then re-edit all
    python tts.py --force [ids]   # resynthesize every section (or only the listed ones)

Raw takes:   build/audio/raw/<id>.mp3  + build/raw_timing.json  (character-aligned word times)
Edited:      build/audio/<id>.wav      + build/timing.json      (what scenes and assembly use)

The edit never regenerates speech, so an approved performance stays exactly as it was:
  * tail clean-up — previous_text/next_text conditioning sometimes leaves a clipped fragment (a breath
    or the start of the next sentence) in the last ~100 ms; it is cut at the preceding silence and faded.
  * pauses — narration.json "pauses" inserts silence after a phrase, at the quietest point of the gap
    between words, and shifts every later word time so cues stay locked to speech.
"""
import base64, hashlib, json, os, re, subprocess, sys

import numpy as np
import requests
from dotenv import load_dotenv

from common import ROOT, ffmpeg, load_narration

load_dotenv(ROOT / ".env")
CFG = load_narration()
RAW = ROOT / "build/audio/raw"
OUT = ROOT / "build/audio"
RAW.mkdir(parents=True, exist_ok=True)
FFMPEG = ffmpeg()
SR = 44100


def key(w):
    return re.sub(r"[^\w']", "", w.lower())


def words_from_alignment(al):
    """Collapse character timings into [{word, start, end, key}]."""
    words, cur, start, end = [], "", None, None
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch.isspace():
            if cur:
                words.append({"word": cur, "start": start, "end": end})
            cur, start = "", None
            continue
        if start is None:
            start = s
        cur += ch
        end = e
    if cur:
        words.append({"word": cur, "start": start, "end": end})
    for w in words:
        w["key"] = key(w["word"])
    return words


def synth(i, sec):
    secs = CFG["sections"]
    body = {"text": sec["text"], "model_id": CFG["model_id"], "voice_settings": CFG["voice_settings"],
            "previous_text": secs[i - 1]["text"] if i > 0 else None,
            "next_text": secs[i + 1]["text"] if i + 1 < len(secs) else None}
    r = requests.post(f"https://api.elevenlabs.io/v1/text-to-speech/{CFG['voice_id']}/with-timestamps",
                      params={"output_format": CFG.get("output_format", "mp3_44100_128")}, headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                      json=body, timeout=180)
    if r.status_code != 200:
        raise SystemExit(f"ElevenLabs TTS {r.status_code}: {r.text[:300]}")
    d = r.json()
    (RAW / f"{sec['id']}.mp3").write_bytes(base64.b64decode(d["audio_base64"]))
    return words_from_alignment(d["alignment"])


def decode(p):
    raw = subprocess.check_output([FFMPEG, "-v", "error", "-i", str(p), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32).copy()


def env_db(a, hop):
    n = len(a) // hop
    fr = a[:n * hop].reshape(n, hop)
    return 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)


def clean_tail(a, words):
    """Cut a clipped trailing fragment (sound that starts after a silence and runs into the file end)."""
    hop = SR // 100
    e = env_db(a, hop)
    if e[-3:].max() < -60:
        return a  # ends in silence already
    i = len(e) - 1
    while i > 0 and e[i] > -70:           # walk back through the fragment
        i -= 1
    j = i
    while j > 0 and e[j] <= -70:          # and through the silence before it
        j -= 1
    frag, gap = (len(e) - i) / 100, (i - j) / 100
    if frag < 0.4 and gap >= 0.1 and (j + 1) / 100 >= words[-1]["start"]:
        cut = (j + 1) * hop + int(0.05 * SR)
        a = a[:cut].copy()
    return a


def insert_pauses(a, words, pauses):
    """Insert silence after phrases; returns new audio and shifted words."""
    hop = SR // 200
    e = env_db(a, hop)
    edits = []
    for p in pauses:
        target = [key(x) for x in p["after"].split()]
        ks = [w["key"] for w in words]
        hits = [i for i in range(len(ks) - len(target) + 1) if ks[i:i + len(target)] == target]
        if not hits:
            raise KeyError(f"pause anchor {p['after']!r} not found")
        i = hits[0] + len(target) - 1
        lo, hi = words[i]["end"] - 0.05, (words[i + 1]["start"] + 0.05) if i + 1 < len(words) else words[i]["end"] + 0.3
        f0, f1 = int(lo * 200), max(int(lo * 200) + 1, int(hi * 200))
        t = (f0 + int(np.argmin(e[f0:f1]))) / 200 + 0.0025  # quietest 5 ms in the gap
        edits.append((t, p["sec"], i))
    for t, sec, i in sorted(edits, reverse=True):
        n = int(t * SR)
        a = np.concatenate([a[:n], np.zeros(int(sec * SR), np.float32), a[n:]])
        for w in words[i + 1:]:
            w["start"] += sec
            w["end"] += sec
    return a, words


def write_wav(a, p):
    fade = int(0.03 * SR)
    a = a.copy()
    a[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-c:a", "pcm_s16le", str(p)], input=a.tobytes(), check=True)


def main():
    force = "--force" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]  # optional: section ids to (re)synthesize
    rpath, tpath = ROOT / "build/raw_timing.json", ROOT / "build/timing.json"
    raw = json.loads(rpath.read_text()) if rpath.exists() else {"sections": {}}
    pauses = CFG.get("pauses", [])
    timing = {"lead_in": CFG["lead_in"], "tail": CFG["tail"], "sections": {}}
    for i, sec in enumerate(CFG["sections"]):
        h = hashlib.sha1(json.dumps([sec["text"], CFG["voice_id"], CFG["model_id"], CFG["voice_settings"]]).encode()).hexdigest()[:12]
        prev = raw["sections"].get(sec["id"])
        if (force and (not only or sec["id"] in only)) or not prev or prev.get("hash") != h \
                or not (RAW / f"{sec['id']}.mp3").exists():
            raw["sections"][sec["id"]] = {"hash": h, "words": synth(i, sec)}
            print(f"synth   {sec['id']}")
        words = [dict(w) for w in raw["sections"][sec["id"]]["words"]]
        a = decode(RAW / f"{sec['id']}.mp3")
        before = len(a) / SR
        a = clean_tail(a, words)
        trimmed = before - len(a) / SR
        a, words = insert_pauses(a, words, [p for p in pauses if p["section"] == sec["id"]])
        out = OUT / f"{sec['id']}.wav"
        write_wav(a, out)
        dur = len(a) / SR
        words[-1]["end"] = min(words[-1]["end"], dur)
        timing["sections"][sec["id"]] = {"hash": h, "audio": str(out.relative_to(ROOT)), "voice_dur": dur,
                                         "scene_dur": round(CFG["lead_in"] + dur + CFG["tail"], 3), "words": words}
        added = sum(p["sec"] for p in pauses if p["section"] == sec["id"])
        print(f"edit    {sec['id']:<14} {dur:6.2f}s  (+{added:.2f}s pauses, -{trimmed:.2f}s tail fragment)")
    rpath.write_text(json.dumps(raw, indent=1))
    tpath.write_text(json.dumps(timing, indent=1))
    print(f"total scene time {sum(s['scene_dur'] for s in timing['sections'].values()):.1f}s")


if __name__ == "__main__":
    main()
