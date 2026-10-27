# chalk

A Claude Code plugin that turns a source link (an announcement, a paper, a blog post) into a 2–3
minute narrated explainer in the style of 3Blue1Brown: Manim animation on a dark canvas, an ElevenLabs
voice, a score, a few seconds of real footage, and word-timed captions, rendered at 1920×1080, 60 fps.

It was built while making a video about OpenAI's October 2026 local smoothing / Kakeya result. That
project is included as `examples/needle-problem/`.

## What it does

1. Reads the source and its primary artifacts, asks a few questions, writes a script and storyboard,
   and waits for approval.
2. Synthesises the narration with word timestamps, then edits it (pauses, tail clean-up) without
   regenerating speech.
3. Builds one Manim scene per section. Animations are cued to spoken words, not to hand-typed times.
   Scenes can be built in parallel by `scene-builder` agents.
4. Cuts real footage into an on-screen box, generates or selects music, and assembles everything as
   an OpenTimelineIO timeline rendered with ffmpeg.
5. Burns in captions from speech recognition, corrected against the script, placed to avoid on-screen
   content.
6. Runs an automated check (format, loudness, black frames, freezes, transcript vs script, sync) and
   writes contact sheets for review.

## Requirements

- macOS with Homebrew (Linux works with an ffmpeg built with libass, plus cairo and pango)
- `ffmpeg-full`, `uv`, `yt-dlp` (installed by `setup.sh`)
- Python 3.12 venv per project with Manim CE, OpenTimelineIO, faster-whisper, PyMuPDF, shapely
  (installed by `setup.sh`; LaTeX is not needed)
- An ElevenLabs API key with text-to-speech access. Music generation needs the `music_generation`
  permission on the key; without it, use `music.py --library`.

## Install

```
/plugin marketplace add irfanalimd/chalk
/plugin install chalk@chalk
```

Or copy `skills/chalk` into `~/.claude/skills/` and `agents/scene-builder.md` into `~/.claude/agents/`.

## Example prompts

A full request:

```
Create a video explaining this announcement: <url>. Use the chalk skill. 3Blue1Brown style, for
people with a basic STEM degree rather than a maths background. 2 to 2.5 minutes. The goal is to
show how big and impressive the result is, not to explain every detail. Use my ElevenLabs key for
the voice and music. Ask me questions first if anything is unclear.
```

Shorter ones:

```
Make a chalk video about this paper: <arxiv url>. One main result, one sentence of caution about
verification, Creative Commons footage only.
```

```
Turn this blog post into a two-minute chalk explainer. Pick a calm narrator. Use library music.
```

```
Same pipeline as the needle video, but about <topic>. Reuse the style and the staircase motif.
```

Revision notes in the form that worked well:

```
Make the photo credit much smaller and put it under the picture, bottom right.
Add half a second of pause between topics.
Don't put the verification sentence on its own slide; say it over the next scene.
The audio cuts off abruptly before the title card; fix that part.
Save this as v2 and keep v1.
```

## System prompt

This is the brief the example was made from, rewritten as a reusable system prompt. Put it in a
project `CLAUDE.md` or pass it with the first request.

```
You are producing a short explainer video about a recent result in mathematics, science or AI.

Audience: people with a basic STEM degree, not specialists. They should come away understanding
what the problem is, why it was hard, who came close before, and what has now been claimed. The
goal is to convey how significant the result is, not to teach every detail.

Length: 2 to 2.5 minutes.

Style: 3Blue1Brown. A dark canvas, precise animated geometry, calm motion, CMU Serif for display
type. Production quality should feel expensive: clean typography, consistent colour, deliberate
camera moves, nothing cluttered or clipped.

Narration: speak like a university professor explaining something to a curious friend. Use flowing
sentences of varied length. Do not use short punchy fragments for drama, rhetorical triplets, or
lists of numbers. Mention a year or a figure only when it carries the story.

Sources: read the link and its sublinks, and prefer primary material (paper, code, release notes).
If a page cannot be fetched, say so and ask for the text. You may show screenshots of the paper or
of the problem as originally posed.

Honesty: present unverified results as claims. Include one sentence noting that the community is
still verifying the work. Everything shown as data, geometry or a quote must be real.

Footage: a small number of short clips where they add a real person or document. Confirm who is on
screen. Credit sources in small type.

Process: ask a few questions before writing if the intent is unclear. Show the narration for
approval before rendering. Keep earlier versions when revising.
```

## Pipeline

All scripts are in `skills/chalk/scripts/` and run from the project directory with the project's
venv python.

| Step | Command | Output |
|---|---|---|
| Scaffold | `python new_project.py ~/videos/<topic>` | project skeleton |
| Setup | `bash setup.sh ~/videos/<topic>` | `.venv`, fonts, `.env` |
| Voice | `python tts.py` | `build/audio/*.wav`, `build/timing.json` |
| Scenes | `python render_scenes.py [ids] [--preview]` | `build/manim/...`, length check per beat |
| Footage | `python clips.py` | `build/clips/<name>.mp4` |
| Music | `python music.py` or `python music.py --library` | `build/audio/score.mp3` |
| Assemble | `python assemble.py [--draft]` | `build/edit.otio`, `build/master.mp4` |
| Captions | `python captions.py build/master.mp4 build/final.mp4` | `build/final.mp4`, `build/captions.srt` |
| Check | `python critic.py build/final.mp4` | `build/critic/report.md`, contact sheets |

`common.py` prints the beat plan. `sheet.py <video> <out.png> [n]` makes a contact sheet.

## Project layout

```
project.json            beats (id, scene file:class, fixed dur for silent cards, fade_in),
                        music settings, footage inserts, overlay windows, caption font
script/script.md        narration and storyboard
script/narration.json   voice, settings, sections (one per narrated beat), pauses
scenes/style.py         palette, type helpers, glow, the Cues timing API
scenes/*.py             one Manim scene per beat
research/               sources
clips/, assets/         downloaded footage, images, fonts, music
build/                  everything generated
versions/vN/            delivered versions with their sources
```

## Limits

- 16:9 only. Vertical output would need a second frame configuration.
- Narration is English; caption alignment uses `small.en`.
- Scene code is written per video. The skill provides the style, timing and checks, not a library of
  ready-made scenes (apart from what the example shows).
- Fair use of third-party clips is the user's call; the skill records sources and credits them.

## Example

`examples/needle-problem/` holds the script, narration settings, `project.json` and all Manim scenes
for "The Needle Problem" (2:43). Media and research files are not committed; `assets.md` lists their
sources.
