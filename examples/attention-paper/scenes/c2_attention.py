"""c2_attention — attention as a soft dictionary lookup: query / key / value, dot products, softmax,
weighted average, then the paper's own example ("The Law will never be perfect, but its application
should be just") and a glimpse of Figure 4."""
from style import *
from c2_kit import *

# ── data (all weights below are computed, never typed) ─────────────────────────
# 1. Dictionary: query "dog" vs keys "cat"/"dog" as 2D vectors (length 2, at 70° and 20°).
_kc = 2.0 * np.array([np.cos(np.radians(70)), np.sin(np.radians(70))])
_kd = 2.0 * np.array([np.cos(np.radians(20)), np.sin(np.radians(20))])
DICT_W = softmax(np.array([_kd @ _kc, _kd @ _kd]))          # [cat, dog]  ≈ [0.19, 0.81]
DICT_OUT = DICT_W @ np.array([7.0, 3.0])                     # ≈ 3.77

# 2. "The cat sat on the mat": 2D keys, one 2D query (for "sat"), 4-dim values.
WORDS = ["The", "cat", "sat", "on", "the", "mat"]
FOCUS = 2                                                     # "sat"
K_ANG = [200, 35, 110, 250, 160, 60]
K_LEN = [0.8, 1.9, 1.2, 0.9, 0.8, 1.4]
K2 = np.array([[l * np.cos(np.radians(a)), l * np.sin(np.radians(a))] for a, l in zip(K_ANG, K_LEN)])
Q2 = 1.6 * np.array([np.cos(np.radians(30)), np.sin(np.radians(30))])
SCORES = K2 @ Q2                                              # dot products
WEIGHTS = softmax(SCORES)
_rng = np.random.default_rng(7)
QV = _rng.normal(size=(6, 4))                                 # display shading for the q columns
KV = _rng.normal(size=(6, 4))                                 # … k columns
VV = _rng.normal(size=(6, 4))                                 # values
OUT = WEIGHTS @ VV                                            # the new vector for "sat"

# 3. The paper's sentence (Figure 4). Toy 4-feature keys [noun, subject, verb/aux, function word];
#    the query of "its" looks for a noun that is the subject. Weights = softmax(q·k / √4).
LAW = ["The", "Law", "will", "never", "be", "perfect", "but", "its", "application", "should", "be", "just"]
_F = {"The": [0, 0, 0, 1], "Law": [1, 1, 0, 0], "will": [0, 0, 1, 0], "never": [0, 0, .5, .5],
      "be": [0, 0, 1, 0], "perfect": [.3, 0, 0, 0], "but": [0, 0, 0, 1], "its": [.2, 0, 0, .5],
      "application": [1, 0, 0, 0], "should": [0, 0, 1, 0], "just": [.3, 0, 0, 0]}
_KL = np.array([_F[w] for w in LAW], dtype=float)
_QL = np.array([4.0, 4.8, -1.0, -1.0])
LAW_W = softmax(_KL @ _QL / np.sqrt(4))
ITS = LAW.index("its")

# Figure 4, bottom panel (isolated attention from "its"), p13, PDF points.
FIG4_CLIP = (112, 357.5, 512, 606)
FIG4_ITS = (235.1, 395.0, 247.7, 432.5)      # "its" on the top row (rotated label)
FIG4_LAW = (136.2, 530.4, 148.8, 547.8)      # "Law" on the bottom row


class C2Attention(BeatScene):
    BEAT = "c2_attention"

    def construct(self):
        c = self.cues

        # ════════════════════════════════════════════════════════════════════
        # A. A dictionary lookup, then its soft version
        # ════════════════════════════════════════════════════════════════════
        src = '{"cat": 7, "dog": 3}["dog"]'
        code = Text(src, font=MONO, font_size=40, color=MUTED)
        glyphs = src.replace(" ", "")
        assert len(code) == len(glyphs)
        def span(a, b):
            return VGroup(*code[a:b])
        k_cat, v_cat, k_dog, v_dog, look = span(1, 6), span(7, 8), span(9, 14), span(15, 16), span(18, 23)
        for g, col in ((k_cat, GREEN), (k_dog, GREEN), (v_cat, ORANGE), (v_dog, ORANGE), (look, BLUE)):
            g.set_color(col)
        arrow = Text("→", font=MONO, font_size=40, color=MUTED)
        res = Text("3", font=MONO, font_size=40, color=ORANGE)
        line = VGroup(code, arrow, res).arrange(RIGHT, buff=0.35)
        res.match_y(v_dog)
        arrow.match_y(v_dog)
        ghost = Text(f"{DICT_OUT:.2f}", font=MONO, font_size=40)
        full_w = code.width + arrow.width + ghost.width + 0.7
        line.shift([-full_w / 2 - code.get_left()[0], 0.85 - code.get_y(), 0])
        panel = RoundedRectangle(corner_radius=0.2, width=full_w + 1.5, height=2.75, fill_color=PANEL,
                                 fill_opacity=1, stroke_color=FAINT, stroke_width=1.5).move_to(UP * 0.55)
        lang = sans("python", size=16, color=MUTED).move_to(panel.get_corner(UL) + RIGHT * 0.65 + DOWN * 0.35)
        dots = VGroup(*[Dot(radius=0.05, color=FAINT) for _ in range(3)]).arrange(RIGHT, buff=0.1)
        dots.move_to(panel.get_corner(UR) + LEFT * 0.55 + DOWN * 0.35)

        # match bars under the two keys (hard: 0 / 1; soft: computed)
        BW = 1.45
        def mbar(key, w):
            track = Line(LEFT * BW / 2, RIGHT * BW / 2, stroke_color=FAINT, stroke_width=6)
            track.move_to([key.get_x(), code.get_bottom()[1] - 0.5, 0])
            bar = Line(track.get_start(), track.get_start() + RIGHT * max(BW * w, 0.001),
                       stroke_color=NEEDLE, stroke_width=6)
            return track, bar
        tr_cat, b_cat = mbar(k_cat, 0)
        tr_dog, b_dog = mbar(k_dog, 1)
        n_cat = sans("0", size=20, color=NEEDLE).next_to(tr_cat, DOWN, buff=0.18)
        n_dog = sans("1", size=20, color=NEEDLE).next_to(tr_dog, DOWN, buff=0.18)
        b_cat.set_stroke(opacity=0)

        self.play(FadeIn(panel, shift=UP * 0.1), FadeIn(lang), FadeIn(dots), run_time=0.8)
        self.wait_to(c.at("dictionary") - 0.2)
        dict_part = VGroup(*code[:17])
        self.play(ShowIncreasingSubsets(dict_part, rate_func=linear), run_time=1.3)
        self.wait_to(c.at("hand over") - 0.1)
        self.play(ShowIncreasingSubsets(VGroup(*code[17:]), rate_func=linear), run_time=0.55)
        # the lookup finds its exact match
        hl = SurroundingRectangle(k_dog, color=NEEDLE, buff=0.08, corner_radius=0.08, stroke_width=2)
        self.play(Create(hl), run_time=0.45)
        self.wait_to(c.at("get back") - 0.05)
        hl_v = SurroundingRectangle(v_dog, color=NEEDLE, buff=0.08, corner_radius=0.08, stroke_width=2)
        self.play(TransformFromCopy(hl, hl_v), run_time=0.45)
        self.play(FadeIn(arrow, shift=RIGHT * 0.1), TransformFromCopy(v_dog, res), run_time=0.55)
        self.play(FadeIn(VGroup(tr_cat, tr_dog)), Create(b_dog), FadeIn(n_cat), FadeIn(n_dog), run_time=0.6)

        # "soft version": the hard 0/1 match relaxes to computed similarity weights
        self.wait_to(c.at("soft version") - 0.1)
        b_cat2 = Line(tr_cat.get_start(), tr_cat.get_start() + RIGHT * BW * DICT_W[0], stroke_color=NEEDLE, stroke_width=6)
        b_dog2 = Line(tr_dog.get_start(), tr_dog.get_start() + RIGHT * BW * DICT_W[1], stroke_color=NEEDLE, stroke_width=6)
        n_cat2 = num(DICT_W[0], size=20, color=NEEDLE).move_to(n_cat)
        n_dog2 = num(DICT_W[1], size=20, color=NEEDLE).move_to(n_dog)
        res2 = Text(f"{DICT_OUT:.2f}", font=MONO, font_size=40, color=ORANGE).move_to(res, aligned_edge=LEFT)
        res2.align_to(res, DOWN)
        hl_c = SurroundingRectangle(k_cat, color=NEEDLE, buff=0.08, corner_radius=0.08, stroke_width=2,
                                    stroke_opacity=0.35)
        hl_vc = SurroundingRectangle(v_cat, color=NEEDLE, buff=0.08, corner_radius=0.08, stroke_width=2,
                                     stroke_opacity=0.35)
        self.play(Transform(b_cat, b_cat2), Transform(b_dog, b_dog2),
                  Transform(n_cat, n_cat2), Transform(n_dog, n_dog2),
                  FadeIn(hl_c), FadeIn(hl_vc), hl.animate.set_stroke(opacity=0.8), hl_v.animate.set_stroke(opacity=0.8),
                  run_time=1.1)
        self.play(Transform(res, res2), run_time=0.6)
        soft_lbl = serif("a soft lookup", size=34, color=INK, slant=ITALIC).next_to(panel, DOWN, buff=0.45)
        self.play(FadeIn(soft_lbl, shift=UP * 0.1), run_time=0.5)

        part_a = VGroup(panel, lang, dots, code, arrow, res, tr_cat, tr_dog, b_cat, b_dog, n_cat, n_dog,
                        hl, hl_v, hl_c, hl_vc, soft_lbl)

        # ════════════════════════════════════════════════════════════════════
        # B. Every word produces a query, a key and a value
        # ════════════════════════════════════════════════════════════════════
        chips = VGroup(*[tchip(w, size=26) for w in WORDS]).arrange(RIGHT, buff=0.32).move_to(UP * 3.1)
        minis = VGroup()
        for i, ch in enumerate(chips):
            trio = VGroup(vec_cells(QV[i], BLUE, cell=0.105), vec_cells(KV[i], GREEN, cell=0.105),
                          vec_cells(VV[i], ORANGE, cell=0.105)).arrange(RIGHT, buff=0.07)
            trio.next_to(ch, DOWN, buff=0.16)
            minis.add(trio)

        self.wait_to(c.at("every word") - 0.55)
        self.play(FadeOut(part_a, shift=UP * 0.3), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(ch, shift=DOWN * 0.15) for ch in chips], lag_ratio=0.12), run_time=1.0)
        self.wait_to(c.at("three vectors") - 0.2)
        self.play(LaggedStart(*[LaggedStart(*[GrowFromEdge(col, UP) for col in trio], lag_ratio=0.25)
                                for trio in minis], lag_ratio=0.1), run_time=0.9)

        # focus on "sat"
        big = tchip("sat", size=34).move_to(LEFT * 4.6 + DOWN * 0.15)
        cols = VGroup(vec_cells(QV[FOCUS], BLUE, cell=0.36, stroke_w=1.5, gap=0.04),
                      vec_cells(KV[FOCUS], GREEN, cell=0.36, stroke_w=1.5, gap=0.04),
                      vec_cells(VV[FOCUS], ORANGE, cell=0.36, stroke_w=1.5, gap=0.04))
        xs = [-1.6, 1.1, 3.8]
        for col, x in zip(cols, xs):
            col.move_to([x, 0.15, 0])
        y_name = cols[0].get_bottom()[1] - 0.6
        names = VGroup(*[set_baseline(sans(s, size=28, color=col_c, weight=MEDIUM).set_x(col.get_x()), s, y_name)
                         for s, col, col_c in zip(("query", "key", "value"), cols, (BLUE, GREEN, ORANGE))])
        gloss = VGroup(*[set_baseline(serif(s, size=26, color=MUTED, slant=ITALIC).set_x(n.get_x()), s, y_name - 0.5)
                         for s, n in zip(("looking for", "has to offer", "passes along"), names)])
        hl_sat = chips[FOCUS]
        self.play(TransformFromCopy(chips[FOCUS], big), *tint_chip(chips[FOCUS], BLUE, fill=0.1), run_time=0.7)
        for i, (cue, glo) in enumerate((("a query which", "looking for"), ("a key which", "has to offer"),
                                        ("a value which", "pass along"))):
            self.wait_to(c.at(cue) - 0.05)
            self.play(TransformFromCopy(minis[FOCUS][i], cols[i]),
                      FadeIn(names[i], shift=UP * 0.1), run_time=0.7)
            self.wait_to(c.at(glo) - 0.15)
            self.play(FadeIn(gloss[i], shift=UP * 0.08), run_time=0.5)

        # ════════════════════════════════════════════════════════════════════
        # C. Compare the query with every key: dot products
        # ════════════════════════════════════════════════════════════════════
        P = np.array([-3.75, -0.45, 0])        # plane origin
        U = 1.0                                 # units per vector unit
        ring = Circle(radius=2.0, stroke_color=FAINT, stroke_width=1.2).move_to(P)
        axes = VGroup(Line(P + LEFT * 2.2, P + RIGHT * 2.2), Line(P + DOWN * 2.2, P + UP * 2.2))
        axes.set_stroke(color=FAINT, width=1.2)

        def vec_arrow(v, color, width=5):
            end = P + U * np.array([v[0], v[1], 0])
            return Arrow(P, end, buff=0, stroke_width=width, color=color, tip_length=0.2,
                         max_stroke_width_to_length_ratio=12, max_tip_length_to_length_ratio=0.3)

        q_arrow = vec_arrow(Q2, BLUE, width=6)
        q_lbl = unicode_math("q", size=34, color=BLUE)
        q_dir = Q2 / np.linalg.norm(Q2)
        q_lbl.move_to(q_arrow.get_end() + 0.32 * np.array([q_dir[1], -q_dir[0], 0]) + 0.05 * RIGHT)
        k_arrows, k_lbls = VGroup(), VGroup()
        for i, w in enumerate(WORDS):
            a = vec_arrow(K2[i], GREEN, width=4)
            d = K2[i] / np.linalg.norm(K2[i])
            lbl = sans(w, size=20, color=GREEN).move_to(a.get_end() + np.array([d[0], d[1], 0]) * 0.38)
            k_arrows.add(a)
            k_lbls.add(lbl)

        # right panel: one row per word
        AX = 2.6                                # zero axis x
        SS = 0.75                               # score bar scale
        WS = 3.6                                # weight bar scale
        ys = [1.05 - 0.56 * i for i in range(6)]
        row_lbl = VGroup(*[sans(w, size=22, color=INK).move_to([1.4, y, 0], aligned_edge=RIGHT)
                           for w, y in zip(WORDS, ys)])
        zero = Line([AX, ys[0] + 0.35, 0], [AX, ys[-1] - 0.35, 0], stroke_color=MUTED, stroke_width=1.5)

        def score_bar(i):
            s = SCORES[i] * SS
            r = Rectangle(width=max(abs(s), 0.01), height=0.3, stroke_width=0, fill_color=INK, fill_opacity=0.55)
            r.move_to([AX + s / 2, ys[i], 0])
            return r

        def weight_bar(i):
            s = WEIGHTS[i] * WS
            r = Rectangle(width=max(s, 0.012), height=0.3, stroke_width=0, fill_color=NEEDLE, fill_opacity=0.9)
            r.move_to([AX + s / 2, ys[i], 0])
            return r

        sbars = VGroup(*[score_bar(i) for i in range(6)])
        snums = VGroup(*[num(SCORES[i], size=20, color=INK).move_to([5.4, ys[i], 0], aligned_edge=LEFT)
                         for i in range(6)])
        wbars = VGroup(*[weight_bar(i) for i in range(6)])
        wnums = VGroup(*[num(WEIGHTS[i], size=20, color=NEEDLE).move_to([5.4, ys[i], 0], aligned_edge=LEFT)
                         for i in range(6)])
        head_s = mt("<i>q</i> · <i>k</i>", size=32).move_to([AX + 1.4, 1.75, 0])
        head_w = sans("softmax", size=26, color=NEEDLE, weight=MEDIUM).move_to(head_s)

        self.wait_to(c.at("to update") - 0.15)
        others = VGroup(big, cols[1], cols[2], names, gloss)
        q_seed = cols[0]
        self.play(FadeOut(others, shift=DOWN * 0.2), q_seed.animate.move_to(P + UP * 0.6 + RIGHT * 0.6).scale(0.6),
                  run_time=0.7)
        self.play(FadeIn(VGroup(ring, axes)), ReplacementTransform(q_seed, q_arrow), FadeIn(q_lbl), run_time=0.8)
        self.wait_to(c.at("key of every") - 0.2)
        self.play(LaggedStart(*[AnimationGroup(Indicate(minis[i][1], color=GREEN, scale_factor=1.25),
                                               GrowArrow(k_arrows[i]), FadeIn(k_lbls[i]))
                                for i in range(6)], lag_ratio=0.14), run_time=1.5)
        self.wait_to(c.at("dot product") - 0.25)
        self.play(FadeIn(row_lbl, lag_ratio=0.1), Create(zero), FadeIn(head_s, shift=DOWN * 0.1), run_time=0.6)
        self.play(LaggedStart(*[GrowFromPoint(b, [AX, b.get_y(), 0]) for b in sbars], lag_ratio=0.1),
                  LaggedStart(*[FadeIn(n) for n in snums], lag_ratio=0.1), run_time=1.0)

        # "large when two vectors point in similar directions"
        self.wait_to(c.at("similar directions") - 0.4)
        ang_q = np.arctan2(Q2[1], Q2[0])
        ang_c = np.arctan2(K2[1][1], K2[1][0])
        arc = Arc(radius=0.75, start_angle=ang_q, angle=ang_c - ang_q, arc_center=P, stroke_color=NEEDLE,
                  stroke_width=3)
        dim_keys = [i for i in range(6) if i != 1]
        self.play(Create(arc),
                  k_arrows[1].animate.set_color(NEEDLE), k_lbls[1].animate.set_color(NEEDLE),
                  sbars[1].animate.set_fill(color=NEEDLE, opacity=0.95), snums[1].animate.set_color(NEEDLE),
                  *[k_arrows[i].animate.set_opacity(0.35) for i in dim_keys],
                  *[k_lbls[i].animate.set_opacity(0.45) for i in dim_keys], run_time=0.9)
        self.play(*[k_arrows[i].animate.set_opacity(1) for i in dim_keys],
                  *[k_lbls[i].animate.set_opacity(1) for i in dim_keys],
                  k_arrows[1].animate.set_color(GREEN), k_lbls[1].animate.set_color(GREEN),
                  sbars[1].animate.set_fill(color=INK, opacity=0.55), snums[1].animate.set_color(INK),
                  FadeOut(arc), run_time=0.7)

        # ════════════════════════════════════════════════════════════════════
        # D. Softmax: positive weights that add up to one
        # ════════════════════════════════════════════════════════════════════
        self.wait_to(c.at("softmax") - 0.1)
        self.play(ReplacementTransform(sbars, wbars), FadeOut(snums, shift=UP * 0.12), FadeIn(wnums, shift=UP * 0.12),
                  FadeOut(head_s, shift=UP * 0.12), FadeIn(head_w, shift=UP * 0.12), run_time=1.2)
        # stack the weights end to end into one bar of length 1
        SY = ys[-1] - 0.75
        track = Rectangle(width=WS, height=0.3, stroke_color=MUTED, stroke_width=1.2, fill_opacity=0)
        track.move_to([AX + WS / 2, SY, 0])
        one = sans("= 1", size=24, color=NEEDLE, weight=MEDIUM).next_to(track, RIGHT, buff=0.25)
        pieces, x0 = VGroup(), AX
        for i in range(6):
            w = WEIGHTS[i] * WS
            p = wbars[i].copy().set_fill(opacity=0.9 - 0.12 * (i % 2))
            pieces.add(p)
        targets = []
        for i in range(6):
            w = WEIGHTS[i] * WS
            targets.append([x0 + w / 2, SY, 0])
            x0 += w
        self.wait_to(c.at("add up") - 0.55)
        self.play(FadeIn(track), run_time=0.3)
        self.play(LaggedStart(*[pieces[i].animate.move_to(targets[i]) for i in range(6)], lag_ratio=0.08),
                  run_time=0.8)
        self.play(FadeIn(one, shift=LEFT * 0.1), run_time=0.4)

        # ════════════════════════════════════════════════════════════════════
        # E. The new representation: weighted average of the values
        # ════════════════════════════════════════════════════════════════════
        vcols = VGroup(*[vec_cells(VV[i], ORANGE, cell=0.115) .move_to([6.45, ys[i], 0]) for i in range(6)])
        out_col = vec_cells(OUT, ORANGE, cell=0.42, stroke_w=1.5, gap=0.05).move_to(P + UP * 0.1)
        out_chip = tchip("sat", size=26).next_to(out_col, UP, buff=0.35)
        out_chip[0].set_stroke(color=BLUE, opacity=0.95).set_fill(color=BLUE, opacity=0.1)
        out_chip[1].set_color(BLUE)
        out_math = mt("Σ <i>w</i><sub><i>i</i></sub> <i>v</i><sub><i>i</i></sub>", size=32).next_to(out_col, DOWN, buff=0.35)

        self.wait_to(c.at("new representation") - 0.6)
        self.play(FadeOut(VGroup(ring, axes, q_arrow, q_lbl, k_arrows, k_lbls), shift=LEFT * 0.2),
                  FadeOut(VGroup(track, pieces, one)), run_time=0.6)
        self.play(LaggedStart(*[TransformFromCopy(minis[i][2], vcols[i]) for i in range(6)], lag_ratio=0.08),
                  run_time=0.9)
        self.wait_to(c.at("weighted") - 0.1)
        self.play(*[vcols[i].animate.set_opacity(0.15 + 0.85 * WEIGHTS[i] / WEIGHTS.max()) for i in range(6)],
                  *[Indicate(wbars[i], color=NEEDLE, scale_factor=1.06) for i in (1, 5)], run_time=0.6)
        self.wait_to(c.at("all the values") - 0.35)
        merged = [out_col.copy().set_opacity(WEIGHTS[i] / WEIGHTS.max()) for i in range(6)]
        self.play(*[ReplacementTransform(vcols[i], merged[i]) for i in range(6)], run_time=1.0, rate_func=smooth)
        self.play(FadeIn(out_col), *[FadeOut(m) for m in merged], FadeIn(out_chip, shift=DOWN * 0.1),
                  FadeIn(out_math, shift=UP * 0.1), run_time=0.6)

        # ════════════════════════════════════════════════════════════════════
        # F. The paper's sentence: "its" draws its meaning from "Law"
        # ════════════════════════════════════════════════════════════════════
        self.wait_to(c.at("take a sentence") - 0.2)
        self.play(FadeOut(VGroup(chips, minis, row_lbl, zero, wbars, wnums, head_w, out_col, out_chip, out_math),
                          shift=UP * 0.3), run_time=0.7)
        kicker = eyebrow("from the paper · Figure 4", size=17).to_corner(UL, buff=0.6)
        self.play(FadeIn(kicker, shift=RIGHT * 0.15), run_time=0.6)

        lchips = VGroup(*[tchip(w, size=24, pad=0.14) for w in LAW]).arrange(RIGHT, buff=0.16)
        comma = sans(",", size=24, color=MUTED)
        # place the comma after "perfect" and keep the spacing even
        lchips[6:].shift(RIGHT * 0.12)
        row = VGroup(lchips, comma)
        if lchips.width > 13.3:
            row.scale(13.3 / lchips.width)
        row.move_to(DOWN * 0.75)
        comma.next_to(lchips[5], RIGHT, buff=0.05)
        comma.set_y(baseline(lchips[5][1], "perfect") - 0.01, DOWN).shift(DOWN * comma.height * 0.35)

        # words appear as they are spoken
        for ch in [*lchips]:
            ch[0].set_stroke(opacity=0.18).set_fill(opacity=0.02)
            ch[1].set_opacity(0.22)
        comma.set_opacity(0.22)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.1) for m in [*lchips[:6], comma, *lchips[6:]]],
                              lag_ratio=0.06), run_time=1.0)
        i0, _ = c._find(" ".join(LAW), 1)
        for i, w in enumerate(LAW):
            t = c.lead + c.words[i0 + i]["start"]
            self.wait_to(t - 0.06)
            anims = [lchips[i][0].animate.set_stroke(opacity=0.55).set_fill(opacity=0.07),
                     lchips[i][1].animate.set_opacity(1)]
            if w == "perfect":
                anims.append(comma.animate.set_opacity(1))
            self.play(*anims, run_time=0.2)

        # "Attention lets the word its…": its becomes the query
        self.wait_to(c.at("the word its") + 0.1)
        self.play(*tint_chip(lchips[ITS], BLUE, fill=0.14), lchips[ITS].animate.shift(UP * 0.0), run_time=0.5)

        top_y = lchips.get_top()[1] + 0.06
        src_pt = np.array([lchips[ITS].get_x(), top_y, 0])
        arcs = VGroup()
        targets = [j for j in range(len(LAW)) if j != ITS]
        for j in targets:
            dst = np.array([lchips[j].get_x(), top_y, 0])
            ang = 0.62 * PI if j < ITS else -0.62 * PI
            a = ArcBetweenPoints(src_pt, dst, angle=ang)
            arcs.add(a)

        def styled(j, w):
            return dict(color=NEEDLE, width=0.8 + 16 * w, opacity=0.25 + 0.75 * min(1.0, w / LAW_W.max()))

        uni = 1.0 / len(LAW)
        for a in arcs:
            a.set_stroke(**styled(0, uni))
        # small weight histogram under the row (starts uniform)
        BASE = -2.45
        HB = 1.0 / LAW_W.max()
        hbars = VGroup(*[Rectangle(width=0.26, height=uni * HB, stroke_width=0, fill_color=NEEDLE, fill_opacity=0.9)
                         .move_to([lchips[j].get_x(), BASE, 0], aligned_edge=DOWN) for j in range(len(LAW))])
        hbase = Line([lchips.get_left()[0], BASE, 0], [lchips.get_right()[0], BASE, 0], stroke_color=FAINT,
                     stroke_width=1.5)

        self.wait_to(c.at("draw") - 0.1)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.05), FadeIn(hbase),
                  LaggedStart(*[GrowFromEdge(b, DOWN) for b in hbars], lag_ratio=0.03), run_time=1.0)

        self.wait_to(c.at("law", 2) - 0.45)
        arcs_t = arcs.copy()
        for a, j in zip(arcs_t, targets):
            a.set_stroke(**styled(j, LAW_W[j]))
        hb_t = [b.copy().stretch_to_fit_height(max(LAW_W[j] * HB, 0.012), about_edge=DOWN)
                for j, b in enumerate(hbars)]
        law_lbl = num(LAW_W[1], size=20, color=NEEDLE).next_to(hb_t[1], RIGHT, buff=0.12).align_to(hb_t[1], UP)
        self.play(Transform(arcs, arcs_t), *[Transform(hbars[j], hb_t[j]) for j in range(len(LAW))],
                  *tint_chip(lchips[1], NEEDLE, fill=0.16), run_time=0.9)
        self.play(FadeIn(law_lbl, shift=UP * 0.08), run_time=0.4)

        # "several words away, in a single step": one pulse along the arc
        self.wait_to(c.at("several words") - 0.1)
        law_arc = arcs[targets.index(1)]
        pulse = law_arc.copy().set_stroke(color=WHITE, width=10, opacity=1)
        self.play(ShowPassingFlash(pulse, time_width=0.35), run_time=0.9)

        # cut to the paper's own Figure 4
        self.wait_to(c.at("in a single") - 0.05)
        path = pdf_png(13, FIG4_CLIP, name="c2_fig4")
        card = paper_card(path, height=5.1).move_to(UP * 0.15)
        img = card[1]
        x0, y0, x1, y1 = FIG4_CLIP

        def box(r, color=NEEDLE):
            W, H = img.width, img.height
            tl = img.get_corner(UL)
            bw = (r[2] - r[0]) / (x1 - x0) * W + 0.1
            bh = (r[3] - r[1]) / (y1 - y0) * H + 0.1
            cx = tl[0] + ((r[0] + r[2]) / 2 - x0) / (x1 - x0) * W
            cy = tl[1] - ((r[1] + r[3]) / 2 - y0) / (y1 - y0) * H
            return RoundedRectangle(corner_radius=0.05, width=bw, height=bh, stroke_color=color, stroke_width=3)\
                .move_to([cx, cy, 0])
        b_its = box(FIG4_ITS, BLUE)
        b_law = box(FIG4_LAW, NEEDLE)
        cite = sans("Vaswani et al., 2017 · Figure 4", size=15, color=MUTED).set_opacity(0.8)
        cite.next_to(card, DOWN, buff=0.2).align_to(card, LEFT)
        scene_f = VGroup(lchips, comma, arcs, hbars, hbase, law_lbl)
        self.play(FadeOut(scene_f, shift=DOWN * 0.3), FadeIn(card, shift=UP * 0.3), FadeIn(cite), run_time=0.7)
        self.play(Create(b_its), run_time=0.35)
        self.play(Create(b_law), run_time=0.35)

        self.wait_to(c.dur - 0.5)
        self.play(FadeOut(Group(card, b_its, b_law, cite, kicker)), run_time=0.45)
        self.finish()
