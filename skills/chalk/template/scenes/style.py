"""House style shared by every scene: palette, type, glow, and narration-locked timing.

Timing model: each scene is one beat in project.json. `Cues(beat_id)` reads word times from
build/timing.json (already offset by the lead-in), so scene code says *what word* an animation lands
on, never a hand-typed second:

    c = self.cues
    self.play_until(c.at("needle"), GrowFromCenter(needle))   # anim ends as "needle" is spoken
    self.wait_to(c.at("smallest region"))
    ...
    self.finish()                                               # pad to the exact beat length
"""
import json, re
from pathlib import Path

import manimpango
import numpy as np
from manim import *

ROOT = Path(__file__).resolve().parents[1]  # project root (scenes/ lives inside it)

for f in (ROOT / "assets/fonts").glob("*.otf"):
    manimpango.register_font(str(f))

# ── palette (3Blue1Brown-derived, slightly warmer) ─────────────────────────────
BG = "#0B0D12"
INK = "#ECE8E1"        # primary text
MUTED = "#8A8F98"      # secondary text
FAINT = "#2A2F3A"      # grid / rules
NEEDLE = "#FFD45A"     # the needle: warm gold
BLUE = "#58C4DD"
TEAL = "#5CD0B3"
GREEN = "#83C167"
RED = "#FC6255"
PURPLE = "#A884D8"
ORANGE = "#F0AC5F"

SERIF = "CMU Serif"
SANS = "Avenir Next"

config.background_color = BG

# Where the real-footage card sits (manim units); assembly overlays the clip into this box.
PIP = {"center": (3.45, -0.35), "width": 6.4}  # 16:9 box, height = width * 9/16


def beats():
    """Beat clock, same rule as the pipeline: narrated beats = lead-in + voice + tail, silent beats = fixed dur."""
    proj = json.loads((ROOT / "project.json").read_text())
    tp = ROOT / "build/timing.json"
    timing = json.loads(tp.read_text()) if tp.exists() else {"sections": {}}
    t, out = 0.0, []
    for b in proj["beats"]:
        sec = timing["sections"].get(b["id"])
        dur = sec["scene_dur"] if sec else b["dur"]
        out.append({**b, "start": t, "dur": dur})
        t += dur
    return out


def beat(beat_id):
    return next(b for b in beats() if b["id"] == beat_id)


class Cues:
    """Word-timed cue points for one narrated beat, in seconds from scene start."""

    def __init__(self, beat_id):
        self.beat = beat(beat_id)
        self.dur = self.beat["dur"]
        timing = json.loads((ROOT / "build/timing.json").read_text())
        sec = timing["sections"].get(beat_id)
        self.lead = timing["lead_in"]
        self.words = sec["words"] if sec else []
        self.keys = [w["key"] for w in self.words]

    def _find(self, phrase, occurrence):
        target = [re.sub(r"[^\w']", "", p.lower()) for p in phrase.split()]
        hits = [i for i in range(len(self.keys) - len(target) + 1) if self.keys[i:i + len(target)] == target]
        if len(hits) < occurrence:
            raise KeyError(f"cue {phrase!r} (#{occurrence}) not in narration")
        return hits[occurrence - 1], len(target)

    def at(self, phrase, occurrence=1):
        """Start time of the phrase."""
        i, _ = self._find(phrase, occurrence)
        return self.lead + self.words[i]["start"]

    def after(self, phrase, occurrence=1):
        """End time of the phrase."""
        i, n = self._find(phrase, occurrence)
        return self.lead + self.words[i + n - 1]["end"]

    @property
    def voice_end(self):
        return self.lead + (self.words[-1]["end"] if self.words else 0)


class BeatScene(MovingCameraScene):
    BEAT = None

    def setup(self):
        super().setup()
        self.cues = Cues(self.BEAT)

    @property
    def now(self):
        return self.renderer.time

    def wait_to(self, t):
        dt = t - self.now
        if dt > 1 / 120:
            self.wait(dt)

    def play_until(self, t, *anims, min_time=0.25, **kw):
        """Play anims so they finish exactly at time t (or take min_time if already late)."""
        self.play(*anims, run_time=max(min_time, t - self.now), **kw)

    def play_from(self, t, *anims, run_time=1.0, **kw):
        """Start anims at time t."""
        self.wait_to(t)
        self.play(*anims, run_time=run_time, **kw)

    def drift(self, rate=0.006):
        """Continuous slow camera push-in (fraction of frame per second)."""
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - rate * dt))

    def finish(self):
        self.wait_to(self.cues.dur)


# ── type ────────────────────────────────────────────────────────────────────
def serif(s, size=40, color=INK, slant=NORMAL, weight=NORMAL, **kw):
    return Text(s, font=SERIF, font_size=size, color=color, slant=slant, weight=weight, **kw)


def sans(s, size=24, color=INK, weight=NORMAL, **kw):
    return Text(s, font=SANS, font_size=size, color=color, weight=weight, **kw)


def eyebrow(s, color=MUTED, size=17):
    """Small tracked uppercase label (section kickers, credits)."""
    return MarkupText(f'<span letter_spacing="3000">{s.upper()}</span>', font=SANS, font_size=size,
                      color=color, weight=MEDIUM)


def chip(s, color=NEEDLE, size=20, pad=0.18):
    t = sans(s, size=size, color=color, weight=MEDIUM)
    box = RoundedRectangle(corner_radius=0.12, width=t.width + 2 * pad + 0.1, height=t.height + 2 * pad,
                           stroke_color=color, stroke_width=1.5, stroke_opacity=0.7,
                           fill_color=color, fill_opacity=0.08)
    return VGroup(box, t.move_to(box))


def credit(s):
    """Bottom-left source line for screenshots and footage."""
    return sans(s, size=15, color=MUTED).to_corner(DL, buff=0.35)


# ── graphics ────────────────────────────────────────────────────────────────
def glow(mob, color=None, layers=6, max_width=22, max_opacity=0.18):
    """Soft bloom: widening, fading stroke copies behind mob."""
    color = color or mob.get_stroke_color()
    halo = VGroup()
    for i in range(layers, 0, -1):
        a = i / layers
        halo.add(mob.copy().set_fill(opacity=0).set_stroke(color=color, width=max_width * a,
                                                            opacity=max_opacity * (1 - a) ** 1.4 + 0.012))
    return VGroup(halo, mob)


def make_needle(length=4.0, angle=0.0, color=NEEDLE, width=7, with_glow=True):
    """A needle with a distinguishable tip (bright dot) so a half-turn is visible."""
    line = Line(LEFT * length / 2, RIGHT * length / 2, stroke_color=color, stroke_width=width)
    line.set_cap_style(CapStyleType.ROUND)
    tip = Dot(RIGHT * length / 2, radius=0.075, color=WHITE)
    tail = Dot(LEFT * length / 2, radius=0.05, color=color)
    body = glow(line) if with_glow else line
    g = VGroup(body, tail, tip)
    g.rotate(angle, about_point=ORIGIN)
    return g


def grid(opacity=0.35, step=0.5):
    return NumberPlane(
        x_range=[-9, 9, step], y_range=[-5, 5, step],
        background_line_style={"stroke_color": FAINT, "stroke_width": 1, "stroke_opacity": opacity},
        axis_config={"stroke_opacity": 0},
        faded_line_ratio=1,
    )


# ── paper helpers (long mode) ────────────────────────────────────────────────
def _paper_path():
    proj = json.loads((ROOT / "project.json").read_text())
    return ROOT / proj.get("paper", "research/paper.pdf")


def pdf_png(page, clip=None, dpi=300, name=None):
    """Render page (0-based) of the project's paper, optionally a clip rect (x0, y0, x1, y1) in PDF
    points, to assets/img/<name>.png (cached) and return the path."""
    import pymupdf
    name = name or f"paper_p{page}" + ("_" + "_".join(str(int(v)) for v in clip) if clip else "")
    out = ROOT / f"assets/img/{name}.png"
    if not out.exists():
        pg = pymupdf.open(str(_paper_path()))[page]
        pix = pg.get_pixmap(dpi=dpi, clip=pymupdf.Rect(*clip) if clip else None)
        out.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(out))
    return out


def paper_card(path, height=5.0):
    """A paper crop as a white sheet with a soft shadow."""
    img = ImageMobject(str(path)).set_height(height)
    shadow = Rectangle(width=img.width + 0.12, height=img.height + 0.12, stroke_width=0,
                       fill_color=BLACK, fill_opacity=0.55).shift(DOWN * 0.08 + RIGHT * 0.06)
    return Group(shadow, img)


def math_text(markup, size=40, color=INK):
    """Math without LaTeX, as Pango markup: math_text('softmax(<i>QK</i><sup>T</sup> / √<i>d</i><sub>k</sub>) <i>V</i>').
    Do not use Unicode sub/superscript characters (ₖ, ᵀ): CMU Serif lacks most of them and draws empty
    boxes. Check ≈ and ≡ too; draw them as shapes if they look wrong."""
    return MarkupText(markup, font=SERIF, font_size=size, color=color)
