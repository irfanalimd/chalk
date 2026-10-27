"""Silent cards: title, chapter cards (with a progress rail), end card.

Text comes from project.json: title, kicker, byline, source, credits, chapters {"ch1": "..."}.
Beats: {"id": "title", "scene": "cards.py:Title", "dur": 3.4}, {"id": "ch1", "scene": "cards.py:Ch1",
"dur": 2.6}, ..., {"id": "end", "scene": "cards.py:End", "dur": 5.0}.
"""
import json

from style import *

PROJECT = json.loads((ROOT / "project.json").read_text())
CHAPTERS = PROJECT.get("chapters", {})
N = len(CHAPTERS)


def rail(current):
    """Nine short segments; finished ones white, the current one gold, the rest faint."""
    segs = VGroup()
    for i in range(1, N + 1):
        col, op = (NEEDLE, 1.0) if i == current else ((INK, 0.55) if i < current else (INK, 0.15))
        segs.add(Line(LEFT * 0.22, RIGHT * 0.22, stroke_width=3, stroke_color=col, stroke_opacity=op))
    return segs.arrange(RIGHT, buff=0.12)


class ChapterCard(BeatScene):
    NUM = 1

    def construct(self):
        kicker = eyebrow(f"Chapter {self.NUM} of {N}", color=NEEDLE, size=18)
        title = serif(CHAPTERS[f"ch{self.NUM}"], size=64, color=INK)
        r = rail(self.NUM)
        block = VGroup(kicker, title, r).arrange(DOWN, buff=0.38)
        block.move_to(UP * 0.35)
        self.play(FadeIn(kicker, shift=UP * 0.1), FadeIn(title, shift=UP * 0.18),
                  LaggedStart(*[FadeIn(s) for s in r], lag_ratio=0.06), run_time=0.8)
        self.wait_to(self.cues.dur - 0.6)
        self.play(FadeOut(block, shift=UP * 0.12), run_time=0.55)
        self.finish()


def _mk(n):
    cls = type(f"Ch{n}", (ChapterCard,), {"NUM": n, "BEAT": f"ch{n}"})
    globals()[cls.__name__] = cls


for _n in range(1, N + 1):
    _mk(_n)


class Title(BeatScene):
    BEAT = "title"

    def construct(self):
        kicker = eyebrow(PROJECT.get("kicker", "A guided reading"), color=MUTED, size=18)
        title = serif(PROJECT["title"], size=78, color=INK)
        rule = Line(LEFT, RIGHT, stroke_color=NEEDLE, stroke_width=3).set_width(2.4)
        authors = sans(PROJECT.get("byline", ""), size=19, color=MUTED)
        block = VGroup(kicker, title, rule, authors).arrange(DOWN, buff=0.34).move_to(UP * 0.3)
        self.drift(0.01)
        self.play(FadeIn(kicker), FadeIn(title, scale=0.97), run_time=0.9)
        self.play(GrowFromCenter(rule), FadeIn(authors, shift=UP * 0.1), run_time=0.7)
        self.wait_to(self.cues.dur - 0.7)
        self.play(FadeOut(block), run_time=0.6)
        self.finish()


class End(BeatScene):
    BEAT = "end"

    def construct(self):
        title = serif(PROJECT["title"], size=46, color=INK)
        src = sans(PROJECT.get("source", ""), size=18, color=MUTED)
        block = VGroup(title, src).arrange(DOWN, buff=0.28).move_to(UP * 0.3)
        fine = sans(PROJECT.get("credits", ""), size=10, color=MUTED).set_opacity(0.55).to_edge(DOWN, buff=0.22)
        self.play(FadeIn(title, shift=UP * 0.12), FadeIn(src), FadeIn(fine), run_time=1.0)
        self.wait_to(self.cues.dur - 0.9)
        self.play(FadeOut(block), FadeOut(fine), run_time=0.8)
        self.finish()
