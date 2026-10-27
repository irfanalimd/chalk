from style import *


class S1Puzzle(BeatScene):
    BEAT = "s1_puzzle"

    def construct(self):
        c = self.cues
        frame = self.camera.frame
        plane = grid(opacity=0.0)
        self.add(plane)

        self.drift(0.006)  # slow push-in across the whole beat

        # Museum-label caption: year + name.
        year = serif("1917", size=64, color=INK)
        name = serif("Sōichi Kakeya", size=30, color=MUTED, slant=ITALIC)
        rule = Line(LEFT, RIGHT, stroke_color=NEEDLE, stroke_width=2).set_width(0.6)
        label = VGroup(year, rule, name).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UL, buff=0.9)

        # Archival portrait card with a slow Ken Burns drift.
        photo = ImageMobject(str(ROOT / "assets/img/kakeya_sepia.png")).set_height(5.6)
        frame_box = SurroundingRectangle(photo, buff=0.0, stroke_color=INK, stroke_width=1.2, stroke_opacity=0.5)
        card = Group(photo, frame_box).move_to(RIGHT * 2.4 + DOWN * 0.1)
        src = sans("Wikimedia Commons, CC BY-SA 4.0", size=11, color=MUTED).set_opacity(0.7)
        src.next_to(frame_box, DOWN, buff=0.08, aligned_edge=RIGHT)
        photo.add_updater(lambda m, dt: m.scale(1 + 0.01 * dt))

        self.wait_to(c.at("nineteen") - 0.2)
        self.play(FadeIn(year, shift=UP * 0.15), Create(rule), FadeIn(card, shift=LEFT * 0.3), FadeIn(src), run_time=1.0)
        self.play_until(c.after("Kakeya"), FadeIn(name, shift=UP * 0.1))
        q = serif("?", size=150, color=FAINT).move_to(ORIGIN)
        self.wait_to(c.after("children") - 0.6)
        self.play(FadeOut(card, shift=RIGHT * 0.3), FadeOut(src), run_time=1.0)
        photo.clear_updaters()
        self.add(q.set_opacity(0))

        # The needle, on a table (the grid comes up to become the tabletop).
        needle = make_needle(length=4.2)
        self.wait_to(c.at("needle") - 0.3)
        self.play(FadeOut(q, scale=1.1), GrowFromCenter(needle), run_time=0.8)
        self.play_until(c.after("table"), plane.background_lines.animate.set_stroke(opacity=0.35))

        # "What is the smallest region…": a dashed, uncertain boundary breathes around the needle.
        region = DashedVMobject(Circle(radius=2.45, stroke_color=BLUE, stroke_width=2.5), num_dashes=60)
        region_label = serif("smallest area?", size=34, color=BLUE, slant=ITALIC).next_to(region, DOWN, buff=0.35)
        self.wait_to(c.at("smallest region") - 0.15)
        self.play(Create(region), FadeIn(region_label, shift=UP * 0.1), run_time=1.1)
        room = c.at("turn it") - 0.1 - self.now
        if room > 0.8:  # breathe only if it doesn't delay the turn
            self.play(region.animate.scale(0.82), rate_func=there_and_back, run_time=min(1.2, room))

        # "…turn it all the way around": a ghost stays behind, the tip ends up on the other side.
        ghost = needle.copy().set_opacity(0.18)
        self.add(ghost)
        self.wait_to(c.at("turn it") - 0.1)
        self.play(Rotate(needle, PI, about_point=ORIGIN), run_time=max(1.4, c.voice_end + 0.2 - self.now),
                  rate_func=smooth)
        arrow = CurvedArrow(RIGHT * 2.6 + UP * 0.25, LEFT * 2.6 + UP * 0.25, angle=PI * 0.8,
                            color=NEEDLE, stroke_width=3, tip_length=0.2)
        arrow[0].set_fill(opacity=0)
        self.play(Create(arrow), run_time=0.45)
        self.wait_to(c.dur - 0.4)
        self.play(*[FadeOut(m) for m in (label, region, region_label, arrow, ghost)], run_time=min(0.4, c.dur - self.now))
        self.finish()
