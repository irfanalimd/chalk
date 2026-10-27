from functools import lru_cache

from scipy.optimize import brentq, minimize
from shapely.geometry import Polygon as SPoly
from shapely.ops import unary_union

from style import *

L = 4.2            # needle length (matches scene 1)
R_ROLL = L / 4     # deltoid rolling-circle radius: every tangent chord has length 4r
S1_DRIFT = float(np.exp(-0.006 * Cues("s1_puzzle").dur))  # camera scale scene 1 ends on


# ── deltoid geometry ─────────────────────────────────────────────────────────
def deltoid_point(t, r=R_ROLL):
    return np.array([2 * r * np.cos(t) + r * np.cos(2 * t), 2 * r * np.sin(t) - r * np.sin(2 * t), 0.0])


DELTOID_CENTER = np.array([-R_ROLL, 0, 0])  # puts the horizontal chord (t=0) centred on the origin


def deltoid_chord(t):
    """Tangent chord at parameter t: (midpoint, unit direction of the tip). Direction turns as -t/2."""
    u = np.array([np.cos(-t / 2), np.sin(-t / 2), 0.0])
    p = deltoid_point(t)
    def f(s):
        d = deltoid_point(s) - p
        return u[0] * d[1] - u[1] * d[0]
    # the tangent line crosses the curve at two other parameters; find them by bracketing
    grid_s = np.linspace(t + 1e-3, t + 2 * np.pi - 1e-3, 721)
    r = R_ROLL
    gx = 2 * r * np.cos(grid_s) + r * np.cos(2 * grid_s) - p[0]
    gy = 2 * r * np.sin(grid_s) - r * np.sin(2 * grid_s) - p[1]
    vals = u[0] * gy - u[1] * gx
    roots = [brentq(f, a, b) for a, b, fa, fb in zip(grid_s, grid_s[1:], vals, vals[1:]) if fa * fb < 0]
    ends = [deltoid_point(s) for s in roots]
    lam = sorted(np.dot(e - p, u) for e in ends)
    if len(lam) < 2:            # at a cusp the tangent chord runs from the cusp through the opposite side
        lam = [min(lam + [0.0]), max(lam + [0.0])]
    mid = p + u * (lam[0] + lam[-1]) / 2
    return mid + DELTOID_CENTER, u


# ── Perron tree ─────────────────────────────────────────────────────────────
TRI_H = 5.0
TRI_W = TRI_H * 2 / np.sqrt(3)          # equilateral: holds every direction within 60°
TRI_BASE_Y = -2.95
TRI_CX = 0.0


def offsets(k, s):
    n = 2 ** k
    x = np.array([-sum(s[j] for j in range(k) if (i >> j) & 1) for i in range(n)])
    return x - x.mean()


def sliver_pts(k, i, dx):
    n = 2 ** k
    xs = np.linspace(-TRI_W / 2, TRI_W / 2, n + 1) + TRI_CX
    return [(xs[i] + dx, TRI_BASE_Y), (xs[i + 1] + dx, TRI_BASE_Y), (TRI_CX + dx, TRI_BASE_Y + TRI_H)]


def union_ratio(k, xs):
    u = unary_union([SPoly(sliver_pts(k, i, dx)) for i, dx in enumerate(xs)])
    return u.area / (TRI_W * TRI_H / 2)


@lru_cache(None)
def best_shifts(k):
    """Per-level slide distances minimising the real union area (warm-started from level k-1)."""
    w = TRI_W / 2 ** k
    prev = list(best_shifts(k - 1)) if k > 1 else []
    s0 = np.array(prev + [w * 2 ** (k - 1) * 0.6])
    best = None
    for sc in (1.0, 0.8, 1.2):
        r = minimize(lambda s: union_ratio(k, offsets(k, np.clip(s, 0, None))), s0 * sc, method="Nelder-Mead",
                     options={"maxiter": 3000, "xatol": 1e-6, "fatol": 1e-7})
        if best is None or r.fun < best.fun:
            best = r
    return tuple(np.clip(best.x, 0, None))


def sliver_mob(k, i, dx):
    return Polygon(*[np.array([x, y, 0]) for x, y in sliver_pts(k, i, dx)],
                   stroke_color=BLUE, stroke_width=1.2 if k <= 5 else 0.8, stroke_opacity=0.75,
                   fill_color=BLUE, fill_opacity=0.16)


class S2Area(BeatScene):
    BEAT = "s2_area"

    def construct(self):
        c = self.cues
        frame = self.camera.frame
        self.add(grid(opacity=0.35))
        frame.scale(S1_DRIFT)

        # ── 1. the disc ─────────────────────────────────────────────────────
        needle = make_needle(length=L).rotate(PI, about_point=ORIGIN)
        self.add(needle)
        theta = ValueTracker(0.0)
        sweep = always_redraw(lambda: VGroup(*[
            Sector(radius=L / 2, angle=max(theta.get_value(), 1e-4), start_angle=a,
                   fill_color=BLUE, fill_opacity=0.22, stroke_width=0) for a in (PI, 0)]))
        self.add(sweep, needle)
        self.play_until(c.after("disc"), theta.animate.set_value(PI), Rotate(needle, PI, about_point=ORIGIN),
                        frame.animate.scale(1 / S1_DRIFT), rate_func=smooth)
        disc = Circle(radius=L / 2, fill_color=BLUE, fill_opacity=0.22, stroke_color=BLUE, stroke_width=2)
        disc_label = serif("disc", size=34, color=BLUE, slant=ITALIC).move_to(UR * 1.75 + RIGHT * 0.35)
        self.remove(sweep)
        self.add(disc, needle)
        self.play(FadeIn(disc_label, shift=DOWN * 0.1), run_time=0.5)

        # ── 2. the deltoid ──────────────────────────────────────────────────
        delt_pts = [deltoid_point(t) + DELTOID_CENTER for t in np.linspace(0, TAU, 400)]
        deltoid = VMobject(fill_color=TEAL, fill_opacity=0.25, stroke_color=TEAL, stroke_width=3)
        deltoid.set_points_smoothly(delt_pts)
        disc_ghost = DashedVMobject(Circle(radius=L / 2, stroke_color=BLUE, stroke_width=2, stroke_opacity=0.6),
                                    num_dashes=70)
        delt_label = serif("deltoid", size=34, color=TEAL, slant=ITALIC).move_to(LEFT * 3.7 + DOWN * 2.2)
        self.wait_to(c.at("curved") - 0.1)
        self.add(disc_ghost)
        self.play_until(c.after("deltoid"), ReplacementTransform(disc, deltoid), FadeOut(disc_label),
                        FadeIn(delt_label, shift=UP * 0.1), rate_func=smooth)

        # needle glides through a half-turn on tangent chords (real geometry); bars land on "half"
        frac = ValueTracker(0.0)
        self.remove(needle)
        glider = always_redraw(lambda: self._chord_needle(TAU * smooth(frac.get_value())))
        self.add(glider)
        bars = self._area_bars()
        t0, t3 = self.now, c.at("but") - 0.1
        seg = lambda t: (t - t0) / (t3 - t0)
        t1, t2 = c.at("manages") - 0.1, c.at("half") - 0.1
        self.play(frac.animate.set_value(seg(t1)), run_time=t1 - t0, rate_func=linear)
        self.play(frac.animate.set_value(seg(t2)), LaggedStart(*[FadeIn(b, shift=LEFT * 0.2) for b in bars[:2]],
                  lag_ratio=0.3), run_time=t2 - t1, rate_func=linear)
        self.play(frac.animate.set_value(1.0), FadeIn(bars[2], shift=LEFT * 0.1, rate_func=smooth),
                  run_time=t3 - t2, rate_func=linear)

        # ── 3. Besicovitch ──────────────────────────────────────────────────
        name = serif("Abram Besicovitch", size=40, color=INK)
        rule = Line(LEFT, RIGHT, stroke_color=NEEDLE, stroke_width=2).set_width(0.6)
        sub = serif("there is no smallest area", size=28, color=MUTED, slant=ITALIC)
        label = VGroup(name, rule, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.18).to_corner(UL, buff=0.7)
        self.remove(glider)
        last = self._chord_needle(TAU)
        self.add(last)
        self.play(FadeOut(VGroup(deltoid, disc_ghost, delt_label, last, bars)), FadeIn(name, shift=UP * 0.15),
                  Create(rule), run_time=0.7)

        # the triangle: a needle pivoting at the apex sweeps a 60° slice of directions
        apex = np.array([TRI_CX, TRI_BASE_Y + TRI_H, 0])
        tri = Polygon(*[np.array([x, y, 0]) for x, y in sliver_pts(0, 0, 0)], stroke_color=BLUE, stroke_width=2,
                      fill_color=BLUE, fill_opacity=0.16)
        self.wait_to(c.at("showed"))
        self.play(DrawBorderThenFill(tri), run_time=1.0)
        phi = ValueTracker(-PI / 2 - PI / 6)
        pivot = always_redraw(lambda: Line(apex, apex + TRI_H / np.cos(phi.get_value() + PI / 2) *
                                           np.array([np.cos(phi.get_value()), np.sin(phi.get_value()), 0]),
                                           stroke_color=NEEDLE, stroke_width=5))
        self.add(pivot)
        meter = self._meter()
        self.play(phi.animate(rate_func=there_and_back_with_pause).set_value(-PI / 2 + PI / 6),
                  FadeIn(meter[0], rate_func=smooth), run_time=1.6)
        self.add(meter[1], meter[2])
        self.play_until(c.after("all"), FadeIn(sub, shift=UP * 0.1), FadeOut(pivot))
        self.remove(pivot)

        # ── 4. slicing ──────────────────────────────────────────────────────
        self.n_slivers = 1
        count = always_redraw(lambda: sans(f"{self.n_slivers} slivers" if self.n_slivers > 1 else "1 triangle",
                                           size=22, color=MUTED, weight=MEDIUM)
                              .next_to(meter, DOWN, buff=0.35, aligned_edge=LEFT))
        self.n_slivers = 1
        self.add(count)
        self.wait_to(c.at("slicing") - 0.1)
        t_cut_end = c.after("slivers") + 0.2
        per = (t_cut_end - self.now) / 5
        for k in range(1, 6):
            n = 2 ** k
            xs = np.linspace(-TRI_W / 2, TRI_W / 2, n + 1) + TRI_CX
            cuts = VGroup(*[Line([xs[i], TRI_BASE_Y, 0], apex, stroke_color=BLUE, stroke_width=1.2, stroke_opacity=0.75)
                            for i in range(1, n, 2)])
            self.n_slivers = n
            self.play(LaggedStart(*[Create(l) for l in cuts], lag_ratio=0.05), run_time=per)
            self.add(cuts)
        # swap the drawing for 32 independent slivers
        self.k = 5
        self.xs = np.zeros(32)
        slivers = VGroup(*[sliver_mob(5, i, 0) for i in range(32)])
        self.clear_cuts_and(tri, slivers)
        self.slivers = slivers

        # ── 5. sliding ──────────────────────────────────────────────────────
        self.wait_to(c.at("sliding") - 0.15)
        self._slide_to(5, offsets(5, best_shifts(5)), run_time=c.after("another") + 0.2 - self.now)

        # thinner and thinner: 64, then 128 slivers
        self._split()
        self._slide_to(6, offsets(6, best_shifts(6)), run_time=0.9)
        self._split()
        self._slide_to(7, offsets(7, best_shifts(7)), run_time=0.9)
        to_zero = VGroup(sans("more slivers, smaller still", size=20, color=MUTED),
                         sans("→  0", size=26, color=BLUE, weight=MEDIUM)).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        to_zero.next_to(count, DOWN, buff=0.3, aligned_edge=LEFT)
        self.wait_to(c.at("zero") - 0.3)
        self.play(FadeIn(to_zero, shift=UP * 0.1), run_time=0.6)

        # the slivers still hold a needle in every direction of the slice
        picks = [0, 21, 42, 64, 85, 106, 127]
        needles = VGroup()
        for i in picks:
            p = sliver_pts(7, i, self.xs[i])
            base_mid = np.array([(p[0][0] + p[1][0]) / 2, p[0][1], 0])
            top = np.array([p[2][0], p[2][1], 0])
            needles.add(Line(base_mid, top, stroke_color=NEEDLE, stroke_width=3.5))
        self.play(LaggedStart(*[Create(n) for n in needles], lag_ratio=0.12), run_time=1.0)
        self.wait_to(c.dur - 0.55)
        self.play(*[FadeOut(m) for m in self.mobjects if not isinstance(m, NumberPlane)], run_time=0.5)
        self.finish()

    # ── helpers ──────────────────────────────────────────────────────────────
    def _chord_needle(self, t):
        mid, u = deltoid_chord(t)
        n = make_needle(length=L, angle=np.arctan2(u[1], u[0]))
        return n.shift(mid)

    def _area_bars(self):
        x0 = 2.5
        full = 2.6
        rows = VGroup()
        for lab, col, frac, y in (("disc", BLUE, 1.0, -2.55), ("deltoid", TEAL, 0.5, -3.15)):
            t = sans(lab, size=20, color=col, weight=MEDIUM).move_to([x0, y, 0], aligned_edge=LEFT)
            bar = Rectangle(width=full * frac, height=0.2, fill_color=col, fill_opacity=0.85, stroke_width=0)
            bar.move_to([x0 + 1.35, y, 0], aligned_edge=LEFT)
            rows.add(VGroup(t, bar))
        half = serif("half", size=24, color=TEAL, slant=ITALIC).next_to(rows[1][1], RIGHT, buff=0.2)
        return VGroup(rows[0], rows[1], half)

    def _meter(self):
        lab = eyebrow("area")
        track = RoundedRectangle(corner_radius=0.07, width=3.4, height=0.14, fill_color=FAINT, fill_opacity=1,
                                 stroke_width=0)
        g = VGroup(lab, track).arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_corner(UR, buff=0.8).shift(DOWN * 0.3)
        self.area_ratio = 1.0

        def fill():
            w = max(0.02, 3.4 * self.area_ratio)
            return RoundedRectangle(corner_radius=0.07, width=w, height=0.14, fill_color=BLUE, fill_opacity=1,
                                    stroke_width=0).move_to(track.get_left(), aligned_edge=LEFT)

        pct = always_redraw(lambda: sans(f"{round(self.area_ratio * 100)}%", size=26, color=INK, weight=MEDIUM)
                            .next_to(track, UP, buff=0.12).align_to(track, RIGHT))
        bar = always_redraw(fill)
        whole = VGroup(g, bar, pct)
        return whole

    def clear_cuts_and(self, tri, slivers):
        for m in list(self.mobjects):
            if isinstance(m, VGroup) and len(m) and all(isinstance(x, Line) for x in m):
                self.remove(m)
        self.remove(tri)
        self.add(slivers)

    def _slide_to(self, k, target, run_time):
        start = self.xs.copy()
        u = ValueTracker(0.0)
        n = 2 ** k

        def upd(group):
            a = smooth(u.get_value())
            cur = start + (target - start) * a
            self.xs = cur
            for i, m in enumerate(group):
                m.become(sliver_mob(k, i, cur[i]))
            self.area_ratio = union_ratio(k, cur)

        self.slivers.add_updater(upd)
        self.play(u.animate.set_value(1.0), run_time=max(0.3, run_time), rate_func=linear)
        self.slivers.remove_updater(upd)
        self.xs = np.array(target)

    def _split(self):
        """Each sliver splits in two in place (same union), ready for the next level's slide."""
        k = self.k + 1
        xs = np.repeat(self.xs, 2)
        new = VGroup(*[sliver_mob(k, i, xs[i]) for i in range(2 ** k)])
        self.remove(self.slivers)
        self.add(new)
        self.slivers, self.xs, self.k = new, xs, k
        self.n_slivers = 2 ** k
