#!/usr/bin/env bash
# One-time machine setup, then per-project venv. Usage: setup.sh <project-dir>
# macOS + Homebrew assumed for system packages; on Linux install the equivalents
# (ffmpeg built with libass, cairo, pango, pkg-config) and skip the brew line.
set -euo pipefail
PROJECT="${1:?usage: setup.sh <project-dir>}"

if command -v brew >/dev/null; then
  brew list ffmpeg-full >/dev/null 2>&1 || brew install ffmpeg-full
  for p in uv yt-dlp pkg-config cairo pango; do brew list "$p" >/dev/null 2>&1 || brew install "$p"; done
fi

cd "$PROJECT"
[ -d .venv ] || uv venv --python 3.12 .venv
# Pillow < 11.3: newer Pillow breaks Manim CE 0.22's ImageMobject rendering.
uv pip install --python .venv/bin/python manim opentimelineio faster-whisper requests python-dotenv \
  pymupdf shapely "pillow<11.3"

# CMU Serif (the Computer Modern face 3Blue1Brown uses). Manim's Text needs no LaTeX with this.
mkdir -p assets/fonts
for f in cmunrm cmunti cmunbx cmunrb cmunbi; do
  [ -f "assets/fonts/$f.otf" ] || curl -sfL -o "assets/fonts/$f.otf" "https://mirrors.ctan.org/fonts/cm-unicode/fonts/otf/$f.otf"
done

[ -f .env ] || { cp .env.example .env 2>/dev/null || printf 'ELEVENLABS_API_KEY=\n' > .env; }
chmod 600 .env
echo "ready: $PROJECT  (put the ElevenLabs key in .env)"
