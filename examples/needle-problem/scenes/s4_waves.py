from style import *
from s4_wavesim import R0, solve

FIELD_W = 6.0                       # on-screen width of the visible window [-1, 1]^2
FIELD_POS = LEFT * 3.35 + DOWN * 0.15


def hex_rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


class WaveField:
    """Intensity frames -> RGBA images: BG -> BLUE -> white, with a soft circular edge fade."""

    def __init__(self):
        self.frames, self.taus, self.peak = solve()
        self.I0 = self.peak[0]
        n = self.frames.shape[1]
        yy, xx = np.mgrid[0:n, 0:n]
        r = np.hypot(xx - (n - 1) / 2, yy - (n - 1) / 2) / ((n - 1) / 2)
        self.alpha = (np.clip((1.0 - r) / 0.18, 0, 1) ** 1.5 * 255).astype(np.uint8)
        self.bg, self.blue, self.white = hex_rgb(BG), hex_rgb(BLUE), hex_rgb("#FFFFFF")

    def rgba(self, tau):
        i = int(np.clip(np.searchsorted(self.taus, tau), 0, len(self.taus) - 1))
        a = np.sqrt(self.frames[i] / self.I0)
        lo = np.clip(a, 0, 1)[..., None] ** 1.7
        hi = np.clip((a - 1) / 3.5, 0, 1)[..., None]
        rgb = self.bg + (self.blue - self.bg) * lo
        rgb = rgb + (self.white - rgb) * hi
        out = np.empty(a.shape + (4,), np.uint8)
        out[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        out[..., 3] = self.alpha
        return out


class S4Waves(BeatScene):
    BEAT = "s4_waves"

    def construct(self):
        c = self.cues
        wf = WaveField()
        tau = ValueTracker(0.0)
        T_END = float(wf.taus[-1])

        # ── 1. the needle becomes a wavefront ("shadow of a deeper question") ──────────
        needle = make_needle(length=4.2)
        self.play(GrowFromCenter(needle), run_time=0.6)
        ring_r = R0 * FIELD_W / 2
        ring = Circle(radius=ring_r, stroke_color=NEEDLE, stroke_width=6)
        ring_g = glow(ring, color=NEEDLE)
        kicker = eyebrow("a deeper question about waves", color=BLUE).to_edge(UP, buff=0.55)
        self.wait_to(c.at("shadow") - 0.1)
        self.play(ReplacementTransform(needle, ring_g), run_time=1.5, rate_func=smooth)
        self.play_until(c.after("waves"), FadeIn(kicker, shift=DOWN * 0.1),
                        ring_g.animate.set_stroke(color=BLUE))

        # ── 2. the field takes over from the ring, slides left; graph appears right ────
        img = ImageMobject(wf.rgba(0.0)).set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        img.width = FIELD_W
        def refresh(m):
            m.pixel_array = wf.rgba(tau.get_value())
        img.add_updater(refresh)

        self.play(FadeIn(img), FadeOut(ring_g), run_time=0.5)

        ax = Axes(x_range=[0, T_END, 0.25], y_range=[0, float(wf.peak.max() / wf.I0) * 1.08, 20],
                  x_length=5.4, y_length=3.4, tips=False,
                  axis_config={"stroke_color": MUTED, "stroke_width": 2, "include_ticks": False})
        ax.move_to(RIGHT * 3.55 + DOWN * 0.55)
        xl = sans("time", size=20, color=MUTED).next_to(ax.x_axis, DOWN, buff=0.18).align_to(ax.x_axis, RIGHT)
        yl = sans("peak intensity", size=20, color=MUTED).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.18)
        yl.align_to(ax.y_axis, UP)
        graph_grp = VGroup(ax, xl, yl)

        norm_peak = wf.peak / wf.I0

        def curve():
            k = max(2, int(np.searchsorted(wf.taus, tau.get_value())))
            pts = [ax.c2p(t, p) for t, p in zip(wf.taus[:k], norm_peak[:k])]
            v = VMobject(stroke_color=NEEDLE, stroke_width=3.5).set_points_as_corners(pts)
            dot = Dot(pts[-1], radius=0.06, color=WHITE)
            return VGroup(v, dot)
        live = always_redraw(curve)

        self.play(img.animate.move_to(FIELD_POS), FadeIn(graph_grp, shift=LEFT * 0.2),
                  FadeOut(kicker), run_time=0.9)
        self.add(live)

        # Run the simulation so the focus lands on "peak".
        i_focus = int(norm_peak.argmax())
        tau_focus = float(wf.taus[i_focus])
        t0 = self.now
        t_focus = c.at("peak") + 0.15
        rate = tau_focus / (t_focus - t0)
        t_end = t0 + T_END / rate

        # Sogge credit label (lands on "Christopher Sogge") while the wave is still running.
        sogge = VGroup(eyebrow("local smoothing conjecture", color=NEEDLE),
                       serif("Christopher Sogge · 1991", size=30, color=INK)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        sogge.to_edge(UP, buff=0.5).shift(RIGHT * 3.0)

        t_sogge = min(c.at("Christopher") - 0.1, t_end - 0.6)
        tau_sogge = (t_sogge - t0) * rate
        self.play(tau.animate(rate_func=linear).set_value(tau_sogge), run_time=t_sogge - t0)
        self.play(tau.animate(rate_func=linear).set_value(T_END), FadeIn(sogge, shift=UP * 0.1),
                  run_time=t_end - t_sogge)

        # Wave has passed: the field bows out and the graph takes centre stage.
        self.play(FadeOut(img, scale=0.96), graph_grp.animate.scale(1.25).move_to(DOWN * 0.45 + LEFT * 0.2),
                  sogge.animate.to_edge(UP, buff=0.5).set_x(0), run_time=1.0)
        img.clear_updaters()

        # ── 3. "only last an instant": flag the spike ──────────────────────────────────
        spike_pt = ax.c2p(tau_focus, norm_peak[i_focus])
        worst = sans("worst moment", size=20, color=NEEDLE, weight=MEDIUM).next_to(spike_pt, RIGHT, buff=0.45)
        self.wait_to(c.at("only last") - 0.2)
        self.play(Flash(spike_pt, color=NEEDLE, line_length=0.25, num_lines=10, flash_radius=0.3),
                  FadeIn(worst, shift=LEFT * 0.1), run_time=0.8)

        # ── 4. "on average … far gentler": the time average sits far below ──────────────
        avg = float(norm_peak.mean())
        avg_line = DashedLine(ax.c2p(0, avg), ax.c2p(T_END, avg), stroke_color=TEAL, stroke_width=3, dash_length=0.12)
        avg_lab = sans("average", size=20, color=TEAL, weight=MEDIUM).next_to(avg_line, UP, buff=0.1).align_to(avg_line, RIGHT)
        self.wait_to(c.at("average") - 0.2)
        self.play(Create(avg_line), FadeIn(avg_lab, shift=UP * 0.1), run_time=0.9)
        # Replay a short focus in the field for visual life while the line holds.
        self.wait_to(c.after("worst") + 0.2)

        # ── 5. implication diagram ──────────────────────────────────────────────────────
        live.clear_updaters()
        self.play(*[FadeOut(m, shift=DOWN * 0.2) for m in (graph_grp, live, worst, avg_line, avg_lab)],
                  FadeOut(sogge, shift=UP * 0.2), run_time=0.7)

        def node(text, color, w=4.4, icon=None):
            t = serif(text, size=38, color=INK)
            content = VGroup(icon, t).arrange(RIGHT, buff=0.3) if icon is not None else t
            box = RoundedRectangle(corner_radius=0.18, width=max(w, content.width + 0.9), height=1.15,
                                   stroke_color=color, stroke_width=2.5, fill_color=color, fill_opacity=0.07)
            return VGroup(box, content.move_to(box))

        # Small icons tie the nodes back to the pictures: a needle star, and a sphere's arc.
        star = VGroup(*[Line(LEFT * 0.28, RIGHT * 0.28, stroke_color=NEEDLE, stroke_width=3).rotate(k * PI / 6)
                        for k in range(6)])
        cap = Arc(radius=0.34, start_angle=PI * 0.15, angle=PI * 0.7, stroke_color=BLUE, stroke_width=3.5)
        cap_dots = VGroup(*[Dot(cap.point_from_proportion(q), radius=0.035, color=BLUE) for q in (0.15, 0.5, 0.85)])
        top = node("Local smoothing", NEEDLE, w=5.0).move_to(UP * 1.75)
        top_g = VGroup(glow(top[0], color=NEEDLE, max_opacity=0.12), top[1])
        kak = node("Kakeya", INK, icon=star).move_to(DOWN * 1.55 + LEFT * 3.4)
        res = node("Restriction (Stein)", INK, w=5.0, icon=VGroup(cap, cap_dots)).move_to(DOWN * 1.55 + RIGHT * 3.4)
        a1 = Arrow(top.get_bottom() + LEFT * 1.2, kak.get_top(), buff=0.12, stroke_width=4, color=INK,
                   max_tip_length_to_length_ratio=0.12)
        a2 = Arrow(top.get_bottom() + RIGHT * 1.2, res.get_top(), buff=0.12, stroke_width=4, color=INK,
                   max_tip_length_to_length_ratio=0.12)
        sub = sans("Sogge, 1991", size=20, color=MUTED).next_to(top, UP, buff=0.2)

        self.wait_to(c.at("local smoothing") - 0.35)
        self.play(FadeIn(top_g, scale=0.92), FadeIn(sub), run_time=0.8)
        self.wait_to(c.at("Kakeya conjecture follows") - 0.15)
        self.play(GrowArrow(a1), FadeIn(kak, shift=DOWN * 0.15), run_time=0.9)
        self.wait_to(c.at("Stein's") - 0.2)
        self.play(GrowArrow(a2), FadeIn(res, shift=DOWN * 0.15), run_time=0.9)

        # ── 6. "only proven in 2019" (2D) ────────────────────────────────────────────────
        note = chip("proven in 2D only · Guth–Wang–Zhang, 2019", color=GREEN, size=19)
        note.move_to(DOWN * 3.15)
        self.wait_to(c.at("two dimensions") - 0.2)
        self.play(FadeIn(note, shift=UP * 0.15), run_time=0.8)
        self.finish()
