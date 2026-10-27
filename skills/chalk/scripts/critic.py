"""Critic: an automated QA pass over a finished video. Writes build/critic/report.md plus contact sheets
for a human (or model) to inspect.

    python critic.py build/final.mp4

Checks
  format     resolution, frame rate, duration vs the edit plan
  loudness   integrated LUFS and true peak (target -14 LUFS, <= -1 dBTP)
  defects    black frames, long freezes, clipping-level peaks
  transcript ASR of the final audio vs the script: word error rate and every mismatch
  sync       ASR word onsets vs planned onsets (catches drift between picture and voice)
  visuals    contact sheets every ~2.5 s and a frame either side of every cut
"""
import difflib, json, re, statistics, subprocess, sys
from pathlib import Path

from asr import transcribe
from common import ROOT, beats, ffmpeg, load_narration
from sheet import sheet

FFMPEG = ffmpeg()
OUT = ROOT / "build/critic"


def norm(w):
    return re.sub(r"[^\w']", "", w.lower())


def probe(v):
    d = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", v]))
    vs = next(s for s in d["streams"] if s["codec_type"] == "video")
    num, den = map(int, vs["r_frame_rate"].split("/"))
    return {"w": vs["width"], "h": vs["height"], "fps": num / den, "dur": float(d["format"]["duration"])}


def ff_stderr(args):
    return subprocess.run([FFMPEG, "-hide_banner", "-nostats", *args], capture_output=True, text=True).stderr


def main(video):
    OUT.mkdir(parents=True, exist_ok=True)
    rep, issues = [], []
    bs = beats()
    planned = sum(b["dur"] for b in bs)

    p = probe(video)
    rep.append(f"## Format\n{p['w']}x{p['h']} @ {p['fps']:.2f} fps, {p['dur']:.2f}s (plan {planned:.2f}s)")
    if abs(p["dur"] - planned) > 0.1:
        issues.append(f"duration {p['dur']:.2f}s differs from plan {planned:.2f}s")

    e = ff_stderr(["-i", video, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"])
    I = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", e)[-1])
    TP = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)[-1])
    rep.append(f"## Loudness\nintegrated {I:.1f} LUFS, true peak {TP:.1f} dBTP")
    if abs(I + 14) > 1: issues.append(f"loudness {I:.1f} LUFS (target -14)")
    if TP > -1: issues.append(f"true peak {TP:.1f} dBTP above -1")

    bl = re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", ff_stderr(["-i", video, "-vf", "blackdetect=d=0.4:pix_th=0.035", "-an", "-f", "null", "-"]))
    fr = re.findall(r"freeze_start: ([\d.]+)[\s\S]*?freeze_duration: ([\d.]+)", ff_stderr(["-i", video, "-vf", "freezedetect=n=0.0005:d=3", "-an", "-f", "null", "-"]))
    rep.append("## Defects\nblack: " + (", ".join(f"{a}-{b}s" for a, b in bl) or "none")
               + "\nfreezes >3s: " + (", ".join(f"{a}s (+{d}s)" for a, d in fr) or "none"))
    for a, b in bl:
        if float(a) > 0.2 and float(b) < p["dur"] - 0.5:
            issues.append(f"black frames mid-video {a}-{b}s")
    for a, d in fr:
        issues.append(f"picture static for {float(d):.1f}s from {float(a):.1f}s — check it is intentional")

    # Transcript vs script.
    cfg = load_narration()
    script = [w for s in cfg["sections"] for w in s["text"].split()]
    last_voice = max(b["voice_start"] + b["voice_dur"] for b in bs if "audio" in b)
    heard = [w for seg in transcribe(video, model="small.en", words=True) for w in seg.words
             if w.start < last_voice + 1.0]  # ignore ASR hallucinations in the silent tail
    a, s = [norm(w.word) for w in heard], [norm(w) for w in script]
    sm = difflib.SequenceMatcher(None, s, a, autojunk=False)
    errs, diffs = 0, []
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != "equal":
            errs += max(i2 - i1, j2 - j1)
            diffs.append(f"- script: “{' '.join(script[i1:i2])}”  heard: “{' '.join(w.word.strip() for w in heard[j1:j2])}”"
                         + (f" @ {heard[j1].start:.1f}s" if j1 < len(heard) else ""))
    wer = errs / max(1, len(s))
    rep.append(f"## Transcript\nWER vs script {wer:.1%} ({errs} edits / {len(s)} words). Numbers and spelling variants "
               "of names count as edits; read the list.\n" + "\n".join(diffs))
    if wer > 0.08: issues.append(f"transcript WER {wer:.1%}")

    # Sync: planned word onsets (ElevenLabs alignment + beat offsets) vs heard onsets.
    timing = json.loads((ROOT / "build/timing.json").read_text())
    plan_words = []
    for b in bs:
        if "audio" in b:
            plan_words += [(w["key"], b["voice_start"] + w["start"]) for w in timing["sections"][b["id"]]["words"]]
    pk = [k for k, _ in plan_words]
    offs = []
    for blk in difflib.SequenceMatcher(None, pk, a, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            offs.append(heard[blk.b + k].start - plan_words[blk.a + k][1])
    if offs:
        med, worst = statistics.median(offs), max(offs, key=abs)
        rep.append(f"## Sync\n{len(offs)} matched words; median offset {med * 1000:+.0f} ms, worst {worst * 1000:+.0f} ms")
        if abs(med) > 0.12: issues.append(f"voice/picture offset {med * 1000:+.0f} ms")

    # Visual sheets.
    n, step, page = 0, 2.5, 16
    times = [t * step + 0.6 for t in range(int(p["dur"] / step))]
    for i in range(0, len(times), page):
        sheet(video, OUT / f"sheet_{i // page:02d}.png", times=times[i:i + page], cols=4, width=480)
        n += 1
    cuts = []
    t = 0
    for b in bs[:-1]:
        t += b["dur"]
        cuts += [t - 0.12, t + 0.05]
    sheet(video, OUT / "cuts.png", times=cuts, cols=4, width=400)
    rep.append(f"## Visuals\n{n} contact sheets (every {step}s) and cuts.png (frame before/after every cut) in build/critic/")

    issues_md = "\n".join(f"- {x}" for x in issues) or "- none"
    (OUT / "report.md").write_text(f"# Critic report: {video}\n\n## Issues\n{issues_md}\n\n" + "\n\n".join(rep) + "\n")
    print((OUT / "report.md").read_text())


if __name__ == "__main__":
    main(sys.argv[1])
