"""Real-footage inserts: cut shots from downloaded sources, crop away burned-in subtitles and logos,
grade gently toward the house palette, and size them for their on-screen box.

    python clips.py               # build every insert in project.json "inserts"
    python clips.py <name>        # just one

project.json:
  "inserts": {
    "hongwang": {
      "credit": "Simons Foundation, “2026 Fields Medal: Hong Wang”",
      "box": {"center": [3.45, -0.35], "width": 6.4},          # manim units; 16:9 box (matches style.PIP)
      "shots": [["clips/source.mp4", 254.0, 257.7, "crop=iw*0.79:ih*0.79:iw*0.105:ih*0.035"],
                ["clips/source.mp4", 135.15, 138.95, "crop=iw*0.76:ih*0.76:iw*0.12:0"]]
    }
  }

Fetch sources first, e.g. `yt-dlp -f "bv*[height<=1080][ext=mp4]+ba[ext=m4a]" -o clips/source.mp4 <url>`.
Pick in/out points from a contact sheet (sheet.py) so no shot crosses a cut in the source, and make the
insert at least as long as its on-screen window (overlays) so it never freezes.
"""
import json, subprocess, sys

from common import ROOT, ffmpeg, load_project

PX_PER_UNIT = 1920 / (8 * 16 / 9)  # manim frame is 8 units tall at 16:9


def pip_rect(center=(3.45, -0.35), width=6.4):
    w = round(width * PX_PER_UNIT / 2) * 2
    h = round(w * 9 / 16 / 2) * 2
    x = round(960 + center[0] * PX_PER_UNIT - w / 2)
    y = round(540 - center[1] * PX_PER_UNIT - h / 2)
    return x, y, w, h


def build(name, spec):
    ff = ffmpeg()
    box = spec.get("box", {})
    x, y, w, h = pip_rect(tuple(box.get("center", (3.45, -0.35))), box.get("width", 6.4))
    parts = []
    for i, (src, a, b, *crop) in enumerate(spec["shots"]):
        p = ROOT / f"build/clips/{name}_{i}.mp4"
        p.parent.mkdir(parents=True, exist_ok=True)
        vf = (f"{crop[0] + ',' if crop else ''}scale={w}:{h}:flags=lanczos,fps=60,"
              "eq=saturation=0.88:contrast=1.03,format=yuv420p")
        subprocess.run([ff, "-v", "error", "-y", "-ss", str(a), "-to", str(b), "-i", str(ROOT / src),
                        "-vf", vf, "-an", "-c:v", "libx264", "-crf", "14", "-preset", "slow", str(p)], check=True)
        parts.append(p)
    out = ROOT / f"build/clips/{name}.mp4"
    lst = ROOT / f"build/clips/{name}.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run([ff, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)], check=True)
    meta = {"path": str(out.relative_to(ROOT)), "x": x, "y": y, "w": w, "h": h, "credit": spec.get("credit", "")}
    (ROOT / f"build/clips/{name}.json").write_text(json.dumps(meta, indent=1))
    return meta


if __name__ == "__main__":
    inserts = load_project().get("inserts", {})
    for n in (sys.argv[1:] or inserts):
        print(n, build(n, inserts[n]))
