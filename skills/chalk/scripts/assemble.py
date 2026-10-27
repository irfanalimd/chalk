"""Assembly: build the edit as an OpenTimelineIO timeline, then render it with ffmpeg.

    python assemble.py            # build/edit.otio  +  build/master.mp4 (clean, no captions)
    python assemble.py --draft    # quick 720p30 render for review (falls back to preview renders)

Tracks
  V1  scenes        one Manim render per beat, trimmed/padded to the beat length
  V2  inserts       real footage composited into its on-screen box (metadata: x, y, w, h)
  A1  narration     one clip per section at its voice start
  A2  score         ElevenLabs music under everything, side-chain ducked under the voice

The .otio file is the source of truth for the render and also opens in Resolve/Premiere for hand edits.
"""
import json, subprocess, sys
from pathlib import Path

import opentimelineio as otio

from common import ROOT, beats, ffmpeg, load_project, media_dur

FFMPEG = ffmpeg()
RATE = 60
PROJECT = load_project()
SCENES = {b["id"]: (Path(b["scene"].split(":")[0]).stem, b["scene"].split(":")[1])
          for b in PROJECT["beats"]}  # beat id -> (manim file stem, scene class); "scene": "s1_intro.py:S1Intro"
OVERLAYS = PROJECT.get("overlays", [])
MUSIC_GAIN_DB = PROJECT.get("music", {}).get("gain_db", -9.0)
BG_HEX = PROJECT.get("bg", "#0B0D12").lstrip("#")


def rt(sec):
    return otio.opentime.RationalTime(round(sec * RATE), RATE)


def rng(start, dur):
    return otio.opentime.TimeRange(rt(start), rt(dur))


def scene_path(bid):
    """Best available render: full quality, else (draft only) a preview render."""
    stem, cls = SCENES[bid]
    for q in ("1080p60",) + (("720p30", "480p15") if "--draft" in sys.argv else ()):
        p = ROOT / f"build/manim/videos/{stem}/{q}/{cls}.mp4"
        if p.exists():
            return p
    return ROOT / f"build/manim/videos/{stem}/1080p60/{cls}.mp4"


def build_timeline():
    bs = beats()
    by_id = {b["id"]: b for b in bs}
    total = sum(b["dur"] for b in bs)
    tl = otio.schema.Timeline(name="The Needle Problem", global_start_time=rt(0))

    v1 = otio.schema.Track(name="V1 scenes", kind=otio.schema.TrackKind.Video)
    for b in bs:
        p = scene_path(b["id"])
        c = otio.schema.Clip(name=b["id"], media_reference=otio.schema.ExternalReference(target_url=str(p)),
                             source_range=rng(0, b["dur"]))
        if b.get("fade_in"):  # soft dip-from-background, e.g. after a card that faded out
            c.metadata["fade_in"] = b["fade_in"]
        v1.append(c)

    v2 = otio.schema.Track(name="V2 inserts", kind=otio.schema.TrackKind.Video)
    cursor = 0.0
    for o in sorted(OVERLAYS, key=lambda o: by_id[o["beat"]]["start"] + o["start"]):
        meta = json.loads((ROOT / f"build/clips/{o['insert']}.json").read_text())
        t0 = by_id[o["beat"]]["start"] + o["start"]
        dur = o["end"] - o["start"]
        if t0 > cursor:
            v2.append(otio.schema.Gap(source_range=rng(0, t0 - cursor)))
        clip = otio.schema.Clip(name=o["insert"], media_reference=otio.schema.ExternalReference(target_url=str(ROOT / meta["path"])),
                                source_range=rng(0, dur))
        clip.metadata["overlay"] = {k: meta[k] for k in ("x", "y", "w", "h")} | {"fade": o.get("fade", 0.35), "radius": o.get("radius", 11)}
        clip.metadata["credit"] = meta["credit"]
        v2.append(clip)
        cursor = t0 + dur

    a1 = otio.schema.Track(name="A1 narration", kind=otio.schema.TrackKind.Audio)
    cursor = 0.0
    for b in bs:
        if "audio" not in b:
            continue
        if b["voice_start"] > cursor:
            a1.append(otio.schema.Gap(source_range=rng(0, b["voice_start"] - cursor)))
        a1.append(otio.schema.Clip(name=b["id"], media_reference=otio.schema.ExternalReference(target_url=str(ROOT / b["audio"])),
                                   source_range=rng(0, b["voice_dur"])))
        cursor = b["voice_start"] + b["voice_dur"]

    a2 = otio.schema.Track(name="A2 score", kind=otio.schema.TrackKind.Audio)
    score = ROOT / "build/audio/score.mp3"
    if score.exists():
        c = otio.schema.Clip(name="score", media_reference=otio.schema.ExternalReference(target_url=str(score)),
                             source_range=rng(0, min(total, media_dur(score))))
        c.metadata["gain_db"] = MUSIC_GAIN_DB
        c.metadata["duck_under"] = "A1 narration"
        a2.append(c)

    tl.tracks.extend([v1, v2, a1, a2])
    otio.adapters.write_to_file(tl, str(ROOT / "build/edit.otio"))
    return tl


def _items(track):
    """(item, absolute start seconds) for clips on a track, skipping gaps."""
    t = 0.0
    for it in track:
        d = it.source_range.duration.to_seconds()
        if isinstance(it, otio.schema.Clip):
            yield it, t
        t += d


def render(tl, out, draft=False):
    v1, v2, a1, a2 = tl.tracks
    total = v1.duration().to_seconds()
    W, H, FPS = (1280, 720, 30) if draft else (1920, 1080, RATE)
    args, filt, n = [FFMPEG, "-v", "error", "-stats", "-y"], [], 0

    # V1: trim/pad each scene to its exact beat length, then concatenate.
    vlabels = []
    for clip, _ in _items(v1):
        d = clip.source_range.duration.to_seconds()
        args += ["-i", clip.media_reference.target_url]
        fade = clip.metadata.get("fade_in", 0)
        fade_f = f",fade=t=in:st=0:d={fade}:color=0x{BG_HEX}" if fade else ""
        filt.append(f"[{n}:v]fps={FPS},scale={W}:{H}:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=2,"
                    f"trim=0:{d:.4f},setpts=PTS-STARTPTS{fade_f}[v{n}]")
        vlabels.append(f"[v{n}]")
        n += 1
    filt.append(f"{''.join(vlabels)}concat=n={len(vlabels)}:v=1:a=0[base]")
    cur = "base"

    # V2: inserts with rounded corners and alpha fades.
    sx = W / 1920
    for clip, t0 in _items(v2):
        o = clip.metadata["overlay"]
        d = clip.source_range.duration.to_seconds()
        w, h, x, y = (round(o[k] * sx / 2) * 2 if k in "wh" else round(o[k] * sx) for k in ("w", "h", "x", "y"))
        r, f = max(2, round(o["radius"] * sx)), o["fade"]
        args += ["-i", clip.media_reference.target_url]
        mask = (f"geq=lum='255*lte(hypot(max(0\\,max({r}-X\\,X-(W-1-{r})))\\,max(0\\,max({r}-Y\\,Y-(H-1-{r}))))\\,{r})'")
        filt.append(f"[{n}:v]fps={FPS},scale={w}:{h},setsar=1,tpad=stop_mode=clone:stop_duration=3,trim=0:{d:.4f},format=yuva420p,"
                    f"split[ic{n}][im{n}];[im{n}]format=gray,{mask}[mk{n}];[ic{n}][mk{n}]alphamerge,"
                    f"fade=t=in:st=0:d={f}:alpha=1,fade=t=out:st={d - f:.4f}:d={f}:alpha=1,"
                    f"setpts=PTS-STARTPTS+{t0:.4f}/TB[ov{n}]")
        filt.append(f"[{cur}][ov{n}]overlay=x={x}:y={y}:eof_action=pass:enable='between(t,{t0:.4f},{t0 + d:.4f})'[c{n}]")
        cur, n = f"c{n}", n + 1

    # Finishing: gentle vignette and fine luma grain (also breaks up banding on dark gradients).
    filt.append(f"[{cur}]vignette=angle=0.32:mode=forward,noise=c0s=3:c0f=t,format=yuv420p[vout]")

    # A1: narration placed at absolute times.
    alabels = []
    for clip, t0 in _items(a1):
        args += ["-i", clip.media_reference.target_url]
        ms = round(t0 * 1000)
        filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[a{n}]")
        alabels.append(f"[a{n}]")
        n += 1
    filt.append(f"{''.join(alabels)}amix=inputs={len(alabels)}:normalize=0,apad=whole_dur={total:.3f},asplit=2[vox][key]")

    # A2: score, ducked under the voice.
    music = list(_items(a2))
    if music:
        clip, _ = music[0]
        args += ["-i", clip.media_reference.target_url]
        g = clip.metadata.get("gain_db", MUSIC_GAIN_DB)
        filt.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}dB,apad=whole_dur={total:.3f},"
                    f"afade=t=out:st={total - 3:.3f}:d=3[mus]")
        filt.append("[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=60:release=700:makeup=1[duck]")
        filt.append("[vox][duck]amix=inputs=2:normalize=0[aout]")
        n += 1
    else:
        filt.append("[key]anullsink;[vox]anull[aout]")

    graph = ROOT / "build/filtergraph.txt"
    graph.write_text(";\n".join(filt))
    mix = ROOT / "build/audio/mix.wav"
    # Pass 1: picture + raw mix.
    args += ["-/filter_complex", str(graph), "-map", "[vout]", "-map", "[aout]", "-t", f"{total:.3f}",
             "-c:v", "libx264", "-preset", "veryfast" if draft else "slow", "-crf", "22" if draft else "16",
             "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "pcm_s16le", str(out.with_suffix(".tmp.mov"))]
    subprocess.run(args, check=True)
    # Pass 2: two-pass loudness normalisation to -14 LUFS / -1.5 dBTP, then mux with AAC.
    tmp = out.with_suffix(".tmp.mov")
    stats = subprocess.run([FFMPEG, "-hide_banner", "-i", str(tmp), "-vn", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(stats[stats.rindex("{"):stats.rindex("}") + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(tmp), "-map", "0:v", "-map", "0:a", "-c:v", "copy",
                    "-af", f"{ln},aresample=48000", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)], check=True)
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(tmp), "-vn", "-af", f"{ln},aresample=48000", str(mix)], check=True)
    tmp.unlink()
    return out


if __name__ == "__main__":
    draft = "--draft" in sys.argv
    tl = build_timeline()
    missing = [c.media_reference.target_url for t in tl.tracks for c, _ in _items(t) if not Path(c.media_reference.target_url).exists()]
    if missing:
        sys.exit("missing media:\n  " + "\n  ".join(missing))
    out = render(tl, ROOT / ("build/draft.mp4" if draft else "build/master.mp4"), draft=draft)
    print("wrote", out)
