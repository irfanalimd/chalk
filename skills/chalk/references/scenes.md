# Manim scenes

One scene per beat, Manim Community (0.22), no LaTeX. `scenes/style.py` (from the template) is the
house style and the timing API; scenes start with `from style import *`.

## Timing API

```python
class S3Conjecture(BeatScene):
    BEAT = "s3_conjecture"                      # must match a beat id in project.json

    def construct(self):
        c = self.cues                           # word times for this beat, seconds from scene start
        self.wait_to(c.at("every direction"))   # idle until the phrase starts
        self.play_until(c.after("thin"), FadeIn(x))  # animation ends as "thin" finishes
        self.play_from(c.at("Kakeya"), Write(t), run_time=1.2)
        self.drift(0.006)                       # slow continuous camera push-in
        ...
        self.finish()                           # pad to the exact beat length
```

`c.at(phrase, occurrence=1)`, `c.after(phrase)`, `c.voice_end`, `c.dur`. Phrases match normalised
words, so punctuation and case do not matter. A missing phrase raises, which catches script drift.

Budget time: every `play` advances the clock. If an animation before a cue runs long, everything after
it slips and the scene overruns its beat; `render_scenes.py` reports the length as `LEN`. Make
optional flourishes conditional on the time left (`room = c.at("turn it") - self.now`).

## House style

- Background `#0B0D12`, faint grid; the hero object (here the gold needle) keeps one colour all film.
- 3Blue1Brown palette: BLUE `#58C4DD`, TEAL `#5CD0B3`, GREEN `#83C167`, RED `#FC6255`, gold `#FFD45A`.
- Type: CMU Serif for display (`serif()`), Avenir Next for labels (`sans()`, `eyebrow()` for tracked
  small caps, `chip()` for pill labels). `credit()` for small source lines.
- `glow()` for soft bloom, `make_needle()` style hero objects with a distinguishable tip so rotations read.
- Motion: smooth easing, lagged reveals, one idea on screen at a time, a slow push-in where a scene
  would otherwise sit still. End each scene in a state the next one can start from (continuity), or
  fade to the background and set `"fade_in"` on the next beat.
- Recurring motifs (the dimension staircase in the example) go in their own module so several scenes
  share them; anchor any markers to members of the group so moving or scaling it keeps them in place.
- Keep 0.4 units of margin inside the *current* camera frame. When pushing in, fade edge elements first.
- Leave the bottom ~120 px calm where possible; captions are placed automatically but read best there.

## Gotchas

- No LaTeX: `MathTex`, `Tex`, `DecimalNumber`, `Integer`, `Variable`, `Matrix` fail. Use `Text`/`MarkupText`
  and rebuild numbers with `always_redraw` when they must animate. Formulas: `math_text()` with
  `<sub>`/`<sup>`/`<i>` markup; Unicode subscript characters (ₖ) render as empty boxes in CMU Serif.
- Pillow ≥ 11.3 breaks `ImageMobject` ("Invalid mode for data type"); pin `pillow<11.3`.
- Grayscale images: convert to RGB first (and tint with PIL), `set_color` on an L-mode image fails.
- Register fonts with `manimpango.register_font` (style.py does it for `assets/fonts/*.otf`).
- Heavy per-frame content (wave fields): precompute frames with numpy, cache in `build/`, and show via
  an `ImageMobject` whose pixels are swapped in an updater.
- Footage boxes: draw an empty framed box at `PIP` and `print("PIP", t0, t1)` when it is fully visible;
  assembly overlays the clip there (`project.json` overlays). The fade-in starts ~0.45 s before t0.
- Contact sheets put the timestamp bottom-right. If something looks clipped at the top-left, check a
  full-resolution frame before "fixing" it.

## Scene-builder brief (one per agent)

Give each agent: the beat id, file and class name; the exact narration of that beat; what the previous
scene ends on and what the next one starts with; a numbered visual plan tied to phrases; the palette
and helper names; the constraints (no LaTeX, don't edit shared files, real geometry/data only, finish
exactly at the beat); the render commands; and what to report (path, duration, what is on screen when,
any `PIP` window, known issues). Then review its contact sheet and send back concrete fixes.
