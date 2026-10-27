"""Render Manim scenes in parallel and check each against its beat length.

    python render_scenes.py                 # every beat in project.json, 1080p60
    python render_scenes.py s1_intro s3_x   # only these beats
    python render_scenes.py --preview ...   # 480p15 for quick checks

A scene that runs long gets its tail cut by assembly, and a short one gets its last frame held, so any
mismatch over one frame is reported as a failure. Lines a scene prints that start with "PIP" (on-screen
footage windows) are echoed so they can be copied into project.json overlays.
"""
import os, shutil, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from common import ROOT, beats, media_dur


def manim_bin():
    for m in (os.environ.get("CHALK_MANIM"), ROOT / ".venv/bin/manim", shutil.which("manim")):
        if m and Path(m).exists():
            return str(m)
    raise SystemExit("manim not found (set CHALK_MANIM or create .venv with manim)")


def render(b, preview):
    file, cls = b["scene"].split(":")
    log = ROOT / f"build/logs/{b['id']}.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    cmd = [manim_bin(), "--config_file", str(ROOT / "manim.cfg")] + (["-ql"] if preview else []) + [file, cls]
    with open(log, "w") as fh:
        rc = subprocess.run(cmd, cwd=ROOT / "scenes", stdout=fh, stderr=subprocess.STDOUT).returncode
    q = "480p15" if preview else "1080p60"
    out = ROOT / f"build/manim/videos/{Path(file).stem}/{q}/{cls}.mp4"
    return b, rc, out, log


def main():
    preview = "--preview" in sys.argv
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = [b for b in beats() if not ids or b["id"] in ids]
    bad = 0
    with ThreadPoolExecutor(max_workers=min(8, len(todo))) as ex:
        for b, rc, out, log in ex.map(lambda b: render(b, preview), todo):
            text = log.read_text()
            if rc or "Traceback" in text or not out.exists():
                print(f"FAIL  {b['id']:<16} see {log.relative_to(ROOT)}")
                bad += 1
                continue
            d = media_dur(out)
            fps = 15 if preview else 60
            ok = abs(d - b["dur"]) <= 1.5 / fps
            bad += not ok
            print(f"{'ok ' if ok else 'LEN'}   {b['id']:<16} {d:7.3f}s  (beat {b['dur']:.3f}s)")
            for line in text.splitlines():
                if line.startswith("PIP"):
                    print(f"      {b['id']}: {line}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
