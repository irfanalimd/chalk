"""Shared helpers: project paths, project.json, the beat clock, ffmpeg discovery.

Every script runs from (or is pointed at) a project directory:
    project.json            beats, scenes, music, inserts, overlays
    script/narration.json   voice settings, narration per section, pauses
    build/                  everything generated
The project root is $CHALK_PROJECT if set, else the current directory.
"""
import json, os, shutil, subprocess
from pathlib import Path

ROOT = Path(os.environ.get("CHALK_PROJECT", Path.cwd())).resolve()
BUILD = ROOT / "build"


def load_project():
    return json.loads((ROOT / "project.json").read_text())


def load_narration():
    return json.loads((ROOT / "script/narration.json").read_text())


def beats():
    """Ordered beats with absolute times. Narrated beats take their length from build/timing.json
    (lead-in + voice + tail); silent beats use their fixed `dur`."""
    proj = load_project()
    tpath = BUILD / "timing.json"
    timing = json.loads(tpath.read_text()) if tpath.exists() else {"sections": {}, "lead_in": 0}
    t, out = 0.0, []
    for b in proj["beats"]:
        sec = timing["sections"].get(b["id"])
        if sec:
            d = {"id": b["id"], "start": t, "dur": sec["scene_dur"], "audio": sec["audio"],
                 "voice_start": t + timing["lead_in"], "voice_dur": sec["voice_dur"]}
        elif "dur" in b:
            d = {"id": b["id"], "start": t, "dur": b["dur"]}
        else:
            raise SystemExit(f"beat {b['id']!r} has no narration in build/timing.json and no fixed dur; run tts.py")
        d.update({k: v for k, v in b.items() if k not in d})
        out.append(d)
        t += d["dur"]
    return out


def _has_filters(ff, names):
    try:
        out = subprocess.run([ff, "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    except OSError:
        return False
    return all(f" {n} " in out for n in names)


def ffmpeg():
    """An ffmpeg with libass (captions) and drawtext. $CHALK_FFMPEG wins; Homebrew's ffmpeg-full is preferred."""
    for ff in (os.environ.get("CHALK_FFMPEG"), "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg",
               "/usr/local/opt/ffmpeg-full/bin/ffmpeg", shutil.which("ffmpeg")):
        if ff and Path(ff).exists() and _has_filters(ff, ["subtitles", "xfade", "loudnorm"]):
            return ff
    raise SystemExit("No ffmpeg with libass found. macOS: brew install ffmpeg-full (or set CHALK_FFMPEG).")


def media_dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).strip())


if __name__ == "__main__":
    for b in beats():
        print(f"{b['id']:<16} {b['start']:7.2f}  +{b['dur']:.2f}")
    print("total", round(sum(b["dur"] for b in beats()), 2))
