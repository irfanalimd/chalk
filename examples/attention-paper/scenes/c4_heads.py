"""c4_heads: multi-head attention. One pattern -> eight heads in 64-dim subspaces -> Concat -> Linear,
the equal-cost balance, and the paper's own evidence (Figure 5, then Figure 4's anaphora heads)."""
import colorsys

from style import *

# ── data: real computations on seeded random vectors ─────────────────────────────
TOKENS = ["The", "Law", "will", "never", "be", "perfect"]
N, D, H = len(TOKENS), 512, 8
DK = D // H
GAIN = 1.45  # scales the random embeddings so softmax patterns are visibly distinct


def softmax(s):
    e = np.exp(s - s.max(axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)


rng = np.random.default_rng(17)
X = rng.standard_normal((N, D)) * GAIN
# one full-width head
Wq1, Wk1 = (rng.standard_normal((D, D)) / np.sqrt(D) for _ in range(2))
A_SINGLE = softmax((X @ Wq1) @ (X @ Wk1).T / np.sqrt(D))
# eight heads: one projection each for Q, K, V into a 64-dim subspace
WQ = rng.standard_normal((H, D, DK)) / np.sqrt(D)
WK = rng.standard_normal((H, D, DK)) / np.sqrt(D)
WV = rng.standard_normal((H, D, DK)) / np.sqrt(D)
WO = rng.standard_normal((D, D)) / np.sqrt(D)
Qh = np.einsum("nd,hdk->hnk", X, WQ)
Kh = np.einsum("nd,hdk->hnk", X, WK)
Vh = np.einsum("nd,hdk->hnk", X, WV)
A_HEADS = softmax(Qh @ Kh.transpose(0, 2, 1) / np.sqrt(DK))          # (8, n, n)
HEAD_OUT = A_HEADS @ Vh                                             # (8, n, 64)
ROW = 1                                                              # follow the word "Law"
CONCAT = np.concatenate([HEAD_OUT[h, ROW] for h in range(H)])       # 512
OUT = CONCAT @ WO                                                    # 512
Q_FULL = np.concatenate([Qh[h, ROW] for h in range(H)])             # projected q, k, v of "Law"
K_FULL = np.concatenate([Kh[h, ROW] for h in range(H)])
V_FULL = np.concatenate([Vh[h, ROW] for h in range(H)])


def hue(i, n=H):
    r, g, b = colorsys.hls_to_rgb(((0.98 + i / n) % 1.0), 0.68, 0.66)
    return ManimColor.from_rgb((r, g, b))


HUES = [hue(i) for i in range(H)]

# ── layout ──────────────────────────────────────────────────────────────────────
SLOT, PITCH = 1.2, 1.49
SLOT_Y = 1.75
SLOT_X = [(i - 3.5) * PITCH for i in range(H)]
CELLS_PER_SLICE = 8                    # one drawn cell = 8 dimensions
CELL_W = SLOT / CELLS_PER_SLICE
BAR_H = 0.24


def mt(s, size=30, color=INK):
    """Math via Pango markup (no LaTeX): <i>, <sub>, <sup>."""
    return MarkupText(s, font=SERIF, font_size=size, color=color)


def block_means(v, n_cells):
    return v.reshape(n_cells, -1).mean(axis=1)


def vec_cells(values, color, cell_w=CELL_W, h=BAR_H, vmax=None):
    """A row of cells; opacity follows |value| (computed numbers, not decoration)."""
    vmax = vmax or np.abs(values).max()
    g = VGroup()
    for v in values:
        a = 0.12 + 0.88 * min(1.0, abs(v) / vmax)
        g.add(Rectangle(width=cell_w, height=h, stroke_width=0.6, stroke_color=BG,
                        fill_color=color, fill_opacity=a))
    return g.arrange(RIGHT, buff=0)


def heatmap(W, size, color, stroke=None):
    n = W.shape[0]
    c = size / n
    cells = VGroup()
    m = W.max()
    for i in range(n):
        for j in range(n):
            a = 0.05 + 0.95 * (W[i, j] / m) ** 0.85
            cells.add(Square(c, stroke_width=0.8, stroke_color=BG, fill_color=color, fill_opacity=a)
                      .move_to([(j - (n - 1) / 2) * c, ((n - 1) / 2 - i) * c, 0]))
    frame = Square(size, stroke_color=stroke or color, stroke_width=1.6, stroke_opacity=0.9, fill_opacity=0)
    return VGroup(cells, frame)


def pdf_map(card_img, rect, px, py):
    x0, y0, x1, y1 = rect
    w, h = card_img.width, card_img.height
    c = card_img.get_center()
    return np.array([c[0] - w / 2 + (px - x0) / (x1 - x0) * w, c[1] + h / 2 - (py - y0) / (y1 - y0) * h, 0])


class C4Heads(BeatScene):
    BEAT = "c4_heads"

    def construct(self):
        c = self.cues

        # ── 1. one head, one pattern ────────────────────────────────────────────
        big = heatmap(A_SINGLE, 3.6, NEEDLE).move_to(RIGHT * 0.35 + DOWN * 0.25)
        cell = 3.6 / N
        rows = VGroup(*[sans(t, size=20, color=BLUE).set_opacity(0.95) for t in TOKENS])
        for i, r in enumerate(rows):
            r.move_to(big[0][i * N].get_center()).next_to(big, LEFT, buff=0.22, coor_mask=[1, 0, 0])
        cols = VGroup()
        for j, t in enumerate(TOKENS):
            lab = sans(t, size=20, color=GREEN).rotate(PI / 4)
            lab.move_to(big[0][j].get_top() + UP * 0.12, aligned_edge=DL).shift(LEFT * 0.12)
            cols.add(lab)
        q_ax = eyebrow("queries", color=BLUE, size=14).rotate(PI / 2).next_to(rows, LEFT, buff=0.28)
        k_ax = eyebrow("keys", color=GREEN, size=14).next_to(cols, UP, buff=0.22)
        kicker = eyebrow("One attention pattern", color=MUTED).to_edge(UP, buff=0.55)
        # strongest key for each query: the single relationship this pattern captures
        best = VGroup(*[Square(cell, stroke_color=WHITE, stroke_width=2.4, fill_opacity=0)
                        .move_to(big[0][i * N + int(A_SINGLE[i].argmax())]) for i in range(N)])

        self.play(FadeIn(big[1]), FadeIn(kicker, shift=DOWN * 0.08),
                  LaggedStart(*[FadeIn(s, scale=0.6) for s in big[0]], lag_ratio=0.02),
                  run_time=1.3)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in rows], lag_ratio=0.08),
                  LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in cols], lag_ratio=0.08),
                  FadeIn(q_ax), FadeIn(k_ax), run_time=0.9)
        self.play_until(c.after("one kind of relationship"),
                        LaggedStart(*[Create(b) for b in best], lag_ratio=0.15))

        # ── 2. "run several side by side": one pattern becomes eight empty slots ────
        slots = VGroup(*[Square(SLOT, stroke_color=HUES[i], stroke_width=1.6, stroke_opacity=0.9)
                         .move_to([SLOT_X[i], SLOT_Y, 0]) for i in range(H)])
        self.wait_to(c.at("so the authors"))
        self.play(FadeOut(VGroup(rows, cols, q_ax, k_ax, best, kicker)), FadeOut(big[0], scale=0.9), run_time=0.6)
        self.play_until(c.after("side by side", 1), ReplacementTransform(big[1], slots),
                        rate_func=rate_functions.ease_in_out_cubic, min_time=1.0)

        # ── 3. Q, K, V of width 512 split into eight 64-dim subspaces ──────────────
        roles = [("Q", Q_FULL, BLUE, "queries"), ("K", K_FULL, GREEN, "keys"), ("V", V_FULL, ORANGE, "values")]
        bar_y = [-0.2, -0.56, -0.92]
        bars, tags = VGroup(), VGroup()
        for (name, vec, col, _), y in zip(roles, bar_y):
            cells = block_means(vec, H * CELLS_PER_SLICE)
            vm = np.abs(cells).max()
            b = VGroup(*[vec_cells(cells[h * 8:(h + 1) * 8], col, vmax=vm) for h in range(H)])
            b.arrange(RIGHT, buff=0).move_to([0, y, 0])
            bars.add(b)
            tags.add(mt(f"<i>{name}</i>", 26, col).move_to([-5.45, y, 0]))
        dm_rule = VGroup(Line(LEFT * 4.8, RIGHT * 4.8, stroke_color=MUTED, stroke_width=1.2),
                         Line(UP * 0.07, DOWN * 0.07, stroke_color=MUTED, stroke_width=1.2).move_to(LEFT * 4.8),
                         Line(UP * 0.07, DOWN * 0.07, stroke_color=MUTED, stroke_width=1.2).move_to(RIGHT * 4.8)
                         ).move_to(UP * 0.2)
        dm = mt("<i>d</i><sub>model</sub> = 512", 26, INK).next_to(dm_rule, UP, buff=0.1)
        for (name, _, _, word), b, t in zip(roles, bars, tags):
            self.play_from(c.at(word), GrowFromEdge(b, LEFT), FadeIn(t, shift=RIGHT * 0.1),
                           *([FadeIn(dm_rule), FadeIn(dm, shift=DOWN * 0.08)] if name == "Q" else []),
                           run_time=0.5)

        # split into 8 slices, each sliding under its own slot
        self.wait_to(c.at("eight smaller subspaces"))
        moves = []
        for b in bars:
            for h in range(H):
                moves.append(b[h].animate.move_to([SLOT_X[h], b.get_y(), 0]))
        self.play(*moves, FadeOut(dm_rule), FadeOut(dm),
                  *[t.animate.move_to([-6.35, t.get_y(), 0]) for t in tags], run_time=0.9)
        br_l, br_r = SLOT_X[0] - SLOT / 2, SLOT_X[0] + SLOT / 2
        dk_rule = VGroup(Line([br_l, 0, 0], [br_r, 0, 0]), Line([br_l, 0.07, 0], [br_l, -0.07, 0]),
                         Line([br_r, 0.07, 0], [br_r, -0.07, 0])).set_stroke(HUES[0], 1.4).move_to(
            [SLOT_X[0], -1.2, 0])
        dk = mt("<i>d</i><sub><i>k</i></sub> = 64", 24, INK).next_to(dk_rule, DOWN, buff=0.1)
        hh = mt("<i>h</i> = 8", 24, INK).move_to([0, dk.get_y(), 0])
        self.play(Create(dk_rule), FadeIn(dk, shift=UP * 0.06), FadeIn(hh, shift=UP * 0.06), run_time=0.55)

        # ── 4. attention runs separately in each subspace ──────────────────────────
        heads = VGroup(*[heatmap(A_HEADS[h], SLOT, HUES[h])[0].move_to(slots[h]) for h in range(H)])
        self.wait_to(c.at("run attention separately"))
        flows, trios = [], []
        for h in range(H):
            trio = VGroup(*[bars[r][h].copy() for r in range(3)])
            trios.append(trio)
            flows.append(Succession(
                trio.animate(run_time=0.55, rate_func=rate_functions.ease_in_cubic)
                .scale(0.5).move_to(slots[h]).set_opacity(0),
                LaggedStart(*[FadeIn(s, scale=0.5) for s in heads[h]], lag_ratio=0.02, run_time=0.6)))
        self.play_until(c.after("in each"), LaggedStart(*flows, lag_ratio=0.09), min_time=1.4)
        self.remove(*trios)

        # ── 5. join (Concat) and project back to full size (Linear) ──────────────
        outs = VGroup(*[vec_cells(block_means(HEAD_OUT[h, ROW], 8), HUES[h],
                                  vmax=np.abs(block_means(HEAD_OUT[:, ROW].ravel(), 64)).max())
                        .move_to([SLOT_X[h], SLOT_Y - SLOT / 2 - 0.3, 0]) for h in range(H)])
        cat_y = -0.45
        self.wait_to(c.at("then join"))
        self.play(FadeOut(bars), FadeOut(tags), FadeOut(dk_rule), FadeOut(dk), FadeOut(hh),
                  LaggedStart(*[FadeIn(o, shift=DOWN * 0.15) for o in outs], lag_ratio=0.05), run_time=0.45)
        self.play(*[o.animate.move_to([(h - 3.5) * SLOT, cat_y, 0]) for h, o in enumerate(outs)],
                  run_time=0.65, rate_func=rate_functions.ease_in_out_cubic)
        cat_box = SurroundingRectangle(outs, buff=0.1, corner_radius=0.08, stroke_color=MUTED, stroke_width=1.3)
        cat_lab = sans("Concat", size=20, color=MUTED).next_to(cat_box, LEFT, buff=0.25)
        lin_box = RoundedRectangle(corner_radius=0.1, width=2.3, height=0.56, stroke_color=INK, stroke_width=1.5,
                                   fill_color=INK, fill_opacity=0.06).move_to([0, -1.4, 0])
        lin_lab = sans("Linear", size=21, color=INK).move_to(lin_box)
        a1 = Arrow(cat_box.get_bottom(), lin_box.get_top(), buff=0.04, stroke_width=2.2, color=MUTED,
                   max_tip_length_to_length_ratio=0.35, tip_length=0.14)
        final = vec_cells(block_means(OUT, 64), INK, cell_w=SLOT * H / 64, h=BAR_H).move_to([0, -2.32, 0])
        a2 = Arrow(lin_box.get_bottom(), final.get_top(), buff=0.04, stroke_width=2.2, color=MUTED,
                   max_tip_length_to_length_ratio=0.35, tip_length=0.14)
        out_lab = mt("512", 22, MUTED).next_to(final, RIGHT, buff=0.25)
        self.play(Create(cat_box), FadeIn(cat_lab, shift=RIGHT * 0.1), run_time=0.4)
        self.play_from(c.at("project them back"), GrowArrow(a1), FadeIn(lin_box), FadeIn(lin_lab), run_time=0.5)
        self.play_until(c.after("full size"), GrowArrow(a2), GrowFromEdge(final, LEFT), FadeIn(out_lab),
                        min_time=0.6)

        # ── 6. "each of these is called a head" ──────────────────────────────────
        head_labs = VGroup(*[sans(f"head {h + 1}", size=17, color=HUES[h]).next_to(slots[h], UP, buff=0.14)
                             for h in range(H)])
        self.wait_to(c.at("each of these"))
        self.play_until(c.after("called a head"),
                        LaggedStart(*[FadeIn(l, shift=DOWN * 0.08) for l in head_labs], lag_ratio=0.08),
                        LaggedStart(*[Indicate(s, scale_factor=1.06, color=HUES[i]) for i, s in enumerate(slots)],
                                    lag_ratio=0.08), min_time=1.0)

        # ── 7. eight thin heads cost about as much as one wide one ────────────────
        diagram = VGroup(slots, heads, head_labs, outs, cat_box, cat_lab, a1, lin_box, lin_lab, a2, final, out_lab)
        self.wait_to(c.at("and because"))
        self.play(FadeOut(diagram, shift=UP * 0.15), run_time=0.6)

        pivot = np.array([0, -0.9, 0])
        fulcrum = Polygon(pivot + DOWN * 0.04, pivot + DOWN * 0.95 + LEFT * 0.5, pivot + DOWN * 0.95 + RIGHT * 0.5,
                          stroke_color=MUTED, stroke_width=1.5, fill_color=FAINT, fill_opacity=1)
        base = Line(pivot + DOWN * 0.95 + LEFT * 1.2, pivot + DOWN * 0.95 + RIGHT * 1.2, stroke_color=MUTED,
                    stroke_width=1.5)
        beam = Line(pivot + LEFT * 4.4, pivot + RIGHT * 4.4, stroke_color=INK, stroke_width=3.5)
        pin = Dot(pivot, radius=0.06, color=INK)
        # equal area: width = dimensions, height = n² (same for both sides)
        tw, th = 0.26, 1.9
        thin = VGroup(*[Rectangle(width=tw, height=th, stroke_color=HUES[h], stroke_width=1.4,
                                  fill_color=HUES[h], fill_opacity=0.35) for h in range(H)])
        thin.arrange(RIGHT, buff=0.06)
        thin.move_to(pivot + LEFT * 2.9, aligned_edge=DOWN).shift(UP * 0.03)
        wide = Rectangle(width=tw * H, height=th, stroke_color=NEEDLE, stroke_width=1.6,
                         fill_color=NEEDLE, fill_opacity=0.3)
        wide.move_to(pivot + RIGHT * 2.9, aligned_edge=DOWN).shift(UP * 0.03)
        lab_l = mt("8 × 64", 28, INK).next_to(thin, UP, buff=0.22)
        lab_r = mt("1 × 512", 28, INK).next_to(wide, UP, buff=0.22)
        sub_l = sans("eight heads", size=17, color=MUTED).next_to(lab_l, UP, buff=0.12)
        sub_r = sans("one full-sized head", size=17, color=MUTED).next_to(lab_r, UP, buff=0.12)

        self.play(FadeIn(fulcrum), FadeIn(base), Create(beam), FadeIn(pin), run_time=0.6)
        tilt = 7 * DEGREES
        left_side = VGroup(thin, lab_l, sub_l)
        self.play_from(c.at("smaller space"),
                       LaggedStart(*[FadeIn(b, shift=DOWN * 0.5) for b in thin], lag_ratio=0.07), run_time=0.8)
        self.play(Rotate(VGroup(beam, left_side[0]), tilt, about_point=pivot),
                  FadeIn(VGroup(lab_l, sub_l).rotate(tilt, about_point=pivot), shift=DOWN * 0.05),
                  run_time=0.6, rate_func=rate_functions.ease_out_back)
        right_side = VGroup(wide, lab_r, sub_r).rotate(tilt, about_point=pivot)
        eq = VGroup(*[ParametricFunction(lambda t: np.array([t, 0.06 * np.sin(t / 0.56 * TAU), 0]),
                                         t_range=[-0.28, 0.28, 0.01], stroke_color=NEEDLE, stroke_width=4.5)
                      for _ in range(2)]).arrange(DOWN, buff=0.13).move_to(pivot + UP * 0.95)
        self.wait_to(c.at("as one"))
        self.play(FadeIn(wide, shift=DOWN * 0.5), run_time=0.45)
        self.play_until(c.after("fullsized head"),
                        Rotate(VGroup(beam, thin, lab_l, sub_l, wide), -tilt, about_point=pivot),
                        FadeIn(VGroup(lab_r, sub_r).rotate(-tilt, about_point=pivot), shift=DOWN * 0.05),
                        FadeIn(eq, scale=0.6),
                        rate_func=rate_functions.ease_in_out_sine, min_time=0.6)
        balance = VGroup(fulcrum, base, beam, pin, thin, wide, lab_l, lab_r, sub_l, sub_r, eq)

        # ── 8. the paper's evidence: Figure 5 (structure), then Figure 4 (anaphora) ──
        R5A, R5B = (112, 180, 505, 377), (112, 396, 505, 593)
        f5a = paper_card(pdf_png(14, R5A, name="c4_fig5_green"), height=3.0)
        f5b = paper_card(pdf_png(14, R5B, name="c4_fig5_red"), height=3.0)
        Group(f5a, f5b).arrange(RIGHT, buff=0.4).move_to(UP * 0.35)
        k5 = eyebrow("Encoder self-attention · layer 5 of 6", color=MUTED).to_edge(UP, buff=0.6)
        cr5 = sans("Vaswani et al., 2017 · Figure 5", size=13, color=MUTED).set_opacity(0.7) \
            .next_to(f5b, DOWN, buff=0.62, aligned_edge=RIGHT)
        self.wait_to(c.at("when the authors"))
        self.play(FadeOut(balance, shift=DOWN * 0.15), run_time=0.7)
        self.play_from(c.at("trained model") - 0.3, FadeIn(f5a, shift=UP * 0.25), FadeIn(k5, shift=DOWN * 0.08),
                       run_time=0.8)
        self.play(FadeIn(f5b, shift=UP * 0.25), FadeIn(cr5), run_time=0.8)
        tag_a = sans("one head", size=18, color=GREEN).next_to(f5a, DOWN, buff=0.22)
        tag_b = sans("another head", size=18, color=RED).next_to(f5b, DOWN, buff=0.22)
        self.play_from(c.at("specialised"), FadeIn(tag_a, shift=UP * 0.08), FadeIn(tag_b, shift=UP * 0.08),
                       run_time=0.6)
        glow_a = SurroundingRectangle(f5a[1], buff=0.06, stroke_color=NEEDLE, stroke_width=2.5, corner_radius=0.04)
        glow_b = SurroundingRectangle(f5b[1], buff=0.06, stroke_color=NEEDLE, stroke_width=2.5, corner_radius=0.04)
        self.play_from(c.at("grammatical structure"), Create(glow_a), Create(glow_b), run_time=0.8)
        self.play_from(c.after("of the sentence") - 0.2, FadeOut(glow_a), FadeOut(glow_b), run_time=0.5)

        R4 = (112, 359, 505, 606)
        f4 = paper_card(pdf_png(13, R4, name="c4_fig4_its"), height=4.85)
        f4.move_to(UP * 0.18)
        k4 = eyebrow("Two heads · layer 5 of 6", color=MUTED).to_edge(UP, buff=0.45)
        cr4 = sans("Vaswani et al., 2017 · Figure 4", size=13, color=MUTED).set_opacity(0.7) \
            .next_to(f4, DOWN, buff=0.16, aligned_edge=RIGHT)
        self.wait_to(c.at("while others"))
        fig5 = Group(f5a, f5b, cr5, tag_a, tag_b)
        self.play(fig5.animate.shift(LEFT * 0.8).set_opacity(0), FadeOut(k5), run_time=0.55,
                  rate_func=rate_functions.ease_in_sine)
        self.remove(fig5)
        self.play(FadeIn(f4, shift=LEFT * 0.6), FadeIn(k4, shift=DOWN * 0.08), FadeIn(cr4), run_time=0.85,
                  rate_func=rate_functions.ease_out_sine)
        self.drift(0.004)

        img = f4[1]
        pad = 2.2
        its_box = Polygon(*[pdf_map(img, R4, x, y) for x, y in
                            [(235 - pad, 421 - pad), (248 + pad, 421 - pad), (248 + pad, 433 + pad),
                             (235 - pad, 433 + pad)]])
        law_box = Polygon(*[pdf_map(img, R4, x, y) for x, y in
                            [(136 - pad, 530 - pad), (149 + pad, 530 - pad), (149 + pad, 549 + pad),
                             (136 - pad, 549 + pad)]])
        for b in (its_box, law_box):
            b.set_stroke(NEEDLE, 3).set_fill(NEEDLE, 0.12).round_corners(0.05)
        noun = sans("noun", size=21, color=NEEDLE)
        noun.move_to([law_box.get_x(), f4.get_bottom()[1] - 0.3, 0])
        pron = sans("pronoun", size=21, color=NEEDLE)
        pron.move_to([its_box.get_x(), f4.get_top()[1] + 0.3, 0])
        self.play_from(c.at("which noun") - 0.15, Create(law_box), FadeIn(noun, shift=UP * 0.08), run_time=0.5)
        self.play_from(c.at("pronoun"), Create(its_box), FadeIn(pron, shift=DOWN * 0.08), run_time=0.5)

        # ── fade out for the chapter card ──────────────────────────────────────────
        self.wait_to(c.dur - 0.55)
        self.play(FadeOut(Group(*self.mobjects)), run_time=0.5)
        self.finish()
