"""Contact sheet: evenly spaced (or given) frames from a video, tiled with timestamps."""
import subprocess, sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)]))


def frame(video, t, width=480):
    png = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1",
                                   "-vf", f"scale={width}:-2", "-f", "image2pipe", "-vcodec", "png", "-"])
    return Image.open(BytesIO(png)).convert("RGB")


def sheet(video, out, n=12, cols=4, times=None, width=480):
    times = times or [dur(video) * (i + 0.5) / n for i in range(n)]
    frames = [frame(video, t, width) for t in times]
    w, h = frames[0].size
    rows = -(-len(frames) // cols)
    canvas = Image.new("RGB", (cols * (w + 4), rows * (h + 4)), (90, 90, 90))
    for i, (t, f) in enumerate(zip(times, frames)):
        d = ImageDraw.Draw(f)
        d.rectangle([w - 66, h - 22, w, h], fill=(0, 0, 0))
        d.text((w - 60, h - 18), f"{t:.1f}s", fill=(255, 255, 255))
        canvas.paste(f, ((i % cols) * (w + 4), (i // cols) * (h + 4)))
    canvas.save(out)
    return out


if __name__ == "__main__":
    v, o = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    print(sheet(v, o, n=n))
