from style import *
from staircase import Staircase, LABELS

PALETTE = [NEEDLE, ORANGE, RED, PURPLE, BLUE, TEAL, NEEDLE]


def dir_color(a):
    """Colour for a direction a in [0, 1) (fraction of a half-turn), looping through the palette."""
    a = (a % 1.0) * (len(PALETTE) - 1)
    i = int(a)
    return interpolate_color(ManimColor(PALETTE[i]), ManimColor(PALETTE[i + 1]), a - i)


def bitrev(k, bits):
    return int(format(k, f"0{bits}b")[::-1], 2)


def needle_fan(n=48, length=3.6):
    """Needles through the origin in n directions (a star = a disc of needles)."""
    g = VGroup()
    for k in range(n):
        th = PI * k / n
        d = np.array([np.cos(th), np.sin(th), 0])
        ln = Line(-d * length / 2, d * length / 2, stroke_width=3, stroke_color=dir_color(k / n))
        ln.set_cap_style(CapStyleType.ROUND)
        g.add(ln)
    return g


def thin_targets(fan, length=3.6, groups=3):
    """Same needles rearranged into three overlapping, Perron-like thin fans (60° of directions each)."""
    n = len(fan)
    per = n // groups
    bits = int(np.log2(per)) if 2 ** int(np.log2(per)) == per else None
    out = VGroup()
    for k, ln in enumerate(fan):
        th = PI * k / n
        gi, j = divmod(k, per)
        axis = PI / 2 + gi * PI / 3 - PI / 3          # each group centred on a different axis
        rel = th - axis
        rel = (rel + PI / 2) % PI - PI / 2           # relative angle in (-90°, 90°]
        u = np.array([np.cos(axis), np.sin(axis), 0])     # group axis
        w = np.array([-np.sin(axis), np.cos(axis), 0])    # perpendicular
        jitter = (bitrev(j, bits) if bits else (j * 7) % per) / per - 0.5
        base = u * (-1.55) + w * (-0.82 * np.sin(rel) * length / 2 * 1.45 + 0.22 * jitter)
        d = np.array([np.cos(th), np.sin(th), 0])
        if np.dot(d, u) < 0:
            d = -d
        tgt = Line(base, base + d * length, stroke_width=1.8, stroke_color=ln.get_stroke_color())
        tgt.set_cap_style(CapStyleType.ROUND)
        out.add(tgt)
    out.move_to(ORIGIN)
    return out


def fib_dirs(n):
    """n roughly even unit directions on the upper hemisphere (a line has two ends)."""
    pts = []
    g = PI * (3 - np.sqrt(5))
    for i in range(n):
        z = 1 - (i + 0.5) / n          # (0, 1]
        r = np.sqrt(1 - z * z)
        pts.append(np.array([r * np.cos(g * i), r * np.sin(g * i), z]))
    return pts


def rot(yaw, pitch):
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    return Rx @ Ry


class S3Conjecture(BeatScene):
    BEAT = "s3_conjecture"

    def construct(self):
        c = self.cues
        frame = self.camera.frame
        plane = grid(opacity=0.35)
        kicker = eyebrow("A subtler question").to_edge(UP, buff=0.6)

        # 0 · a faint gold echo of the previous scene's spiky set, which then opens into the full fan
        fan = needle_fan()
        echo = thin_targets(needle_fan()).set_stroke(color=NEEDLE, opacity=0.3)
        echo.add_updater(lambda m, dt: m.rotate(0.03 * dt))
        self.play(FadeIn(plane), FadeIn(echo, scale=1.04), run_time=1.0)
        self.play(FadeIn(kicker, shift=DOWN * 0.1), run_time=0.8)

        # 1 · needles in every direction → compressed into a thin, spiky set → zoom in
        self.wait_to(c.at("set") - 0.6)
        echo.clear_updaters()
        self.play_until(c.after("direction") + 0.1, ReplacementTransform(echo, fan), rate_func=smooth)
        thin = thin_targets(fan)
        self.wait_to(c.at("almost") - 0.2)
        self.play_until(c.after("area") + 0.2, Transform(fan, thin), rate_func=smooth)

        self.wait_to(c.at("truly") - 0.4)
        frame.save_state()
        focus = fan.get_center() + UP * 0.35 + RIGHT * 0.15
        self.play_until(c.after("thin") + 0.35, frame.animate.scale(0.3).move_to(focus), FadeOut(kicker),
                        rate_func=smooth)

        # 2 · the conjecture, in words
        title = serif("The Kakeya conjecture", size=54).to_edge(UP, buff=0.75)
        stmt = serif("A set with a needle in every direction\nmust have full dimension.", size=34,
                     color=NEEDLE, slant=ITALIC, line_spacing=0.9).next_to(title, DOWN, buff=0.35)
        self.wait_to(c.at("Kakeya") - 0.45)
        self.play(Restore(frame), fan.animate.set_opacity(0.22).scale(0.8).shift(DOWN * 0.9),
                  FadeIn(title, shift=UP * 0.15), run_time=0.9)
        self.play_until(c.after("cannot") + 0.1, Write(stmt))

        # dimension, a finer notion of size: point / line / square
        y = DOWN * 1.55
        pt = Dot(radius=0.09, color=INK)
        seg = Line(LEFT * 0.75, RIGHT * 0.75, stroke_color=INK, stroke_width=5)
        sq = Square(1.4, stroke_color=NEEDLE, stroke_width=3, fill_color=NEEDLE, fill_opacity=0.25)
        icons = VGroup(pt, seg, sq).arrange(RIGHT, buff=1.6).move_to(y)
        labs = VGroup(*[sans(f"dimension {d}", size=20, color=MUTED).next_to(m, DOWN, buff=0.3)
                        for d, m in zip((0, 1, 2), icons)])
        labs.align_to(labs[2], DOWN)
        for l in labs:
            l.set_y(sq.get_bottom()[1] - 0.35)
        self.wait_to(c.at("measured") - 0.1)
        self.play(FadeOut(fan), run_time=0.4)
        self.play_until(c.after("size") + 0.1,
                        LaggedStart(*[AnimationGroup(FadeIn(m, scale=0.6), FadeIn(l, shift=UP * 0.1))
                                      for m, l in zip(icons, labs)], lag_ratio=0.3))
        sq_glow = glow(sq.copy().set_fill(opacity=0), color=NEEDLE, max_width=30, max_opacity=0.3)[0]
        self.wait_to(c.at("fill") - 0.1)
        self.play(FadeIn(sq_glow), sq.animate.set_fill(opacity=0.55), labs[2].animate.set_color(NEEDLE),
                  pt.animate.set_opacity(0.3), seg.animate.set_stroke(opacity=0.3),
                  labs[0].animate.set_opacity(0.4), labs[1].animate.set_opacity(0.4), run_time=0.9)

        # 3 · the staircase of dimensions, compact on the left
        st = Staircase(step_w=0.8, step_h=0.44, origin=np.array([-6.55, -2.35, 0]))
        st_kick = eyebrow("Proven in", size=14).next_to(st, UP, buff=0.35).align_to(st, LEFT)
        self.wait_to(c.at("plane") - 0.45)
        self.play(FadeOut(VGroup(stmt, icons, labs, sq_glow), shift=UP * 0.2),
                  title.animate.scale(0.62).move_to(frame.get_corner(UL) + np.array([0.6, -0.6, 0]), aligned_edge=UL),
                  run_time=0.6)
        self.play(st.build(run_time=1.0), FadeIn(st_kick), run_time=1.0)
        self.wait_to(c.at("settled") - 0.1)
        self.play(st.mark("2D", "proven"))

        # rotating 3D fan of needles, where the footage box will later sit
        cx = np.array([PIP["center"][0], PIP["center"][1], 0])
        dirs = fib_dirs(70)
        clock = ValueTracker(0)
        R0 = 1.65

        def fan3d():
            Rm = rot(0.35 + clock.get_value() * 0.55, -0.42)
            g = VGroup()
            for i, v in enumerate(dirs):
                p = Rm @ v
                for s in (1, -1):
                    tip = s * p
                    depth = (tip[2] + 1) / 2          # 0 far … 1 near
                    ln = Line(cx, cx + np.array([tip[0], tip[1], 0]) * R0,
                              stroke_color=dir_color(i / len(dirs) * 2.3),
                              stroke_width=1.2 + 2.6 * depth, stroke_opacity=0.25 + 0.75 * depth)
                    g.add(ln)
            g.submobjects.sort(key=lambda m: m.get_stroke_width())
            return g

        sphere = Circle(radius=R0, stroke_color=INK, stroke_width=1, stroke_opacity=0.18).move_to(cx)
        tag3d = sans("three dimensions", size=20, color=MUTED).next_to(sphere, DOWN, buff=0.3)
        fan3 = always_redraw(fan3d)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        self.wait_to(c.at("three") - 0.35)
        self.play(FadeIn(fan3), Create(sphere), FadeIn(tag3d, shift=UP * 0.1), run_time=0.8)
        self.wait_to(c.at("proven") - 0.05)
        self.play(st.mark("3D", "proven"))

        # 4 · footage box for Hong Wang (clip composited in post)
        bw = PIP["width"]
        box = RoundedRectangle(corner_radius=0.08, width=bw, height=bw * 9 / 16, stroke_color=INK,
                               stroke_width=1.5, stroke_opacity=0.5, fill_color=BG, fill_opacity=1).move_to(cx)
        names = serif("Hong Wang  ·  Joshua Zahl", size=30).next_to(box, DOWN, buff=0.28).align_to(box, LEFT)
        medal = chip("2026 Fields Medal — Hong Wang", size=17).next_to(names, RIGHT, buff=0.35)
        if medal.get_right()[0] > 7.0:
            medal.next_to(names, DOWN, buff=0.18).align_to(names, LEFT)
        src = credit("Video: Simons Foundation")
        self.wait_to(c.at("by") - 0.45)
        self.play(FadeOut(VGroup(sphere, tag3d)), FadeOut(fan3), FadeIn(box, scale=0.96), run_time=0.45)
        self.remove(fan3)
        clock.clear_updaters()
        t0 = self.now
        self.play(FadeIn(names, shift=UP * 0.1), FadeIn(src), run_time=0.6)
        self.wait_to(c.at("fields") - 0.25)
        self.play(FadeIn(medal, shift=UP * 0.1), run_time=0.5)
        self.wait_to(c.at("beyond") - 0.35)
        t1 = self.now
        print("PIP", round(t0, 3), round(t1, 3))
        self.play(FadeOut(VGroup(box, names, medal, src)), run_time=0.4)

        # 5 · beyond that, open — the upper steps fade into the dark
        st_group = VGroup(st, st_kick)
        self.play(st_group.animate.scale(1.3).move_to(DOWN * 0.3 + RIGHT * 0.4), run_time=0.7)
        opens = LABELS[2:]
        self.play(LaggedStart(*[st.mark(l, "open", run_time=0.35) for l in opens], lag_ratio=0.35),
                  run_time=max(0.8, c.after("open") - self.now))
        fades = []
        for i, l in enumerate(opens):
            o = max(0.08, 1 - 0.17 * (i + 1))
            fades += [st.tags[l].animate.set_opacity(o), st.marks[l].animate.set_opacity(o)]
        self.play(*fades, st.outline.animate.set_stroke(color=[INK, INK, BG]), run_time=0.5)
        self.wait_to(c.dur - 0.4)
        self.play_until(c.dur, FadeOut(VGroup(st_group, title)), min_time=1 / 30)
        self.finish()
