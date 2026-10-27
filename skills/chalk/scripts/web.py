"""Web package: a compact encode, a poster frame and a self-contained HTML page with chapter links.

    python web.py build/final.mp4 --slug attention-is-all-you-need [--max-mb 95] [--poster 34.0]
                  [--description "..."] [--media-dir media]

Writes build/web/<slug>.html and build/web/<media-dir>/<slug>.mp4 + .jpg. The page references the
media by relative path, so copy both into the site keeping that layout (e.g. p/learning/<slug>.html and
p/learning/media/<slug>.mp4). The encode removes the film grain (it costs bitrate and nothing at web
sizes), drops to 30 fps and uses two-pass x264 sized to stay under --max-mb (GitHub Pages rejects
files over 100 MB).
"""
import argparse, html, json, subprocess

from common import ROOT, beats, ffmpeg, load_project, media_dur


def encode(src, out, max_mb, ff):
    dur = media_dur(src)
    audio_k = 128
    video_k = int(max_mb * 8192 / dur * 0.96) - audio_k
    vf = "hqdn3d=3:2:5:4,scale=1920:1080:flags=lanczos,fps=30,format=yuv420p"
    common = ["-vf", vf, "-c:v", "libx264", "-preset", "slow", "-b:v", f"{video_k}k",
              "-maxrate", f"{int(video_k * 1.8)}k", "-bufsize", f"{video_k * 4}k", "-profile:v", "high"]
    log = str(out.with_suffix(""))
    subprocess.run([ff, "-v", "error", "-y", "-i", str(src), *common, "-pass", "1", "-passlogfile", log,
                    "-an", "-f", "mp4", "/dev/null"], check=True)
    subprocess.run([ff, "-v", "error", "-y", "-i", str(src), *common, "-pass", "2", "-passlogfile", log,
                    "-c:a", "aac", "-b:a", f"{audio_k}k", "-movflags", "+faststart", str(out)], check=True)
    for p in out.parent.glob(out.stem + "*.log*"):
        p.unlink()
    return out.stat().st_size / 1e6


def chapters():
    proj = load_project()
    names = proj.get("chapters", {})
    out = [(0.0, "Opening")]
    for b in beats():
        if b["id"] in names:
            out.append((b["start"], names[b["id"]]))
    return out


def page(slug, media, title, description, chaps, source):
    items = "\n".join(
        f'      <li><button data-t="{t:.2f}"><span class="t">{int(t // 60)}:{int(t % 60):02d}</span>'
        f"{html.escape(n)}</button></li>" for t, n in chaps)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="{media}/{slug}.jpg">
<style>
  :root {{ --bg:#f6f5f2; --fg:#16181d; --muted:#6b6f78; --rule:#dcdad4; --accent:#b8860b; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#0b0d12; --fg:#ece8e1; --muted:#8a8f98; --rule:#23272f; --accent:#ffd45a; }} }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--fg);
         font:16px/1.55 -apple-system, BlinkMacSystemFont, "Avenir Next", "Segoe UI", sans-serif; }}
  main {{ max-width:1040px; margin:0 auto; padding:40px 16px 64px; }}
  h1 {{ font:400 clamp(28px,4.5vw,44px)/1.15 "Iowan Old Style", "Palatino", Georgia, serif; margin:0 0 8px; }}
  .lede {{ color:var(--muted); margin:0 0 24px; max-width:68ch; }}
  video {{ width:100%; aspect-ratio:16/9; background:#000; border-radius:10px; display:block; }}
  h2 {{ font-size:13px; letter-spacing:.12em; text-transform:uppercase; color:var(--muted); margin:28px 0 8px; font-weight:600; }}
  ol {{ list-style:none; padding:0; margin:0; display:grid; grid-template-columns:repeat(auto-fill,minmax(250px,1fr)); gap:2px 24px; }}
  button {{ all:unset; cursor:pointer; display:flex; gap:12px; padding:6px 0; border-bottom:1px solid var(--rule); width:100%; }}
  button:hover {{ color:var(--accent); }}
  .t {{ font-variant-numeric:tabular-nums; color:var(--muted); min-width:3.2em; }}
  footer {{ margin-top:32px; color:var(--muted); font-size:13px; }}
  a {{ color:inherit; }}
</style>
</head>
<body>
<main>
  <h1>{html.escape(title)}</h1>
  <p class="lede">{html.escape(description)}</p>
  <video id="v" controls preload="metadata" playsinline poster="{media}/{slug}.jpg">
    <source src="{media}/{slug}.mp4" type="video/mp4">
  </video>
  <h2>Chapters</h2>
  <ol>
{items}
  </ol>
  <footer>{source}</footer>
</main>
<script>
  const v = document.getElementById("v");
  document.querySelectorAll("button[data-t]").forEach(b =>
    b.addEventListener("click", () => {{ v.currentTime = +b.dataset.t; v.play(); window.scrollTo({{top: v.offsetTop - 16, behavior: "smooth"}}); }}));
</script>
</body>
</html>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--max-mb", type=float, default=95)
    ap.add_argument("--poster", type=float, default=None, help="seconds; default: start of the title beat")
    ap.add_argument("--description", default="")
    ap.add_argument("--media-dir", default="media")
    a = ap.parse_args()
    proj, ff = load_project(), ffmpeg()
    out_dir = ROOT / "build/web"
    (out_dir / a.media_dir).mkdir(parents=True, exist_ok=True)
    mp4 = out_dir / a.media_dir / f"{a.slug}.mp4"
    mb = encode(ROOT / a.src, mp4, a.max_mb, ff)
    t = a.poster if a.poster is not None else next((b["start"] + 1.6 for b in beats() if b["id"] == "title"), 2.0)
    subprocess.run([ff, "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1", "-q:v", "3",
                    str(out_dir / a.media_dir / f"{a.slug}.jpg")], check=True)
    source = html.escape(proj.get("source", "")) + (" · " + html.escape(proj["credits"]) if proj.get("credits") else "")
    (out_dir / f"{a.slug}.html").write_text(page(a.slug, a.media_dir, proj["title"], a.description, chapters(), source))
    print(f"{mp4.relative_to(ROOT)}  {mb:.1f} MB\n{(out_dir / (a.slug + '.html')).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
