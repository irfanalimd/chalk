from style import *
from staircase import Staircase, LABELS

PANEL = "#11141B"


def result_card(field, title, note, color, width=4.3, height=2.6):
    box = RoundedRectangle(corner_radius=0.16, width=width, height=height, fill_color=PANEL, fill_opacity=1,
                           stroke_color=FAINT, stroke_width=1.5)
    rule = Line(box.get_corner(UL) + RIGHT * 0.3, box.get_corner(UR) + LEFT * 0.3,
                stroke_color=color, stroke_width=4).shift(DOWN * 0.02)
    kick = eyebrow(field, color=color, size=13)
    head = VGroup(*[serif(t, size=27, color=INK) for t in title.split("\n")]).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    foot = sans(note, size=15, color=MUTED)
    body = VGroup(kick, head, foot).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
    body.scale_to_fit_width(min(body.width, width - 0.7))
    body.align_to(box, LEFT).align_to(box, UP).shift(RIGHT * 0.35 + DOWN * 0.42)
    return VGroup(box, rule, body)


class S6Close(BeatScene):
    BEAT = "s6_close"

    def construct(self):
        c = self.cues
        frame = self.camera.frame

        # ── "only begun to verify it": no caption card — the staircase assembles quietly, every step open ──
        st = Staircase()
        self.drift(0.004)
        self.wait_to(c.at("mathematical") - 0.3)
        self.play(st.build(run_time=2.4))
        self.play(LaggedStart(*[st.mark(l, "open", run_time=0.45) for l in LABELS], lag_ratio=0.18))
        frame.clear_updaters()

        def milestone(lab, lines):
            t = VGroup(*[sans(s, size=16, color=GREEN) for s in lines]).arrange(DOWN, buff=0.06)
            return t.next_to(st.tags[lab], DOWN, buff=0.14)

        m2, m3 = milestone("2D", ["Davies", "1971"]), milestone("3D", ["Wang & Zahl", "2025"])
        m3.shift(RIGHT * 0.14)  # clear the riser to its left
        self.wait_to(c.at("climbed") - 0.1)
        self.play(st.mark("2D", "proven"), FadeIn(m2, shift=UP * 0.08))
        self.wait_to(c.at("dimension") + 0.05)
        self.play(st.mark("3D", "proven"), FadeIn(m3, shift=UP * 0.08))
        self.wait_to(c.at("finest") - 0.1)
        self.play(Indicate(VGroup(m2, m3), color=GREEN, scale_factor=1.08), run_time=0.9)

        # ── "carried all the way to the top in a single proof" ────────────────────
        stroke = st.outline.copy().set_stroke(color=NEEDLE, width=6, opacity=1)
        stroke_glow = glow(stroke, color=NEEDLE, max_width=26, max_opacity=0.22)
        frame.save_state()
        self.wait_to(c.at("carried") - 0.1)
        self.play(Create(stroke_glow, rate_func=rush_into), st.climb(start="4D", run_time=1.6),
                  frame.animate.scale(1.12).move_to(st.outline.get_center() + UP * 0.35), run_time=1.8)
        tag = chip("one proof · written by a machine", color=NEEDLE, size=18)
        tag.next_to(st.marks["nD"], UP, buff=0.2).shift(LEFT * 1.1)
        self.wait_to(c.at("written") - 0.2)
        self.play(FadeIn(tag, shift=DOWN * 0.1), run_time=0.6)

        # ── "one of three such results announced today" ──────────────────────────
        stairs_all = VGroup(st, *st.marks.values(), m2, m3, stroke_glow, tag)
        self.wait_to(c.at("And it") - 0.35)
        self.play(FadeOut(stairs_all, shift=UP * 0.4), Restore(frame), run_time=0.6)
        cards = VGroup(
            result_card("Harmonic analysis", "Kakeya &\nlocal smoothing", "released openly", NEEDLE),
            result_card("Computer science", "The Exponential Time\nHypothesis is false", "Impagliazzo · Paturi · Williams", BLUE),
            result_card("Physics", "Existence of quantum\nchromodynamics", "group led by David Gross", PURPLE),
        ).arrange(RIGHT, buff=0.25).move_to(DOWN * 0.25)
        kicker = eyebrow("Announced October 26, 2026", color=MUTED, size=17).next_to(cards, UP, buff=0.6)
        self.play(FadeIn(kicker, shift=DOWN * 0.1),
                  LaggedStart(*[FadeIn(cd, shift=UP * 0.35) for cd in cards], lag_ratio=0.28), run_time=1.5)
        self.finish()
