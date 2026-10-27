# Long mode: a guided reading of a whole paper (8–10 minutes)

Use when the request says "long", "deep dive", "full paper", "explain the entire paper", gives an
8–10 minute target, or sets `"mode": "long"` in `project.json`. The default mode is a 2–3 minute
"how big is this" piece; long mode teaches the paper's ideas in order.

## Shape

- ~1,350–1,500 narrated words (≈165 wpm at speed 0.97) plus chapter cards and pauses → 8.5–10 min.
- An opening (~30 s: what the paper is, why it matters, "let's read it together"), a title card, then
  7–9 chapters of 40–70 s, each preceded by a silent chapter card (2.6 s) and ending on a fade to
  background. Last chapter: what the paper predicted vs what happened.
- Follow the paper's own order: problem → core mechanism → its refinements → architecture → why it
  works (the paper's own argument or table) → training and results → legacy.
- One running example carried through several chapters (the Transformer video used the paper's own
  sentence "The Law will never be perfect, but its application should be just").

## Content rules

- Every formula, number and quoted sentence comes from the paper; check them against the extracted
  text (`research/<paper>.txt`) before the script is approved.
- Numbers are allowed where the argument needs them (model sizes, the headline results), still spelled
  out for the TTS, still at most one or two per sentence.
- Show the paper itself: title page, the key equation, the main figure and table, as crops with a
  small attribution. Check the paper's licence or permission statement (arXiv papers often carry one).
- Draw the main architecture/diagram yourself, built in step with the narration, then show the
  paper's version beside it for a moment.
- Math without LaTeX: `math_text('softmax(<i>QK</i><sup>T</sup> / √<i>d</i><sub>k</sub>) <i>V</i>')` (Pango
  markup). Never Unicode subscripts such as ₖ: CMU Serif draws them as empty boxes.

## Production

- `project.json`: `"mode": "long"`, a `chapters` map (`"ch3": "Scaled dot-product attention"`), and beats
  `cN` (narrated) interleaved with `chN` card beats (`"scene": "cards.py:ChN", "dur": 2.6`).
  `template/scenes/cards.py` builds the title, chapter cards (with a progress rail) and end card.
- Music: several library cues crossfaded at act boundaries (e.g. calm piano for the problem, a lighter
  piece for the mechanism chapters, something fuller for results), mixed lower (`gain_db` −11).
- Scenes: write `script/BRIEF.md` once (style, rules, page index of figures, per-section visual plan)
  and give each scene-builder agent its two sections plus "read BRIEF.md first". Five agents with two
  sections each finished a 9.5-minute video's scenes in parallel.
- Pauses: 0.4–0.7 s at each change of idea inside a chapter.
- Review: the critic writes ~16 contact sheets; read every one, and check each chapter boundary.

## Publishing

`web.py` makes a web encode (no grain, 1080p30, two-pass to a size cap), a poster frame, a WebVTT
caption file and a self-contained HTML page with chapter links. A static host such as GitHub Pages
caps single files at 100 MB, so keep `--max-mb` under that.
