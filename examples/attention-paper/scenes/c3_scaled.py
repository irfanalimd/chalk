"""c3_scaled — scaled dot-product attention in matrix form: Q, K, V; Eq. 1 built term by term; two
matrix multiplications and a softmax; why divide by √dₖ (real random dot products, d = 4 vs d = 512);
and the decoder's causal mask."""
from style import *
from c2_kit import *

# ── data (seeded, computed) ───────────────────────────────────────────────────
WORDS = ["The", "cat", "sat", "on", "the", "mat"]
_r = np.random.default_rng(3)
QM, KM, VM = _r.normal(size=(6, 4)), _r.normal(size=(6, 4)), _r.normal(size=(6, 4))
SM = QM @ KM.T / np.sqrt(4)                 # scaled scores, n × n
AM = softmax(SM, axis=1)                    # row softmax
OM = AM @ VM                                # output, n × d

# Why scale: one query against ten keys, components ~ N(0, 1).
_r7 = np.random.default_rng(7)
DEMO = {}
for _d in (4, 512):
    _q = _r7.normal(size=_d)
    _K = _r7.normal(size=(10, _d))
    _s = _K @ _q
    _p = softmax(_s)
    _ps = softmax(_s / np.sqrt(_d))
    _J = np.diag(_p) - np.outer(_p, _p)          # ∂softmax/∂scores
    DEMO[_d] = dict(s=_s, p=_p, ps=_ps, grad=np.abs(_J).max())

# Decoder self-attention with a causal mask.
DE = ["Die", "Katze", "saß", "auf", "der", "Matte"]
_r11 = np.random.default_rng(11)
_qd, _kd = _r11.normal(size=(6, 8)), _r11.normal(size=(6, 8))
SD = _qd @ _kd.T / np.sqrt(8)
MASK = np.triu(np.ones((6, 6), dtype=bool), k=1)       # True = a later word, hidden
AD = softmax(np.where(MASK, -np.inf, SD), axis=1)

EQ1_CLIP = (212, 458, 398, 496)                         # p3, Eq. (1) without the number


def sci(x):
    """4.1e-08 → '4·10<sup>−8</sup>' (markup)."""
    e = int(np.floor(np.log10(x)))
    m = x / 10 ** e
    return f"{m:.0f}·10<sup>−{-e}</sup>" if e < 0 else f"{x:.2f}"


class C3Scaled(BeatScene):
    BEAT = "c3_scaled"

    def construct(self):
        c = self.cues

        # ════════════════════════════════════════════════════════════════════
        # A. Every word at once → stack into Q, K, V
        # ════════════════════════════════════════════════════════════════════
        chips = VGroup(*[tchip(w, size=26) for w in WORDS]).arrange(RIGHT, buff=0.34).move_to(UP * 0.2)
        minis = VGroup()
        for i, ch in enumerate(chips):
            trio = VGroup(vec_cells(QM[i], BLUE, cell=0.105, norm=False),
                          vec_cells(KM[i], GREEN, cell=0.105, norm=False),
                          vec_cells(VM[i], ORANGE, cell=0.105, norm=False)).arrange(RIGHT, buff=0.07)
            trio.next_to(ch, DOWN, buff=0.16)
            minis.add(trio)
        row = VGroup(chips, minis)

        top = chips.get_top()[1] + 0.06
        pairs = VGroup()
        for i in range(6):
            for j in range(i + 1, 6):
                a = ArcBetweenPoints([chips[j].get_x(), top, 0], [chips[i].get_x(), top, 0], angle=0.6 * PI)
                pairs.add(a.set_stroke(color=NEEDLE, width=2, opacity=0.55))

        self.play(LaggedStart(*[FadeIn(VGroup(ch, m), shift=UP * 0.12) for ch, m in zip(chips, minis)],
                              lag_ratio=0.08), run_time=0.9)
        self.wait_to(c.at("same time") - 0.6)
        self.play(*[Create(p) for p in pairs], *[Indicate(m, color=WHITE, scale_factor=1.12) for m in minis],
                  run_time=0.9)
        self.wait_to(c.at("whole operation") - 0.1)
        self.play(FadeOut(pairs), row.animate.move_to(UP * 2.95), run_time=1.1)

        CELL = 0.34
        Qg, Kg, Vg = grid_cells(QM, BLUE, CELL), grid_cells(KM, GREEN, CELL), grid_cells(VM, ORANGE, CELL)
        for g, x in ((Qg, -4.2), (Kg, 0.0), (Vg, 4.2)):
            g.move_to([x, -0.85, 0])

        def lab(markup, g, color, size=40):
            return mt(markup, size=size, color=color).next_to(g, UP, buff=0.28)

        Ql, Kl, Vl = lab("<i>Q</i>", Qg, BLUE), lab("<i>K</i>", Kg, GREEN), lab("<i>V</i>", Vg, ORANGE)
        dims = [mt(s, size=22, color=MUTED).next_to(g, DOWN, buff=0.22) for s, g in
                (("<i>n</i> × <i>d</i><sub><i>k</i></sub>", Qg), ("<i>n</i> × <i>d</i><sub><i>k</i></sub>", Kg),
                 ("<i>n</i> × <i>d</i><sub><i>v</i></sub>", Vg))]

        for k, (cue, g, l, dm) in enumerate((("matrix q", Qg, Ql, dims[0]), ("into k", Kg, Kl, dims[1]),
                                             ("into v", Vg, Vl, dims[2]))):
            self.wait_to(c.at(cue) - (0.75 if k == 0 else 0.55))
            self.play(LaggedStart(*[TransformFromCopy(minis[i][k], g[i]) for i in range(6)], lag_ratio=0.07),
                      FadeIn(l, shift=DOWN * 0.1), FadeIn(dm), run_time=1.0)

        # ════════════════════════════════════════════════════════════════════
        # B. The formula, term by term; Kᵀ transposes
        # ════════════════════════════════════════════════════════════════════
        F = mt("Attention(<i>Q</i>, <i>K</i>, <i>V</i>) = softmax(<i>QK</i><sup><i>T</i></sup> / "
               "√<i>d</i><sub><i>k</i></sub>) <i>V</i>", size=38)
        assert len(F) == 34, len(F)
        for idx, col in ((10, BLUE), (12, GREEN), (14, ORANGE), (25, BLUE), (26, GREEN), (27, GREEN), (33, ORANGE)):
            F[idx].set_color(col)
        F.move_to(UP * 2.75)
        f_head, f_sm, f_close = VGroup(*F[0:17]), VGroup(*F[17:25]), F[32]
        f_Q, f_KT, f_div, f_V = F[25], VGroup(*F[26:28]), VGroup(*F[28:32]), F[33]
        vinc = radical_bar(F[29], VGroup(F[30], F[31]), color=INK, width=2.2)
        F.add(vinc)

        self.wait_to(c.at("and attention becomes") - 0.1)
        self.play(FadeOut(row, shift=UP * 0.3), FadeIn(f_head, shift=DOWN * 0.1), run_time=0.8)
        self.wait_to(c.at("softmax") - 0.1)
        self.play(FadeIn(f_sm, shift=DOWN * 0.1), FadeIn(f_close, shift=DOWN * 0.1), run_time=0.5)
        self.wait_to(c.at("of q") + 0.1)
        self.play(TransformFromCopy(Ql, f_Q), Indicate(Qg, color=BLUE, scale_factor=1.04), run_time=0.6)

        # K → Kᵀ: every cell (i, j) moves to (j, i)
        Ktg = grid_cells(KM.T, GREEN, CELL).move_to(Kg)
        Ktl = lab("<i>K</i><sup><i>T</i></sup>", Ktg, GREEN)
        dims[1].generate_target()
        dims[1].target = mt("<i>d</i><sub><i>k</i></sub> × <i>n</i>", size=22, color=MUTED).next_to(Ktg, DOWN, buff=0.22)
        self.wait_to(c.at("k transpose") - 0.05)
        self.play(*[ReplacementTransform(Kg[i][j], Ktg[j][i], path_arc=-PI / 2) for i in range(6) for j in range(4)],
                  ReplacementTransform(Kl, Ktl), MoveToTarget(dims[1]), run_time=1.0)
        self.remove(*[Kg[i][j] for i in range(6) for j in range(4)])
        self.add(Ktg)
        self.play(TransformFromCopy(Ktl, f_KT), run_time=0.5)
        self.wait_to(c.at("divided") + 0.05)
        self.play(FadeIn(VGroup(*F[28:32]), shift=DOWN * 0.1), run_time=0.6)
        self.wait_to(c.at("d k") - 0.25)
        self.play(Create(vinc), run_time=0.4)
        self.wait_to(c.at("by v") - 0.15)
        self.play(TransformFromCopy(Vl, f_V), Indicate(Vg, color=ORANGE, scale_factor=1.04), run_time=0.6)

        # ════════════════════════════════════════════════════════════════════
        # C. Eq. 1 from the paper; two matmuls and a softmax
        # ════════════════════════════════════════════════════════════════════
        eq_path = pdf_png(3, EQ1_CLIP, dpi=400, name="c3_eq1")
        eq_card = paper_card(eq_path, height=1.0)
        f_scale = 7.0 / F.width
        f_pos = np.array([-6.6 + 3.5, 2.85, 0])
        eq_card.move_to([6.6 - eq_card.width / 2, 2.85, 0])
        eq_cite = sans("Vaswani et al., 2017 · Eq. 1", size=14, color=MUTED).set_opacity(0.8)
        eq_cite.next_to(eq_card, DOWN, buff=0.14).align_to(eq_card, RIGHT)
        self.wait_to(c.at("that one line") - 0.25)
        self.play(F.animate.scale(f_scale).move_to(f_pos), run_time=0.8)
        self.play(FadeIn(eq_card, shift=LEFT * 0.3), FadeIn(eq_cite), run_time=0.6)
        glowF = SurroundingRectangle(F, buff=0.16, corner_radius=0.12, stroke_color=NEEDLE, stroke_width=1.5,
                                     stroke_opacity=0.7)
        self.wait_to(c.at("heart") + 0.1)
        self.play(Create(glowF), run_time=0.6)

        # stage 1: Q · Kᵀ = scores
        Sg = grid_cells(SM, INK, CELL, lo=0.04, hi=0.85)
        times1 = mt("×", size=36, color=MUTED)
        eq1 = mt("=", size=36, color=MUTED)
        stage = VGroup(Qg.copy(), times1, Ktg.copy(), eq1, Sg).arrange(RIGHT, buff=0.42).move_to([-0.9, -0.75, 0])
        Sg_lbl = sans("scores", size=24, color=INK).next_to(Sg, UP, buff=0.28)
        for r in Sg:
            for sq in r:
                sq.set_fill(opacity=0).set_stroke(color=MUTED, opacity=0.35)
        V_park = Vg.copy().move_to([5.35, -0.75, 0])
        self.wait_to(c.at("two matrix") - 0.6)
        self.play(FadeOut(glowF),
                  Qg.animate.move_to(stage[0]), Ktg.animate.move_to(stage[2]),
                  Vg.animate.move_to(V_park), FadeOut(VGroup(*dims)),
                  Ql.animate.next_to(stage[0], UP, buff=0.28), Ktl.animate.next_to(stage[2], UP, buff=0.28),
                  Vl.animate.next_to(V_park, UP, buff=0.28),
                  FadeIn(times1), FadeIn(eq1), FadeIn(Sg), run_time=0.7)
        # one entry, then all of them
        i0, j0 = 2, 1
        rq = SurroundingRectangle(Qg[i0], buff=0.03, stroke_color=NEEDLE, stroke_width=2.5)
        rk = SurroundingRectangle(VGroup(*[Ktg[r][j0] for r in range(4)]), buff=0.03, stroke_color=NEEDLE,
                                  stroke_width=2.5)
        target_cell = Sg[i0][j0]
        rs = SurroundingRectangle(target_cell, buff=0.03, stroke_color=NEEDLE, stroke_width=2.5)
        self.play(Create(rq), Create(rk), FadeIn(Sg_lbl), run_time=0.4)
        cell_full = grid_cells(SM, INK, CELL, lo=0.04, hi=0.85).move_to(Sg)[i0][j0]
        self.play(Create(rs), Transform(target_cell, cell_full), run_time=0.5)
        Sg_full = grid_cells(SM, INK, CELL, lo=0.04, hi=0.85).move_to(Sg)
        self.play(FadeOut(VGroup(rq, rk, rs)),
                  LaggedStart(*[Transform(Sg[i][j], Sg_full[i][j]) for i in range(6) for j in range(6)],
                              lag_ratio=0.02), run_time=0.8)

        # stage 2: row softmax → weights
        Ag = grid_cells(AM / AM.max(), NEEDLE, CELL, signed=False, lo=0.04, hi=0.95).move_to(Sg)
        Ag_lbl = sans("weights", size=24, color=NEEDLE, weight=MEDIUM).move_to(Sg_lbl)
        self.wait_to(c.at("and a softmax") + 0.1)
        self.play(LaggedStart(*[Transform(Sg[i], Ag[i]) for i in range(6)], lag_ratio=0.12),
                  FadeOut(Sg_lbl, shift=UP * 0.1), FadeIn(Ag_lbl, shift=UP * 0.1), run_time=0.8)

        # stage 3: weights · V = output
        Og = grid_cells(OM, INK, CELL, lo=0.06, hi=0.92)
        times2, eq2 = mt("×", size=36, color=MUTED), mt("=", size=36, color=MUTED)
        stage2 = VGroup(Sg.copy(), times2, Vg.copy(), eq2, Og).arrange(RIGHT, buff=0.42).move_to([0, -0.75, 0])
        Og_lbl = sans("output", size=24, color=INK).next_to(Og, UP, buff=0.28)
        Og.set_opacity(0)
        self.play(FadeOut(VGroup(Qg, Ktg, Ql, Ktl, times1, eq1), shift=LEFT * 0.4),
                  Sg.animate.move_to(stage2[0]), Ag_lbl.animate.next_to(stage2[0], UP, buff=0.28),
                  Vg.animate.move_to(stage2[2]), Vl.animate.next_to(stage2[2], UP, buff=0.28),
                  FadeIn(times2), FadeIn(eq2), run_time=0.8)
        Og_full = grid_cells(OM, INK, CELL, lo=0.06, hi=0.92).move_to(Og)
        self.play(FadeIn(Og_lbl),
                  LaggedStart(*[Transform(Og[i], Og_full[i]) for i in range(6)], lag_ratio=0.1), run_time=0.8)
        # "graphics cards": every output entry is independent — light them all at once
        self.wait_to(c.at("graphics cards") - 0.2)
        flash = VGroup(*[sq.copy().set_fill(opacity=0).set_stroke(color=NEEDLE, width=3, opacity=1)
                         for r in Og for sq in r])
        flashS = VGroup(*[sq.copy().set_fill(opacity=0).set_stroke(color=NEEDLE, width=3, opacity=1)
                          for r in Sg for sq in r])
        self.play(FadeIn(flash), FadeIn(flashS), run_time=0.3)
        self.play(FadeOut(flash), FadeOut(flashS), run_time=0.9)

        # ════════════════════════════════════════════════════════════════════
        # D. The division: d = 4 vs d = 512
        # ════════════════════════════════════════════════════════════════════
        self.wait_to(c.at("the division") - 0.4)
        self.play(FadeOut(VGroup(Sg, Ag_lbl, times2, Vg, Vl, eq2, Og, Og_lbl), shift=DOWN * 0.3),
                  FadeOut(Group(eq_card, eq_cite)), F.animate.scale(0.85 / f_scale).move_to(UP * 2.85),
                  run_time=0.8)
        rest = VGroup(*[F[i] for i in range(34) if not 28 <= i <= 31])
        hl_div = SurroundingRectangle(f_div, buff=0.1, corner_radius=0.08, stroke_color=NEEDLE, stroke_width=2)
        self.play(rest.animate.set_opacity(0.4), f_div.animate.set_color(NEEDLE), vinc.animate.set_color(NEEDLE),
                  Create(hl_div), run_time=0.7)

        NB, BW, GAP = 10, 0.3, 0.48
        H = 2.5
        MID, BASE = -0.45, -0.45 - H / 2
        SMAX = max(np.abs(DEMO[d]["s"]).max() for d in (4, 512))
        SC = (H / 2) / SMAX

        charts = {}
        for d, cx in ((4, -3.45), (512, 3.45)):
            xs = [cx + (k - (NB - 1) / 2) * GAP for k in range(NB)]
            axis = Line([xs[0] - 0.4, MID, 0], [xs[-1] + 0.4, MID, 0], stroke_color=MUTED, stroke_width=1.5)
            title = mt(f"<i>d</i> = {d}", size=32, color=INK).move_to([cx, MID + H / 2 + 0.5, 0])
            sbars = VGroup()
            for k, s in enumerate(DEMO[d]["s"]):
                h = max(abs(s) * SC, 0.008)
                r = Rectangle(width=BW, height=h, stroke_width=0, fill_color=INK, fill_opacity=0.6)
                r.move_to([xs[k], MID + np.sign(s) * h / 2, 0])
                sbars.add(r)

            def pbars(p, xs=xs, color=NEEDLE):
                g = VGroup()
                for k, v in enumerate(p):
                    h = max(v * H, 0.008)
                    g.add(Rectangle(width=BW, height=h, stroke_width=0, fill_color=color, fill_opacity=0.92)
                          .move_to([xs[k], BASE + h / 2, 0]))
                return g

            charts[d] = dict(cx=cx, xs=xs, axis=axis, title=title, sbars=sbars,
                             pbars=pbars(DEMO[d]["p"]), psbars=pbars(DEMO[d]["ps"]))

        def stat(markup, d, color=MUTED):
            return mt(markup, size=24, color=color).move_to([charts[d]["cx"], BASE - 0.42, 0])

        self.wait_to(c.at("the dot product") - 0.1)
        self.play(*[FadeIn(charts[d]["title"], shift=DOWN * 0.1) for d in (4, 512)],
                  *[Create(charts[d]["axis"]) for d in (4, 512)], run_time=0.8)
        self.wait_to(c.at("random vectors") - 0.1)
        self.play(*[LaggedStart(*[GrowFromEdge(b, DOWN if b.get_y() > MID else UP) for b in charts[d]["sbars"]],
                                lag_ratio=0.06) for d in (4, 512)], run_time=1.9)
        st_s = {d: stat(f"largest score  {DEMO[d]['s'].max():.1f}", d) for d in (4, 512)}
        self.play(*[FadeIn(st_s[d], shift=UP * 0.08) for d in (4, 512)], run_time=0.5)
        self.wait_to(c.at("scores become large") - 0.1)
        self.play(Indicate(charts[512]["sbars"], color=WHITE, scale_factor=1.05), run_time=0.8)

        # softmax → peaked
        self.wait_to(c.at("softmax", 3) - 0.1)
        base_line = {d: Line([charts[d]["xs"][0] - 0.4, BASE, 0], [charts[d]["xs"][-1] + 0.4, BASE, 0],
                             stroke_color=MUTED, stroke_width=1.5) for d in (4, 512)}
        st_p = {4: stat(f"top weight  {DEMO[4]['p'].max():.2f}", 4),
                512: stat(f"top weight  {DEMO[512]['p'].max():.8f}", 512)}
        self.play(*[ReplacementTransform(charts[d]["sbars"], charts[d]["pbars"]) for d in (4, 512)],
                  *[ReplacementTransform(charts[d]["axis"], base_line[d]) for d in (4, 512)],
                  *[FadeOut(st_s[d], shift=UP * 0.1) for d in (4, 512)], run_time=1.3)
        self.play(*[FadeIn(st_p[d], shift=UP * 0.1) for d in (4, 512)], run_time=0.5)
        # "nearly all of its weight on a single word"
        spike = charts[512]["pbars"][int(np.argmax(DEMO[512]["p"]))]
        self.wait_to(c.at("nearly all") - 0.1)
        halo = glow(spike.copy().set_fill(opacity=0).set_stroke(NEEDLE, width=2), color=NEEDLE, max_opacity=0.25)
        self.play(FadeIn(halo), st_p[512].animate.set_color(NEEDLE), run_time=0.7)
        # vanishing gradients
        st_g = {4: stat(f"largest gradient  {DEMO[4]['grad']:.2f}", 4),
                512: stat(f"largest gradient  {sci(DEMO[512]['grad'])}", 512, color=RED)}
        self.wait_to(c.at("vanishing gradients") - 0.15)
        self.play(*[FadeOut(st_p[d], shift=UP * 0.1) for d in (4, 512)],
                  *[FadeIn(st_g[d], shift=UP * 0.1) for d in (4, 512)], run_time=0.7)

        # divide by √d: the softmax relaxes
        div = {}
        for d in (4, 512):
            t = mt(f"÷ √{d}", size=30, color=NEEDLE)
            t.next_to(charts[d]["title"], RIGHT, buff=0.3)
            bar = radical_bar(t[1], VGroup(*t[2:]), color=NEEDLE, width=2)
            div[d] = VGroup(t, bar)
        self.wait_to(c.at("dividing") - 0.05)
        self.play(*[FadeIn(div[d], shift=LEFT * 0.15) for d in (4, 512)],
                  *[charts[d]["title"].animate.shift(LEFT * (div[d].width + 0.3) / 2) for d in (4, 512)],
                  *[div[d].animate.shift(LEFT * (div[d].width + 0.3) / 2) for d in (4, 512)], run_time=0.9)
        st_ps = {d: stat(f"top weight  {DEMO[d]['ps'].max():.2f}", d) for d in (4, 512)}
        self.wait_to(c.at("keeps the scores") - 0.1)
        self.play(*[ReplacementTransform(charts[d]["pbars"], charts[d]["psbars"]) for d in (4, 512)],
                  FadeOut(halo), *[FadeOut(st_g[d], shift=UP * 0.1) for d in (4, 512)], run_time=1.6)
        self.play(*[FadeIn(st_ps[d], shift=UP * 0.1) for d in (4, 512)], run_time=0.5)
        self.wait_to(c.at("stays soft") - 0.1)
        self.play(rest.animate.set_opacity(1), FadeOut(hl_div), run_time=0.8)

        # ════════════════════════════════════════════════════════════════════
        # E. The decoder's mask
        # ════════════════════════════════════════════════════════════════════
        part_d = VGroup(*[VGroup(charts[d]["title"], div[d], base_line[d], charts[d]["psbars"], st_ps[d])
                          for d in (4, 512)], F)
        self.wait_to(c.at("in the part") - 0.6)
        self.play(FadeOut(part_d, shift=UP * 0.3), run_time=0.6)

        HC = 0.78
        Hm = grid_cells(SD, INK, HC, lo=0.05, hi=0.8).move_to([0.55, -0.4, 0])
        rlbl = VGroup(*[sans(w, size=22, color=BLUE).next_to(Hm[i], LEFT, buff=0.25) for i, w in enumerate(DE)])
        clbl = VGroup(*[sans(w, size=19, color=GREEN).next_to(Hm[0][j], UP, buff=0.2) for j, w in enumerate(DE)])
        for t in clbl:
            t.align_to(clbl[0], DOWN)
        kick = eyebrow("decoder  ·  self-attention", size=17).to_corner(UL, buff=0.6)
        self.play(FadeIn(kick, shift=RIGHT * 0.15), FadeIn(rlbl, lag_ratio=0.08), FadeIn(clbl, lag_ratio=0.08),
                  run_time=0.8)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.1) for r in Hm], lag_ratio=0.15), run_time=1.0)

        # mask: later words → −∞
        masked = [(i, j) for i in range(6) for j in range(6) if MASK[i, j]]
        infs = VGroup()
        for i, j in masked:
            infs.add(mt("−∞", size=22, color=MUTED).move_to(Hm[i][j]))
        pts = [Hm[0][1].get_corner(UL), Hm[0][5].get_corner(UR), Hm[4][5].get_corner(DR)]
        for k in range(4, -1, -1):
            pts += [Hm[k][k + 1].get_corner(DL), Hm[k][k + 1].get_corner(UL)]
        tri = VMobject(stroke_color=NEEDLE, stroke_width=2.5).set_points_as_corners(pts)
        self.wait_to(c.at("one more detail") - 0.1)
        self.play(Create(tri), run_time=1.0)
        self.wait_to(c.at("mask") - 0.2)
        self.play(LaggedStart(*[AnimationGroup(Hm[i][j].animate.set_fill(color="#151922", opacity=1)
                                               .set_stroke(color=FAINT, opacity=1), FadeIn(infs[k]))
                                for k, (i, j) in enumerate(sorted(masked, key=lambda p: p[1] - p[0]))],
                              lag_ratio=0.06), run_time=1.3)
        # softmax over what is left
        Wd = grid_cells(np.where(MASK, 0, AD), NEEDLE, HC, signed=False, lo=0.05, hi=0.95).move_to(Hm)
        self.wait_to(c.at("come later") + 0.15)
        self.play(*[Transform(Hm[i][j], Wd[i][j]) for i in range(6) for j in range(6) if not MASK[i, j]],
                  FadeOut(tri), run_time=0.7)

        # "cannot peek": each row sees only itself and the words before it
        self.wait_to(c.at("so the model") - 0.05)
        rowbox = SurroundingRectangle(VGroup(rlbl[0], Hm[0][0]), buff=0.06, corner_radius=0.06, stroke_color=BLUE,
                                      stroke_width=2.5)

        def seen(i):
            return SurroundingRectangle(VGroup(rlbl[i], *Hm[i][:i + 1]), buff=0.06, corner_radius=0.06,
                                        stroke_color=BLUE, stroke_width=2.5)
        self.play(Create(rowbox), run_time=0.4)
        step = (c.after("produce it") - 0.2 - self.now) / 5
        for i in range(1, 6):
            self.play(Transform(rowbox, seen(i)), run_time=step)

        self.wait_to(c.dur - 0.5)
        self.play(FadeOut(VGroup(Hm, rlbl, clbl, infs, rowbox, kick)), run_time=0.45)
        self.finish()
