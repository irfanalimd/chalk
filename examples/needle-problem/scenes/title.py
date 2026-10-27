from style import *


class Title(BeatScene):
    BEAT = "title"

    def construct(self):
        # Scene 1 ends with the needle horizontal at centre, seen through a ~0.92x pushed-in camera;
        # start at the matching apparent size so the cut reads as continuous.
        needle = make_needle(length=4.2 / 0.916)
        self.add(needle)

        kicker = eyebrow("A century-old puzzle", color=MUTED, size=18)
        title = serif("The Needle Problem", size=92, color=INK)
        VGroup(kicker, title).arrange(DOWN, buff=0.35).move_to(UP * 0.35)
        rule_y = title.get_bottom()[1] - 0.45
        rule = Line(LEFT * 1.6, RIGHT * 1.6, stroke_color=NEEDLE, stroke_width=3).move_to(UP * rule_y)
        rule.set_cap_style(CapStyleType.ROUND)
        tip = Dot(rule.get_end(), radius=0.05, color=WHITE)

        # The needle makes one half-turn while it narrows into the gold rule beneath the title.
        target = VGroup(glow(rule, max_width=14, max_opacity=0.25), Dot(rule.get_start(), radius=0.035, color=NEEDLE), tip)
        target.rotate(PI, about_point=rule.get_center())  # tip ends on the left: the needle has turned around
        self.play(LaggedStart(Transform(needle, target, path_arc=PI, rate_func=smooth),
                              AnimationGroup(FadeIn(title, shift=UP * 0.25), FadeIn(kicker, shift=UP * 0.15)),
                              lag_ratio=0.5), run_time=1.3)
        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - 0.02 * dt))
        self.wait_to(self.cues.dur - 0.6)
        self.play(FadeOut(VGroup(needle, title, kicker), shift=UP * 0.12), run_time=0.55)
        self.finish()
