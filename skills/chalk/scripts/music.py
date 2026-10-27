"""Score: build/audio/score.mp3, cut to the beat plan.

    python music.py             # ElevenLabs music, one composition whose sections match the beats
    python music.py --library   # licensed tracks from project.json music.library, crossfaded at story turns

project.json:
  "music": {
    "global":   ["cinematic underscore", "felt piano", ...],     # ElevenLabs global styles
    "negative": ["vocals", "drum kit", ...],
    "moods":    {"<beat id>": ["solo felt piano", ...], ...},    # per-beat local styles
    "gain_db":  -9,                                              # used by assemble.py
    "library":  {"level_lufs": -20, "xfade": 2.5,
                 "cues": [{"file": "assets/music/a.mp3", "in": 0},
                          {"file": "assets/music/b.mp3", "in": 0, "at_beat": "s5_result"}]}
  }

ElevenLabs needs the key's `music_generation` permission (paid plans). Sections must be >= 3 s, so a
short beat is folded into the start of the next section.
"""
import os, subprocess, sys

import requests
from dotenv import load_dotenv

from common import ROOT, beats, ffmpeg, load_project

load_dotenv(ROOT / ".env")
OUT = ROOT / "build/audio/score.mp3"


def elevenlabs(cfg):
    sections, carry = [], None
    for b in beats():
        sec = {"section_name": b["id"], "positive_local_styles": list(cfg.get("moods", {}).get(b["id"], [])),
               "negative_local_styles": [], "duration_ms": int(round(b["dur"] * 1000)), "lines": []}
        if carry:
            sec["section_name"] = carry["section_name"] + "+" + sec["section_name"]
            if carry["positive_local_styles"]:
                sec["positive_local_styles"].insert(0, "opens with " + ", ".join(carry["positive_local_styles"]))
            sec["duration_ms"] += carry["duration_ms"]
            carry = None
        if sec["duration_ms"] < 3000:
            carry = sec
            continue
        sections.append(sec)
    if carry:
        sections[-1]["duration_ms"] += carry["duration_ms"]
    body = {"composition_plan": {"positive_global_styles": cfg.get("global", []),
                                 "negative_global_styles": cfg.get("negative", []), "sections": sections},
            "model_id": "music_v1", "respect_sections_durations": True}
    r = requests.post("https://api.elevenlabs.io/v1/music", headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"]},
                      params={"output_format": "mp3_44100_128"}, json=body, timeout=600)
    if r.status_code != 200:
        hint = "  (enable Music Generation on the API key, or run with --library)" if r.status_code == 401 else ""
        raise SystemExit(f"music failed {r.status_code}: {r.text[:300]}{hint}")
    OUT.write_bytes(r.content)


def library(cfg):
    lib = cfg["library"]
    cues, xf, level = lib["cues"], lib.get("xfade", 2.5), lib.get("level_lufs", -20)
    bs = {b["id"]: b for b in beats()}
    total = sum(b["dur"] for b in bs.values())
    starts = [0.0] + [bs[c["at_beat"]]["start"] for c in cues[1:]]
    ff = ffmpeg()
    args, filt = [ff, "-v", "error", "-y"], []
    for i, c in enumerate(cues):
        end = starts[i + 1] + xf * 0.6 if i + 1 < len(cues) else total + 1
        length = end - starts[i] + (xf * 0.4 if i else 0)
        args += ["-ss", str(c.get("in", 0)), "-t", f"{length:.3f}", "-i", str(ROOT / c["file"])]
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I={level}:TP=-2:LRA=9,aresample=48000[m{i}]")
    cur = "m0"
    for i in range(1, len(cues)):
        filt.append(f"[{cur}][m{i}]acrossfade=d={xf}:c1=tri:c2=tri[x{i}]")
        cur = f"x{i}"
    subprocess.run(args + ["-filter_complex", ";".join(filt), "-map", f"[{cur}]", "-t", f"{total + 0.5:.3f}",
                           "-c:a", "libmp3lame", "-b:a", "256k", str(OUT)], check=True)


if __name__ == "__main__":
    cfg = load_project().get("music", {})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    library(cfg) if "--library" in sys.argv else elevenlabs(cfg)
    print("wrote", OUT)
