"""c5_position: attention is blind to order (shuffle test, dog bites man), positional encoding added to each
word vector, the real sinusoidal PE matrix, clock hands at geometric speeds, and the shift-as-rotation property."""
from style import *

POS_HUE = TEAL          # colour of "position" throughout this section
D_MODEL = 512


# ── real data ──────────────────────────────────────────────────────────────────
def pe(pos, dims=D_MODEL):
    """Sinusoidal positional encoding exactly as in the paper (Section 3.5)."""
    pos = np.asarray(pos, dtype=float)[..., None]
    i = np.arange(dims // 2)
    ang = pos / (10000 ** (2 * i / D_MODEL))
    out = np.zeros(pos.shape[:-1] + (dims,))
    out[..., 0::2] = np.sin(ang)
    out[..., 1::2] = np.cos(ang)
    return out


def omega(i):
    return 1.0 / 10000 ** (2 * i / D_MODEL)


def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


WORDS = ["dog", "bites", "man"]
rng = np.random.default_rng(1)
DE = 16
EMB = rng.standard_normal((3, DE))
WQ, WK, WV = (rng.standard_normal((DE, DE)) / np.sqrt(DE) for _ in range(3))


def self_attention(X):
    Q, K, V = X @ WQ, X @ WK, X @ WV
    return softmax(Q @ K.T / np.sqrt(DE)) @ V


OUT = self_attention(EMB)                          # order: dog bites man
PERM = [2, 1, 0]                                   # shuffled: man bites dog
OUT_SHUF = self_attention(EMB[PERM])
assert np.allclose(OUT_SHUF, OUT[PERM])            # permutation-equivariant: same output per word
NB = 8                                             # output dims drawn per word
VMAX = np.abs(OUT[:, :NB]).max()


def mt(s, size=30, color=INK):
    return MarkupText(s, font=SERIF, font_size=size, color=color)


def bar_chart(vals, color=ORANGE, filled=True, bw=0.21, gap=0.055, hmax=0.78):
    """Small signed bar chart; bars hang from a baseline at y=0 of the group's frame."""
    g = VGroup()
    for k, v in enumerate(vals):
        h = max(0.02, abs(v) / VMAX * hmax)
        r = Rectangle(width=bw, height=h, stroke_color=color, stroke_width=1.2,
                      fill_color=color, fill_opacity=0.85 if filled else 0)
        r.move_to([k * (bw + gap), np.sign(v) * h / 2, 0])
        g.add(r)
    base = Line([-bw / 2 - 0.06, 0, 0], [(len(vals) - 1) * (bw + gap) + bw / 2 + 0.06, 0, 0],
                stroke_color=MUTED, stroke_width=1, stroke_opacity=0.6)
    return VGroup(base, g)


def div_color(v, pos=POS_HUE, neg=PURPLE, mid="#141821"):
    v = float(np.clip(v, -1, 1))
    return interpolate_color(ManimColor(mid), ManimColor(pos if v >= 0 else neg), abs(v) ** 0.9)


def neutral_color(v):
    v = float(np.clip(v, -1.5, 1.5)) / 1.5
    return interpolate_color(ManimColor("#20242d"), ManimColor(INK if v >= 0 else "#6E7787"), abs(v) ** 0.8)


def column(vals, colorf, cell=0.34):
    g = VGroup(*[Square(cell, stroke_width=1, stroke_color=BG, fill_color=colorf(v), fill_opacity=1) for v in vals])
    return g.arrange(DOWN, buff=0)


def equiv(color=NEEDLE, w=0.42):
    return VGroup(*[Line(LEFT * w / 2, RIGHT * w / 2, stroke_color=color, stroke_width=4) for _ in range(3)]) \
        .arrange(DOWN, buff=0.1)


class C5Position(BeatScene):
    BEAT = "c5_position"

    def construct(self):
        c = self.cues
        self.part_order(c)
        self.part_add(c)
        self.part_waves(c)
        self.part_rotation(c)
        self.finish()

    # ── A. attention has no notion of order ────────────────────────────────────
    def part_order(self, c):
        X = [-2.9, 0.0, 2.9]
        chip_y, base_y = 1.0, -1.15
        chips = [chip(w, color=INK, size=26) for w in WORDS]
        for ch, x in zip(chips, X):
            ch.move_to([x, chip_y, 0])
        slots = VGroup(*[sans(str(k), size=18, color=MUTED).move_to([x, chip_y - 0.62, 0])
                         for k, x in enumerate(X)])

        def arcs_for(xs):
            g = VGroup()
            top = chip_y + 0.33
            for a, b, ang in [(0, 1, -0.75), (1, 2, -0.75), (0, 2, -0.95)]:
                g.add(ArcBetweenPoints([xs[a], top, 0], [xs[b], top, 0], angle=ang,
                                       stroke_color=NEEDLE, stroke_width=2.4, stroke_opacity=0.75))
            return g

        arcs = arcs_for(X)
        charts = []
        for k, x in enumerate(X):
            ch = bar_chart(OUT[k, :NB])
            ch.move_to([x, base_y, 0], coor_mask=[1, 0, 0])
            ch.shift(UP * (base_y - ch[0].get_y()))
            charts.append(ch)
        out_lab = eyebrow("attention output", color=MUTED, size=14).move_to([0, base_y - 1.1, 0])

        words = [VGroup(chips[k], charts[k]) for k in range(3)]
        self.play(LaggedStart(*[FadeIn(ch, shift=UP * 0.12) for ch in chips], lag_ratio=0.25), run_time=1.1)
        self.play_from(c.at("so far") - 0.2, LaggedStart(*[FadeIn(s, shift=UP * 0.06) for s in slots],
                                                         lag_ratio=0.2), run_time=0.7)
        self.wait_to(c.at("attention compares"))
        self.play_until(c.after("every other word") - 0.5, LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.3))
        self.play(*[GrowFromEdge(ch[1], UP) for ch in charts], *[FadeIn(ch[0]) for ch in charts],
                  FadeIn(out_lab), run_time=0.7)

        # "knows the order": the slot numbers become question marks
        qs = VGroup(*[sans("?", size=20, color=MUTED).move_to(s) for s in slots])
        self.play_from(c.at("knows the order"), *[Transform(s, q) for s, q in zip(slots, qs)], run_time=0.6)

        # keep a copy of the original arrangement for the side-by-side later
        original = VGroup(*[w.copy() for w in words], arcs.copy())

        # shuffle: dog and man swap places (dog over the top, man underneath); outputs become outlines
        self.wait_to(c.at("shuffle"))
        self.play(FadeOut(arcs), run_time=0.25)
        for ch in charts:
            ch[1].generate_target()
            ch[1].target.set_fill(opacity=0).set_stroke(ORANGE, 1.4, 0.8)
        self.play(slots.animate.set_opacity(0), run_time=0.2)
        self.play(words[0].animate(path_arc=-0.7 * PI).shift(RIGHT * (X[2] - X[0])),
                  words[2].animate(path_arc=-0.7 * PI).shift(LEFT * (X[2] - X[0])),
                  *[MoveToTarget(ch[1]) for ch in charts], run_time=1.1, rate_func=rate_functions.ease_in_out_cubic)
        # recompute attention on the shuffled sentence and fill each outline with the new output
        new_x = [X[2], X[1], X[0]]                          # man, bites, dog slots after the swap
        arcs2 = arcs_for(X)
        fills = []
        for slot, w in enumerate(PERM):                     # slot 0 now holds WORDS[PERM[0]] = man, etc.
            f = bar_chart(OUT_SHUF[slot, :NB])[1]
            f.move_to(charts[w][1])
            fills.append(f)
        self.play(Create(arcs2), slots.animate.set_opacity(1), run_time=0.6)
        self.wait_to(c.at("exactly the same") - 0.2)
        self.play(*[LaggedStart(*[GrowFromEdge(b, UP if b.get_y() < charts[0][0].get_y() else DOWN)
                                  for b in f], lag_ratio=0.06) for f in fills], run_time=0.9)
        self.play_until(c.after("weighted average"),
                        *[ch[1].animate.set_stroke(NEEDLE, 2.2, 1) for ch in charts], min_time=0.4)
        self.play(*[ch[1].animate.set_stroke(ORANGE, 1.4, 0.8) for ch in charts], run_time=0.4)

        # side by side: dog bites man ≡ man bites dog
        shuffled = VGroup(*[VGroup(chips[k], charts[k][0], charts[k][1], fills[k_slot])
                            for k_slot, k in enumerate(PERM)], arcs2)
        sc = 0.72
        self.wait_to(c.at("so dog") - 0.1)
        self.play(FadeOut(slots), FadeOut(out_lab),
                  shuffled.animate.scale(sc).move_to([3.55, 0.25, 0]), run_time=0.7)
        original.scale(sc).move_to([-3.55, 0.25, 0])
        self.play_from(c.at("dog bites man"), FadeIn(original, shift=RIGHT * 0.2), run_time=0.6)
        eq = equiv().move_to([0, 0.3, 0])
        eq_lab = sans("to attention", size=18, color=MUTED).next_to(eq, DOWN, buff=0.3)
        self.play_from(c.at("look identical"), GrowFromCenter(eq), FadeIn(eq_lab, shift=UP * 0.06), run_time=0.6)
        self.wait_to(c.at("the fix") - 0.05)
        self.play(FadeOut(VGroup(original, shuffled, eq, eq_lab)), run_time=0.5)

    # ── B. add a position signal to each word vector ─────────────────────────────
    def part_add(self, c):
        X = [-3.6, 0.0, 3.6]
        chips = VGroup(*[chip(w, color=INK, size=24).move_to([x, 2.95, 0]) for w, x in zip(WORDS, X)])
        emb = [column(np.clip(EMB[k, :8] * 0.75, -1.5, 1.5), neutral_color).move_to([x - 0.55, 0.42, 0])
               for k, x in enumerate(X)]
        P = pe(np.arange(3))[:, :8]
        pcols = [column(P[k], div_color).move_to([x + 0.55, 0.42, 0]) for k, x in enumerate(X)]
        plus = [mt("+", 34, MUTED).move_to([x, 0.42, 0]) for x in X]
        plab = [sans(f"pos {k}", size=17, color=POS_HUE).next_to(pcols[k], UP, buff=0.14) for k in range(3)]
        wlab = sans("word", size=15, color=MUTED).next_to(emb[0], DOWN, buff=0.14)
        plab2 = sans("position", size=15, color=POS_HUE).next_to(pcols[0], DOWN, buff=0.14)

        self.play(LaggedStart(*[FadeIn(ch, shift=DOWN * 0.1) for ch in chips], lag_ratio=0.12),
                  LaggedStart(*[LaggedStart(*[FadeIn(s) for s in col], lag_ratio=0.05) for col in emb],
                              lag_ratio=0.15), FadeIn(wlab), run_time=0.8)
        self.wait_to(c.at("a signal"))
        self.play_until(c.after("encodes position"),
                        LaggedStart(*[AnimationGroup(FadeIn(p), GrowFromEdge(col, UP), FadeIn(l, shift=DOWN * 0.05))
                                      for p, col, l in zip(plus, pcols, plab)], lag_ratio=0.25),
                        FadeIn(plab2), min_time=0.8)

        # merge: the position column slides onto the word column, the cells take the summed values
        sums = [column(np.clip(EMB[k, :8] * 0.75 + P[k], -1.5, 1.5), neutral_color).move_to(emb[k])
                for k in range(3)]
        for s in sums:
            for sq in s:
                sq.set_stroke(POS_HUE, 1.2, 0.9)
        self.wait_to(c.at("to each") - 0.1)
        self.play(*[pcols[k].animate.move_to(emb[k]).set_opacity(0) for k in range(3)],
                  *[FadeOut(p) for p in plus], FadeOut(wlab), FadeOut(plab2), run_time=0.7,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.play(*[Transform(emb[k], sums[k]) for k in range(3)],
                  *[plab[k].animate.next_to(sums[k], UP, buff=0.14) for k in range(3)], run_time=0.5)
        self.remove(*pcols)

        # then everything else (attention) happens
        box = RoundedRectangle(corner_radius=0.12, width=9.2, height=0.62, stroke_color=NEEDLE, stroke_width=1.6,
                               fill_color=NEEDLE, fill_opacity=0.06).move_to([0, -1.85, 0])
        box_lab = sans("attention", size=22, color=NEEDLE).move_to(box)
        arrows = VGroup(*[Arrow(emb[k].get_bottom(), [emb[k].get_x(), box.get_top()[1], 0], buff=0.08,
                                stroke_width=2.2, color=MUTED, tip_length=0.14) for k in range(3)])
        self.play_from(c.at("before anything"), LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.1),
                       FadeIn(box), FadeIn(box_lab), run_time=0.8)
        self.wait_to(c.at("the authors used") - 0.75)
        self.play(FadeOut(VGroup(chips, *emb, *plab, box, box_lab, arrows)), run_time=0.55)

    # ── C/D. the real PE matrix, its waves, and the clock hands ───────────────────
    def part_waves(self, c):
        NPOS, NDIM = 51, 128
        M = pe(np.arange(NPOS))[:, :NDIM].T                # rows: dimension, cols: position
        rgb = np.array([[np.array(div_color(v).to_rgb()) for v in row] for row in M])
        ax_, ay_ = 20, 6
        full = np.concatenate([(rgb * 255).astype(np.uint8), np.full((NDIM, NPOS, 1), 255, np.uint8)], axis=2)
        full = np.repeat(np.repeat(full, ay_, axis=0), ax_, axis=1)
        W_, H_ = 5.5, 4.15
        img = ImageMobject(full.copy()).set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        img.width = W_
        img.stretch_to_fit_height(H_)
        img.move_to([-3.75, -0.05, 0])
        img.pixel_array[:, :, 3] = 0
        frame = Rectangle(width=W_, height=H_, stroke_color=MUTED, stroke_width=1, stroke_opacity=0.6).move_to(img)
        L, R, T, B = img.get_left()[0], img.get_right()[0], img.get_top()[1], img.get_bottom()[1]
        cw = W_ / NPOS

        def col_x(p):
            return L + (p + 0.5) * cw

        def row_y(d):
            return T - (d + 0.5) * H_ / NDIM

        x_lab = VGroup(sans("0", size=15, color=MUTED).move_to([col_x(0), B - 0.22, 0]),
                       sans("50", size=15, color=MUTED).move_to([col_x(50), B - 0.22, 0]),
                       sans("position", size=16, color=MUTED).move_to([(L + R) / 2, B - 0.24, 0]))
        y_lab = VGroup(sans("0", size=15, color=MUTED).next_to([L, row_y(0), 0], LEFT, buff=0.12),
                       sans("127", size=15, color=MUTED).next_to([L, row_y(127), 0], LEFT, buff=0.12),
                       sans("dimension", size=16, color=MUTED).rotate(PI / 2).move_to([L - 0.32, (T + B) / 2, 0]))
        formula = mt('PE<sub>(<i>pos</i>, 2<i>i</i>)</sub> = sin(<i>pos</i> / 10000<sup>2<i>i</i> / <i>d</i>'
                     '<sub>model</sub></sup>)', 28, INK).move_to([0, 3.15, 0])

        self.play(FadeIn(frame), FadeIn(x_lab), FadeIn(y_lab), FadeIn(formula, shift=DOWN * 0.1), run_time=0.7)

        # build the matrix position by position (columns), with a scanning edge
        reveal = ValueTracker(0.0)
        scan = Line([L, T, 0], [L, B, 0], stroke_color=POS_HUE, stroke_width=2, stroke_opacity=0.9)

        def upd_img(m):
            k = int(round(reveal.get_value() * NPOS * ax_))
            m.pixel_array[:, :k, 3] = 255
            m.pixel_array[:, k:, 3] = 0

        img.add_updater(upd_img)
        scan.add_updater(lambda m: m.set_x(L + reveal.get_value() * W_))
        self.add(img, scan, frame)
        self.play(reveal.animate.set_value(1.0), run_time=c.at("very fast") - 0.3 - self.now,
                  rate_func=rate_functions.ease_in_out_sine)
        img.clear_updaters()
        img.pixel_array[:] = full
        self.play(FadeOut(scan), run_time=0.3)
        self.remove(scan)

        # individual waves, fast → slow, each tied to its row in the matrix
        I_SEL = [0, 12, 36, 60]                            # pair index i; the drawn row is dimension 2i (sine)
        cols = [interpolate_color(ManimColor(POS_HUE), ManimColor(PURPLE), t) for t in np.linspace(0, 1, 4)]
        cx0, cx1 = 0.55, 6.45
        ys = [1.75, 0.6, -0.55, -1.7]
        amp = 0.36

        def wx(p):
            return cx0 + p / 50 * (cx1 - cx0)

        curves, ticks, labs, bases = [], [], [], []
        for i, col, y in zip(I_SEL, cols, ys):
            w = omega(i)
            curves.append(ParametricFunction(lambda t, w=w, y=y: np.array([wx(t), y + amp * np.sin(w * t), 0]),
                                             t_range=[0, 50, 0.05], stroke_color=col, stroke_width=3))
            bases.append(Line([cx0, y, 0], [cx1, y, 0], stroke_color=FAINT, stroke_width=1))
            ticks.append(Line([R + 0.04, row_y(2 * i), 0], [R + 0.22, row_y(2 * i), 0], stroke_color=col,
                              stroke_width=3))
            labs.append(sans(f"dim {2 * i}", size=15, color=col).move_to([cx0, y + amp + 0.2, 0], aligned_edge=LEFT))
        self.wait_to(c.at("very fast") - 0.3)
        self.play_until(c.after("very slow") + 0.1,
                        LaggedStart(*[AnimationGroup(FadeIn(b), Create(cv), FadeIn(t), FadeIn(lb))
                                      for b, cv, t, lb in zip(bases, curves, ticks, labs)], lag_ratio=0.35))

        # every position gets its own pattern: a gold column in the matrix, a cursor across the waves
        pos = ValueTracker(6)
        colbox = always_redraw(lambda: Rectangle(width=cw, height=H_ + 0.08, stroke_color=NEEDLE, stroke_width=2.2)
                               .move_to([col_x(pos.get_value()), (T + B) / 2, 0]))
        cursor = always_redraw(lambda: Line([wx(pos.get_value()), ys[0] + 0.62, 0],
                                            [wx(pos.get_value()), ys[-1] - 0.5, 0],
                                            stroke_color=NEEDLE, stroke_width=1.6, stroke_opacity=0.8))
        dots = always_redraw(lambda: VGroup(*[
            Dot([wx(pos.get_value()), y + amp * np.sin(omega(i) * pos.get_value()), 0], radius=0.055, color=NEEDLE)
            for i, y in zip(I_SEL, ys)]))
        self.play_from(c.at("every position"), FadeIn(colbox), FadeIn(cursor), FadeIn(dots), run_time=0.45)
        self.play(pos.animate.set_value(19), run_time=0.9, rate_func=rate_functions.ease_in_out_cubic)
        self.wait(0.15)
        self.play_until(c.after("distinctive pattern"), pos.animate.set_value(37),
                        rate_func=rate_functions.ease_in_out_cubic, min_time=0.7)

        # clock with many hands: one dial per (sin, cos) pair; hand tip = (sin ωpos, cos ωpos)
        waves = VGroup(*curves, *bases, *ticks, *labs)
        self.wait_to(c.at("rather like") - 0.2)
        self.play(FadeOut(waves), FadeOut(cursor), FadeOut(dots), pos.animate.set_value(0), run_time=0.6)
        self.remove(cursor, dots)
        D_SEL = [0, 12, 24, 36, 48, 60]                    # evenly spaced i → geometric speeds
        dcols = [interpolate_color(ManimColor(POS_HUE), ManimColor(PURPLE), t) for t in np.linspace(0, 1, 6)]
        rad = 0.62
        centers = [np.array([1.65 + (k % 3) * 1.85, 0.95 - (k // 3) * 2.05, 0]) for k in range(6)]
        faces = VGroup()
        for k, ctr in enumerate(centers):
            face = VGroup(Circle(rad, stroke_color=MUTED, stroke_width=1.3, fill_color="#12151c", fill_opacity=1),
                          *[Line(ctr + rad * 0.82 * np.array([np.sin(a), np.cos(a), 0]),
                                 ctr + rad * 0.95 * np.array([np.sin(a), np.cos(a), 0]),
                                 stroke_color=MUTED, stroke_width=1.2) for a in np.arange(12) * TAU / 12])
            face[0].move_to(ctr)
            faces.add(face)
            faces.add(sans(f"i = {D_SEL[k]}", size=15, color=dcols[k]).next_to(face[0], DOWN, buff=0.14))

        def hands():
            g = VGroup()
            for k, ctr in enumerate(centers):
                th = omega(D_SEL[k]) * pos.get_value()
                tip = ctr + rad * 0.78 * np.array([np.sin(th), np.cos(th), 0])
                g.add(Line(ctr, tip, stroke_color=dcols[k], stroke_width=4).set_cap_style(CapStyleType.ROUND),
                      Dot(ctr, radius=0.05, color=dcols[k]))
            return g

        hand_g = always_redraw(hands)
        pos_lab = always_redraw(lambda: mt(f"<i>pos</i> = {int(round(pos.get_value()))}", 26, NEEDLE)
                                .move_to([centers[1][0], 2.25, 0]))
        self.play(FadeIn(faces), FadeIn(hand_g), FadeIn(pos_lab), run_time=0.6)
        self.play_until(c.after("different speeds") + 0.6, pos.animate.set_value(24), rate_func=linear)
        self.play_from(c.at("this choice") - 0.1,
                       FadeOut(Group(img, frame, x_lab, y_lab, formula, colbox, faces, hand_g, pos_lab)),
                       run_time=0.7)
        self.remove(colbox, hand_g, pos_lab)

    # ── E. a fixed shift is a fixed rotation (a linear map) ────────────────────────
    def part_rotation(self, c):
        I, K = 12, 3
        w = omega(I)
        ctr, r = np.array([-3.1, -0.05, 0]), 1.85
        circ = Circle(r, stroke_color=MUTED, stroke_width=1.4).move_to(ctr)
        axes = VGroup(Line(ctr + LEFT * (r + 0.35), ctr + RIGHT * (r + 0.35)),
                      Line(ctr + DOWN * (r + 0.35), ctr + UP * (r + 0.35))).set_stroke(FAINT, 1.4)
        ax_s = mt(f"sin(ω<i>pos</i>)", 20, MUTED).next_to(ctr + RIGHT * (r + 0.35), RIGHT, buff=0.12)
        ax_c = mt(f"cos(ω<i>pos</i>)", 20, MUTED).next_to(ctr + UP * (r + 0.35), RIGHT, buff=0.12)
        p = ValueTracker(1.0)

        def pt(theta):
            return ctr + r * np.array([np.sin(theta), np.cos(theta), 0])

        h1 = always_redraw(lambda: VGroup(Line(ctr, pt(w * p.get_value()), stroke_color=POS_HUE, stroke_width=4),
                                          Dot(pt(w * p.get_value()), radius=0.08, color=POS_HUE)))
        h2 = always_redraw(lambda: VGroup(
            Line(ctr, pt(w * (p.get_value() + K)), stroke_color=NEEDLE, stroke_width=4),
            Dot(pt(w * (p.get_value() + K)), radius=0.08, color=NEEDLE)))
        arc = always_redraw(lambda: Arc(radius=r * 0.42, start_angle=PI / 2 - w * p.get_value(), angle=-w * K,
                                        arc_center=ctr, stroke_color=NEEDLE, stroke_width=3))
        arc_lab = always_redraw(lambda: mt("<i>k</i>ω", 24, NEEDLE).move_to(
            ctr + r * 0.6 * np.array([np.sin(w * (p.get_value() + K / 2)), np.cos(w * (p.get_value() + K / 2)), 0])))
        def outside(m, theta):
            d = np.array([np.sin(theta), np.cos(theta), 0])
            return m.move_to(ctr + d * (r + 0.2 + 0.5 * (abs(d[0]) * m.width + abs(d[1]) * m.height)))

        l1 = always_redraw(lambda: outside(mt("<i>pos</i>", 22, POS_HUE), w * p.get_value()))
        l2 = always_redraw(lambda: outside(mt("<i>pos</i> + <i>k</i>", 22, NEEDLE), w * (p.get_value() + K)))
        dot0 = Dot(ctr, radius=0.05, color=INK)

        self.play(Create(circ), FadeIn(axes), FadeIn(ax_s), FadeIn(ax_c), FadeIn(dot0), run_time=0.8)
        self.play(FadeIn(h1), FadeIn(l1), run_time=0.5)
        self.play_from(c.at("moving a fixed distance"), FadeIn(h2), FadeIn(l2), run_time=0.6)
        self.play_until(c.after("distance"), Create(arc), FadeIn(arc_lab), min_time=0.5)

        # right side: the shift as a 2×2 rotation matrix (same matrix for every pos)
        head = mt("<i>pos</i>  →  <i>pos</i> + <i>k</i>", 30, INK).move_to([3.35, 2.25, 0])
        entries = [["cos <i>k</i>ω", "sin <i>k</i>ω"], ["−sin <i>k</i>ω", "cos <i>k</i>ω"]]
        cells = VGroup()
        for a in range(2):
            for b in range(2):
                box = Rectangle(width=1.55, height=0.72, stroke_color=FAINT, stroke_width=1.2,
                                fill_color=NEEDLE, fill_opacity=0.05).move_to([2.6 + b * 1.55, 0.75 - a * 0.72, 0])
                cells.add(VGroup(box, mt(entries[a][b], 24, INK).move_to(box)))
        brl = VGroup(Line(UP, DOWN), Line(UP, UP + RIGHT * 0.12), Line(DOWN, DOWN + RIGHT * 0.12))
        brl.set_stroke(INK, 2).scale_to_fit_height(1.62).next_to(cells, LEFT, buff=0.1)
        brr = brl.copy().flip(UP).next_to(cells, RIGHT, buff=0.1)
        mat = VGroup(cells, brl, brr).move_to([3.35, 0.4, 0])
        rot_lab = mt("rotation by <i>k</i>ω", 28, NEEDLE).next_to(mat, DOWN, buff=0.45)
        self.play_from(c.at("corresponds to") - 0.1, FadeIn(head, shift=DOWN * 0.08), run_time=0.6)
        self.play_until(c.after("linear transformation"),
                        LaggedStart(Create(brl), Create(brr), *[FadeIn(cl, scale=0.9) for cl in cells],
                                    lag_ratio=0.12), min_time=0.8)
        self.play(FadeIn(rot_lab, shift=UP * 0.08), run_time=0.5)

        # relative positions: slide pos along; the pair rotates rigidly, the angle kω never changes
        self.wait_to(c.at("which makes"))
        self.play_until(c.after("easy for the model") + 0.3, p.animate.set_value(5.5),
                        rate_func=rate_functions.ease_in_out_sine)
        self.wait_to(c.dur - 0.55)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
