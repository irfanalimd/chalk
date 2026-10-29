---
name: chalk
description: Produce a narrated, animated explainer video (Manim animation, ElevenLabs voice and music, real footage inserts, word-timed captions) about a research result, announcement, paper or technical idea, from source links to a finished 1080p60 MP4 and an optional web page. Two modes - short (2-3 min, "how big is this") and long (8-10 min guided reading of a whole paper, triggered by "long", "deep dive", "full paper" or an 8-10 minute target). Use when someone asks for an explainer video, a math/science/AI breakthrough video, a math-style animation with narration, or wants to turn a paper, blog post or announcement into a video.
---

# chalk

Turns a source (announcement, paper, blog post) into a 2–3 minute narrated explainer: Manim scenes on
one dark canvas, a calm professorial voice, a score that follows the story, a few seconds of real
footage, and word-timed captions. Everything runs on one clock so animation lands on spoken words.

Scripts live in `scripts/` next to this file (call them with the project's venv python from the project
directory, or set `CHALK_PROJECT`). Read the reference for a stage before doing that stage:

| Stage | Reference |
|---|---|
| research, questions, script, storyboard | `references/script.md` |
| voice, pauses, music | `references/audio.md` |
| Manim scenes, the timing API, scene-builder briefs | `references/scenes.md` |
| real footage and stills | `references/footage.md` |
| assembly, captions, critic, revisions | `references/finishing.md` |
| long mode (8–10 min, whole paper, chapters, web page) | `references/long.md` |

## Modes

| | short (default) | long |
|---|---|---|
| Trigger | default | "long", "deep dive", "full paper", "explain the entire paper", an 8–10 min target, or `"mode": "long"` |
| Length | 2–3 min, ~370 words | 8–10 min, ~1,350–1,500 words |
| Goal | how significant the result is | how the paper works, chapter by chapter |
| Structure | 6 sections, one title card | opening, title, 7–9 chapters each with a chapter card |
| Scaffold | `new_project.py <dir>` | `new_project.py <dir> --long` (adds `cards.py`) |
| Scenes | 1–4 scene-builder agents | write `script/BRIEF.md`, then ~5 agents with two sections each |
| Footage | one or two real clips | paper figures and tables (check the paper's permission line) |

## Workflow

1. **Read the sources first.** Fetch the link and its sublinks. If a page blocks automated fetching,
   say so and ask the user to paste it; do not try to get around the block. Prefer primary material
   (the paper, the repo, the release notes) over press coverage, and note anything the coverage gets wrong.
2. **Ask before writing** (one round, 3–4 questions, with a recommended default for each):
   one main result or several; how much caution to state about unverified claims; voice preference;
   what footage is acceptable (Creative Commons only, or short fair-use clips).
3. **Script and storyboard → checkpoint.** Write `script/script.md` (narration plus one visual line per
   section) and show the user the narration before generating any audio or rendering anything.
4. **Scaffold and set up.** `python scripts/new_project.py <dir>` then `bash scripts/setup.sh <dir>`.
   Put the API key in `<dir>/.env` (never in a script or command line). Fill `project.json` beats and
   `script/narration.json` sections from the approved script. The key is optional: without one, tell
   the user the narration will use the free local voice (Kokoro) and that an ElevenLabs key sounds more
   natural, then carry on; use library music (`music.py --library`) in that case.
5. **Voice.** `python scripts/tts.py` (ElevenLabs with a key, otherwise the local voice; for a male local
   voice set `"local_voice": "am_michael"` in `narration.json`). Check names with ASR (`asr.py`) before
   building on the audio.
6. **Scenes.** Write `scenes/style.py` adjustments first if the palette changes, then one Manim scene
   per beat. For more than two narrated scenes, brief one `scene-builder` agent per scene (or group)
   and run them in parallel; review every result on a contact sheet (`sheet.py`) and send fixes back.
   Render with `python scripts/render_scenes.py`; it fails any scene whose length is off its beat.
7. **Footage, music.** `clips.py` for inserts, `music.py` (or `music.py --library`).
8. **Assemble, caption, critique.** `assemble.py` → `captions.py build/master.mp4 build/final.mp4` →
   `critic.py build/final.mp4`. Read the report and look at the sheets yourself; fix and repeat until
   the report has no issues and nothing on the sheets is clipped, overlapping or empty for long.
9. **Deliver** `<Title>.mp4`, a no-captions master and the `.srt`. To publish on a website, run
   `web.py build/final.mp4 --slug <slug>` (compact encode under 100 MB, poster, HTML page with chapter
   links) and follow the site's own publishing instructions (e.g. its `llms.txt`). On every later revision, first copy
   the delivered files and sources into `versions/vN/`, then deliver under a new name (`_v2`, …).

## Rules that matter

- **Narration sounds like a university professor talking to a curious friend.** Flowing sentences of
  varied length. No clipped dramatic fragments ("It worked. Barely."), no rule-of-three lists, no stacks
  of statistics, no "Here's the thing", "Let that sink in", "game-changer". A year or a number appears
  only when it carries the story. Spell numbers as they should be spoken ("nineteen seventeen").
- **Length:** ~150 spoken words per minute at speed 0.97 plus pauses; 2:30 is about 370 words.
- **Purpose over completeness.** For a "how big is this" video the viewer should leave knowing what the
  problem is, why it was hard, who got close, and what was claimed. Skip the proof details.
- **Honesty.** State unverified claims as claims ("OpenAI announced that its models produced…"), and
  include one sober line about verification if the user wants caution. Put it in the narration over an
  ongoing visual, not on its own text slide.
- **Visual honesty.** Geometry, simulations, highlighted quotes and numbers on screen must be real
  (computed or copied from the source). If an honest number does not reach the narrated limit, show
  the limit as a note rather than faking the meter.
- **Sync by words, not seconds.** Scenes cue animations with `self.cues.at("phrase")`; never hand-type
  times. Pacing changes go through `narration.json` pauses, which shift every cue automatically.
- **Never regenerate an approved voice take for pacing.** Insert pauses instead; TTS is not repeatable.
- **Credits are small.** Source lines at 10–15 px equivalent, under the image or at the very bottom.
  The end card credits footage and music in one faint line.
- **Footage must show who the narration says it shows.** Confirm the identity of anyone on screen
  from the source's own description before using it, and tell the user who it is.
- **Privacy and secrets.** Keep keys in `.env` (mode 600). Do not put the user's email or other
  personal data in request headers or URLs (use a generic User-Agent). If the user pastes a key into
  chat, use it, and recommend rotating it afterwards.
