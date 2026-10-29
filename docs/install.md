# Installation

chalk runs on macOS and Linux. It has been used on macOS with Homebrew and on Ubuntu 26.04.

## 1. Install the plugin

In Claude Code:

```
/plugin marketplace add irfanalimd/chalk
/plugin install chalk@chalk
```

If you'd rather not use the plugin system, copy `skills/chalk` into `~/.claude/skills/` and
`agents/scene-builder.md` into `~/.claude/agents/`.

## 2. Install the system tools

chalk needs ffmpeg built with libass (for captions), cairo and pango (for Manim), `uv` (for Python),
and `yt-dlp` (only if you use video clips). LaTeX is not needed.

**macOS**

`setup.sh` installs everything through Homebrew the first time it runs, so you can skip to step 3.
If you want to do it yourself:

```
brew install ffmpeg-full uv yt-dlp pkg-config cairo pango
```

**Linux (Ubuntu or Debian)**

```
sudo apt install ffmpeg build-essential pkg-config libcairo2-dev libpango1.0-dev
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install yt-dlp
```

Ubuntu's ffmpeg already includes libass. If you use a different ffmpeg, point chalk at it with
`CHALK_FFMPEG=/path/to/ffmpeg`.

## 3. Set up a project

Each video lives in its own folder with its own Python environment. Claude does this for you when you
ask for a video, but you can also do it by hand:

From the plugin's `skills/chalk/scripts` folder:

```
python3 new_project.py ~/videos/my-topic     # add --long for a long video
bash setup.sh ~/videos/my-topic
```

`setup.sh` creates `.venv` with Python 3.12, installs Manim and the other packages, downloads the CMU
Serif fonts, and creates an empty `.env`.

## 4. Add your ElevenLabs key

Put your key in the project's `.env`:

```
ELEVENLABS_API_KEY=your-key
```

The key needs text-to-speech access. Generated music also needs the `music_generation` permission.
Without it, use library music instead (`music.py --library`, or just ask Claude for library music).

## Captions font on Linux

Captions default to Avenir Next from `/System/Library/Fonts`, which only exists on macOS. On Linux, put
a font file in the project's `assets/fonts/` and name it in `project.json`:

```json
"captions": { "font": "Inter", "fontsdir": "/home/you/videos/my-topic/assets/fonts" }
```

## Machines with little memory

Rendering at 1080p uses a lot of memory, and Claude may render several scenes at once. On a machine
with 8 GB of RAM or less, add some swap space or ask Claude to render one scene at a time.
