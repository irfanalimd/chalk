from style import *


class End(BeatScene):
    BEAT = "end"

    def construct(self):
        plane = grid(opacity=0.3)
        needle = make_needle(length=3.2).shift(UP * 0.55)
        self.play(FadeIn(plane), FadeIn(needle, scale=0.9), run_time=0.5)
        self.play(Rotate(needle, PI, about_point=needle.get_center()), run_time=1.5, rate_func=smooth)

        title = serif("The Needle Problem", size=46, color=INK)
        src1 = sans("Source: OpenAI, “Working with academic communities to build scientific understanding”, Oct 26 2026",
                    size=17, color=MUTED)
        src2 = sans("github.com/openai/math", size=17, color=MUTED)
        src3 = sans("Footage: Simons Foundation  ·  Music: “Clean Soul”, “Inspired” by Kevin MacLeod (incompetech.com), CC BY 4.0",
                    size=10, color=MUTED).set_opacity(0.55)
        block = VGroup(title, src1, src2).arrange(DOWN, buff=0.22).next_to(needle, DOWN, buff=0.7)
        block[1].shift(DOWN * 0.12)
        block[2].shift(DOWN * 0.12)
        src3.to_edge(DOWN, buff=0.22)
        self.play(FadeIn(title, shift=UP * 0.15), LaggedStart(FadeIn(src1), FadeIn(src2), lag_ratio=0.3), FadeIn(src3),
                  run_time=0.9)
        self.wait_to(self.cues.dur - 0.75)
        self.play(*[FadeOut(m) for m in (plane, needle, block, src3)], run_time=0.7)
        self.finish()
