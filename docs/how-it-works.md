# How it works

Claude runs these steps for you. This page is for when you want to know what's happening, or to run a
step yourself.

## The pipeline

1. **Script.** Claude reads the source and its primary material (the paper, code, release notes), asks
   a few questions, and writes a script and storyboard for you to approve.
2. **Voice.** ElevenLabs reads the script and returns word timestamps. Pauses are added and stray sounds
   at the ends of takes are trimmed, without generating the speech again.
3. **Scenes.** Each section of the script gets its own Manim scene. Animations are tied to the words
   they go with, not to typed-in times, so they stay in sync if the narration changes. In long mode,
   several `scene-builder` agents can build scenes in parallel.
4. **Footage and music.** Real clips are cut into an on-screen box. Music is generated or picked from a
   library and crossfaded at the turns in the story.
5. **Assembly.** Everything is laid out as an OpenTimelineIO timeline and rendered with ffmpeg.
6. **Captions.** Speech recognition times the captions to what is actually heard, and spellings are
   corrected against the script. Captions move up when something on screen would be covered.
7. **Check.** An automated pass looks at format, loudness, black frames, freezes, transcript against
   script, and sync, and writes contact sheets for a final look.
8. **Web page** (optional). A simple page with the video, a poster image and, for long videos, chapter links.

## Running steps by hand

The scripts are in `skills/chalk/scripts/`. Run them from the project folder with the project's Python
(`.venv/bin/python`).

| Step | Command | Output |
|---|---|---|
| New project | `new_project.py ~/videos/<topic> [--long]` | project skeleton |
| Setup | `bash setup.sh ~/videos/<topic>` | `.venv`, fonts, `.env` |
| Voice | `tts.py` | `build/audio/*.wav`, `build/timing.json` |
| Scenes | `render_scenes.py [ids] [--preview]` | rendered scenes, length check per section |
| Footage | `clips.py` | `build/clips/<name>.mp4` |
| Music | `music.py` or `music.py --library` | `build/audio/score.mp3` |
| Assemble | `assemble.py [--draft]` | `build/master.mp4` |
| Captions | `captions.py build/master.mp4 build/final.mp4` | `build/final.mp4`, `build/captions.srt` |
| Check | `critic.py build/final.mp4` | `build/critic/report.md`, contact sheets |
| Web page | `web.py build/final.mp4 --slug <slug>` | `build/web/<slug>.html` and media |

`common.py` prints the plan of sections. `sheet.py <video> <out.png> [n]` makes a contact sheet.

## Project layout

```
project.json            sections, music, footage, caption font
script/script.md        narration and storyboard
script/narration.json   voice, voice settings, narration text, pauses
scenes/style.py         colours, type, and the timing helpers scenes use
scenes/*.py             one Manim scene per section
research/               sources
clips/, assets/         footage, images, fonts, music
build/                  everything generated
versions/vN/            delivered versions
```

## Limits

- Output is 16:9 only.
- Narration and captions are English.
- Scene code is written fresh for each video. chalk provides the style, timing and checks, not a
  library of ready-made scenes.
- Whether you can use a third-party clip is your call. chalk records where each one came from and
  credits it on screen.

## Troubleshooting

- **No ffmpeg with libass found.** Captions need an ffmpeg built with libass. Homebrew's `ffmpeg-full`
  and Ubuntu's `ffmpeg` both have it. To use a different build, set `CHALK_FFMPEG=/path/to/ffmpeg`.
- **Captions use the wrong font on Linux.** The default caption font is Avenir Next, which ships with
  macOS. Put a font file in the project's `assets/fonts/` and name it in `project.json`:
  `"captions": {"font": "Inter", "fontsdir": "<project>/assets/fonts"}`.
- **Renders run out of memory.** 1080p scenes are heavy, and several may render at once. On a machine
  with 8 GB of RAM or less, add swap or ask Claude to render one scene at a time.
- **Music generation fails with 401.** The ElevenLabs key lacks music generation. Ask for library music
  instead (`music.py --library`).
- **Using a key per project.** Instead of exporting `ELEVENLABS_API_KEY`, put it in the project's `.env`.
