"""c7_why — Table 1 (why self-attention): rebuilt row by row, with path-length and cost illustrations."""
import numpy as np

from style import *

COLS = [-6.2, -2.0, 1.4, 4.65]        # col 0 is left-aligned, the rest centred
RULE_X = (-6.3, 6.3)
Y_TOP_RULE, Y_HEAD, Y_MID_RULE = 3.12, 2.74, 2.36
ROW_Y = {"sa": 1.9, "rnn": 1.27, "conv": 0.64}
Y_BOT_RULE = 0.22

# exact entries of Table 1 (p.6 of the paper; restricted self-attention row omitted)
ENTRIES = {
    "sa": ("Self-Attention", "O(n²·d)", "O(1)", "O(1)"),
    "rnn": ("Recurrent", "O(n·d²)", "O(n)", "O(n)"),
    "conv": ("Convolutional", "O(k·n·d²)", "O(1)", "O(log<sub>k</sub>(n))"),
}

NODE_Y = -2.42
NODE_X = np.linspace(-4.9, 4.9, 8)


def math(s, size=34, color=INK):
    """Italic serif math; <sub> markup for subscripts (Unicode subscripts are missing in CMU Serif)."""
    if "<" in s:
        return MarkupText(s, font=SERIF, font_size=size, color=color, slant=ITALIC)
    return unicode_math(s, size, color)


def mixed(s, size=30, color=INK):
    """Upright serif with <i> variables, for labels like 'n ≈ 30'."""
    return MarkupText(s, font=SERIF, font_size=size, color=color)


def rule(y, w=1.6, op=1.0):
    return Line([RULE_X[0], y, 0], [RULE_X[1], y, 0], stroke_color=MUTED, stroke_width=w, stroke_opacity=op)


def cursor_box(mob, pad=0.1):
    r = RoundedRectangle(corner_radius=0.12, width=mob.width + 2 * pad, height=mob.height + 2 * pad,
                         stroke_color=NEEDLE, stroke_width=2.6).move_to(mob)
    return glow(r, NEEDLE, layers=5, max_width=14, max_opacity=0.2)


def arc_between(a, b, h):
    a, b = np.array(a), np.array(b)
    return CubicBezier(a, a + UP * h * 4 / 3 + (b - a) * 0.12, b + UP * h * 4 / 3 - (b - a) * 0.12, b)


class C7Why(BeatScene):
    BEAT = "c7_why"

    def hl(self, target, pad=0.1):
        new = cursor_box(target, pad)
        if self.cursor is None:
            self.cursor = new
            return FadeIn(new, scale=1.05)
        return Transform(self.cursor, new)

    def hl_off(self):
        cur, self.cursor = self.cursor, None
        return FadeOut(cur)

    def construct(self):
        c = self.cues
        self.cursor = None

        # ── table skeleton ──────────────────────────────────────────────────
        kicker = VGroup(eyebrow("Table 1"), sans("Vaswani et al., 2017", 16, MUTED)).arrange(RIGHT, buff=0.3)
        kicker.next_to([RULE_X[0], Y_TOP_RULE, 0], UP, buff=0.2, aligned_edge=LEFT)
        rules = VGroup(rule(Y_TOP_RULE), rule(Y_MID_RULE, 1.2, 0.7), rule(Y_BOT_RULE))
        heads = VGroup(sans("Layer type", 20, MUTED).move_to([COLS[0], Y_HEAD, 0], aligned_edge=LEFT),
                       *[sans(s, 20, MUTED).move_to([x, Y_HEAD, 0]) for s, x in
                         zip(["Complexity per layer", "Sequential operations", "Maximum path length"], COLS[1:])])
        heads[0].align_to([COLS[0], 0, 0], LEFT)

        cells = {}
        for key, (name, *vals) in ENTRIES.items():
            y = ROW_Y[key]
            lab = sans(name, 26, INK).move_to([0, y, 0]).align_to([COLS[0], 0, 0], LEFT)
            vs = [math(v, 34, INK).move_to([x, y, 0]) for v, x in zip(vals, COLS[1:])]
            cells[key] = [lab] + vs

        self.play(FadeIn(kicker, shift=RIGHT * 0.1), LaggedStart(*[Create(r) for r in rules], lag_ratio=0.2),
                  run_time=0.9)
        self.play(LaggedStart(*[FadeIn(h, shift=DOWN * 0.08) for h in heads], lag_ratio=0.15), run_time=1.2)

        # "comparing kinds of layers": the three layer types; convolution stays as quiet context
        self.wait_to(c.at("comparing kinds"))
        self.play(LaggedStart(*[FadeIn(cells[k][0], shift=RIGHT * 0.15) for k in ("sa", "rnn", "conv")],
                              lag_ratio=0.25), run_time=1.0)
        conv_vals = VGroup(*cells["conv"][1:])
        self.play(FadeIn(conv_vals), cells["conv"][0].animate.set_opacity(0.45), run_time=0.7)
        conv_vals.set_opacity(0.45)

        # ── recurrent ───────────────────────────────────────────────────────
        def band(key):
            b = RoundedRectangle(corner_radius=0.1, width=RULE_X[1] - RULE_X[0] + 0.1, height=0.56,
                                 stroke_width=0, fill_color=INK, fill_opacity=0.07)
            return b.move_to([(RULE_X[0] + RULE_X[1]) / 2, ROW_Y[key], 0]).set_z_index(-1)

        row_band = band("rnn")
        cellsq = VGroup(*[RoundedRectangle(corner_radius=0.08, width=0.5, height=0.5, stroke_color=INK,
                                           stroke_width=2, stroke_opacity=0.7, fill_color=INK, fill_opacity=0.05)
                          .move_to([x, NODE_Y, 0]) for x in NODE_X])
        links = VGroup(*[Arrow([NODE_X[i] + 0.27, NODE_Y, 0], [NODE_X[i + 1] - 0.27, NODE_Y, 0], buff=0,
                               stroke_width=2.4, stroke_color=INK, stroke_opacity=0.6, tip_length=0.13,
                               max_tip_length_to_length_ratio=0.3) for i in range(7)])
        self.wait_to(c.at("in a recurrent"))
        self.play(FadeIn(row_band), LaggedStart(*[FadeIn(s, shift=UP * 0.1) for s in cellsq], lag_ratio=0.08),
                  LaggedStart(*[GrowArrow(l) for l in links], lag_ratio=0.08), run_time=c.after("recurrent layer") - self.now + 0.2)

        # one step after another
        nums = VGroup(*[sans(str(i + 1), 17, MUTED).next_to(s, UP, buff=0.12) for i, s in enumerate(cellsq)])
        self.wait_to(c.at("the number of steps"))
        t_steps = c.at("grows with the length") - self.now
        step_anims = []
        for i, s in enumerate(cellsq):
            step_anims.append(AnimationGroup(s.animate.set_stroke(BLUE, 2.6, 1).set_fill(BLUE, 0.22),
                                             FadeIn(nums[i], shift=UP * 0.06)))
        self.play(LaggedStart(*step_anims, lag_ratio=0.55), run_time=t_steps)
        rnn_seq = cells["rnn"][2]
        self.play_until(c.after("the sentence"), FadeIn(rnn_seq, shift=UP * 0.1), self.hl(rnn_seq),
                        *[s.animate.set_stroke(INK, 2, 0.7).set_fill(INK, 0.05) for s in cellsq])

        # a signal between two distant words passes through every word in between
        self.wait_to(c.at("and a signal"))
        ends = VGroup(cellsq[0], cellsq[-1])
        self.play(FadeOut(nums), ends.animate.set_stroke(NEEDLE, 2.8, 1).set_fill(NEEDLE, 0.15), run_time=0.6)
        dot = Dot(radius=0.075, color=NEEDLE).set_z_index(5)
        halo = Dot(radius=0.2, color=NEEDLE, fill_opacity=0.18).set_z_index(4)
        sig = VGroup(halo, dot).move_to(cellsq[0])
        self.play(FadeIn(sig, scale=0.5), run_time=0.3)
        t_end = c.after("in between")
        hop_t = (t_end - self.now) / 7
        for i in range(7):
            last = i == 6
            anims = [sig.animate(rate_func=smooth).move_to(cellsq[i + 1]),
                     links[i].animate(rate_func=there_and_back).set_color(NEEDLE)]
            if not last:
                anims.append(cellsq[i + 1].animate(rate_func=there_and_back).set_fill(NEEDLE, 0.3))
            if i == 4:
                anims.append(FadeIn(cells["rnn"][3], shift=UP * 0.1))
                anims.append(self.hl(cells["rnn"][3]))
            self.play(*anims, run_time=hop_t)
        hops = sans("7 hops", 19, NEEDLE).next_to(cellsq[-1], UP, buff=0.14)
        self.play(FadeIn(hops, shift=UP * 0.08), Flash(cellsq[-1], color=NEEDLE, line_length=0.15,
                                                     flash_radius=0.4), run_time=0.6)

        # ── self-attention: every pair, directly ──────────────────────────────
        tops = [np.array([x, NODE_Y + 0.25, 0]) for x in NODE_X]
        arcs = VGroup()
        for i in range(8):
            for j in range(i + 1, 8):
                arcs.add(arc_between(tops[i], tops[j], 0.235 * (j - i)).set_stroke(INK, 1.6, 0.35))
        arcs.set_z_index(1)
        long_arc = arcs[6]   # node 0 → node 7
        self.wait_to(c.at("a self-attention layer"))
        self.play(row_band.animate.move_to([row_band.get_x(), ROW_Y["sa"], 0]), FadeOut(links), FadeOut(hops),
                  FadeOut(sig), self.hl_off(),
                  ends.animate.set_stroke(INK, 2, 0.7).set_fill(INK, 0.05), run_time=0.8)
        self.play_until(c.after("directly"), LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.04))

        # path between any two positions: one hop
        self.wait_to(c.at("so the path"))
        glow_arc = long_arc.copy().set_stroke(NEEDLE, 3.5, 1).set_z_index(3)
        sig.move_to(tops[0])
        self.play(ends.animate.set_stroke(NEEDLE, 2.8, 1).set_fill(NEEDLE, 0.15), Create(glow_arc),
                  FadeIn(sig, scale=0.5), run_time=0.8)
        self.play(MoveAlongPath(sig, long_arc.copy()), run_time=1.0)
        self.play(sig.animate.move_to(cellsq[-1]), run_time=0.2)
        one = sans("1 hop", 19, NEEDLE).next_to(cellsq[-1], UP, buff=0.14).shift(RIGHT * 0.25)
        sa_path = cells["sa"][3]
        self.wait_to(c.at("has length one"))
        self.play_until(c.after("length one"), FadeIn(one, shift=UP * 0.08), FadeIn(sa_path, shift=UP * 0.1),
                        self.hl(sa_path))

        # all of the work at once
        sa_seq = cells["sa"][2]
        self.wait_to(c.at("and all of"))
        self.play(FadeOut(sig), FadeOut(glow_arc), FadeOut(one),
                  ends.animate.set_stroke(INK, 2, 0.7).set_fill(INK, 0.05), run_time=0.4)
        flashes = [ShowPassingFlash(a.copy().set_stroke(NEEDLE, 3, 1), time_width=0.6) for a in arcs]
        self.play(*flashes, *[s.animate(rate_func=there_and_back).set_fill(NEEDLE, 0.35).set_stroke(NEEDLE, 2.6, 1)
                              for s in cellsq],
                  FadeIn(sa_seq, shift=UP * 0.1), self.hl(sa_seq), run_time=c.after("at once") - self.now + 0.3)

        # ── the price: n × n comparisons ──────────────────────────────────────
        cs = 0.19
        N2 = 12
        grid = VGroup()
        for i in range(N2):
            for j in range(N2):
                sq = Square(cs, stroke_color=BG, stroke_width=1.5, fill_color=PURPLE, fill_opacity=0.55)
                grid.add(sq.move_to([(j - (N2 - 1) / 2) * cs, -1.5 - (i - (N2 - 1) / 2) * cs, 0]))
        small = VGroup(*[grid[i * N2 + j] for i in range(8) for j in range(8)])
        extra = VGroup(*[grid[i * N2 + j] for i in range(N2) for j in range(N2) if i >= 8 or j >= 8])
        offset = grid.get_center() - small.get_center()
        small_shift = small.copy().shift(offset)
        lab_nn = mixed("<i>n</i> × <i>n</i>", 32, INK)
        cnt8 = sans("8 words · 64 pairs", 18, MUTED)
        cnt12 = sans("12 words · 144 pairs", 18, MUTED)

        col_band = RoundedRectangle(corner_radius=0.1, width=3.0, height=Y_TOP_RULE - Y_BOT_RULE - 0.06,
                                    stroke_width=0, fill_color=INK, fill_opacity=0.07)
        col_band.move_to([COLS[1], (Y_TOP_RULE + Y_BOT_RULE) / 2, 0]).set_z_index(-1)
        self.wait_to(c.at("the price"))
        self.play(ReplacementTransform(row_band, col_band), FadeOut(arcs), FadeOut(cellsq), self.hl_off(),
                  run_time=0.9)
        self.wait_to(c.at("comparing every word"))
        lab_nn.next_to(small_shift, RIGHT, buff=0.45).shift(UP * 0.2)
        cnt8.next_to(lab_nn, DOWN, buff=0.15, aligned_edge=LEFT)
        self.play(LaggedStart(*[FadeIn(s, scale=0.4) for s in small_shift], lag_ratio=0.02),
                  FadeIn(lab_nn), FadeIn(cnt8), run_time=c.at("grows with the square") - self.now)
        # grows with the square of the length
        lab_target = lab_nn.copy().next_to(grid, RIGHT, buff=0.45).shift(UP * 0.2)
        cnt12.next_to(lab_target, DOWN, buff=0.15, aligned_edge=LEFT)
        sa_cx = cells["sa"][1]
        self.play(Transform(small_shift, small), LaggedStart(*[FadeIn(s, scale=0.4) for s in extra], lag_ratio=0.01),
                  lab_nn.animate.move_to(lab_target), ReplacementTransform(cnt8, cnt12),
                  run_time=c.after("sentence length") - self.now - 0.4)
        self.play(FadeIn(sa_cx, shift=UP * 0.1), self.hl(sa_cx), run_time=0.6)

        # ── ordinary sentences are shorter than the vectors ───────────────────
        unit = 9.8 / 512
        x_bar = -3.75
        n_lbl = mixed("<i>n</i> ≈ 30", 30, INK).move_to([0, -0.42, 0]).align_to([x_bar - 0.35, 0, 0], RIGHT)
        d_lbl = mixed("<i>d</i> = 512", 30, INK).move_to([0, -1.0, 0]).align_to([x_bar - 0.35, 0, 0], RIGHT)
        n_bar = Rectangle(width=30 * unit, height=0.26, stroke_width=0, fill_color=INK, fill_opacity=0.8)
        n_bar.move_to([x_bar, n_lbl.get_y(), 0], aligned_edge=LEFT)
        d_bar = Rectangle(width=512 * unit, height=0.26, stroke_width=0, fill_color=INK, fill_opacity=0.35)
        d_bar.move_to([x_bar, d_lbl.get_y(), 0], aligned_edge=LEFT)
        n_cap = sans("words in a sentence", 18, MUTED).next_to(n_bar, RIGHT, buff=0.2)
        d_cap = sans("numbers per word vector", 18, MUTED).next_to(d_bar, UP, buff=0.1).align_to(d_bar, RIGHT)
        rnn_cx = cells["rnn"][1]
        self.wait_to(c.at("but for sentences"))
        self.play(FadeOut(grid), FadeOut(small_shift), FadeOut(lab_nn), FadeOut(cnt12), self.hl_off(),
                  FadeIn(rnn_cx, shift=UP * 0.1), run_time=0.8)
        self.wait_to(c.at("of ordinary length"))
        self.play(FadeIn(n_lbl), GrowFromEdge(n_bar, LEFT), FadeIn(n_cap), run_time=0.8)
        self.wait_to(c.at("than the vectors"))
        self.play_until(c.after("each word"), FadeIn(d_lbl), GrowFromEdge(d_bar, LEFT), FadeIn(d_cap))

        # cheaper per layer: n²·d vs n·d², computed for n = 30, d = 512
        n, d = 30, 512
        sa_cost, rnn_cost = n * n * d, n * d * d                      # 460,800 and 7,864,320
        cunit = 9.8 / rnn_cost
        y1, y2 = -1.86, -2.44
        sa_l = sans("Self-attention", 20, NEEDLE).move_to([0, y1, 0]).align_to([x_bar - 0.35, 0, 0], RIGHT)
        rnn_l = sans("Recurrent", 20, INK).move_to([0, y2, 0]).align_to([x_bar - 0.35, 0, 0], RIGHT)
        sa_bar = Rectangle(width=sa_cost * cunit, height=0.26, stroke_width=0, fill_color=NEEDLE, fill_opacity=0.9)
        sa_bar.move_to([x_bar, y1, 0], aligned_edge=LEFT)
        rnn_bar = Rectangle(width=rnn_cost * cunit, height=0.26, stroke_width=0, fill_color=INK, fill_opacity=0.35)
        rnn_bar.move_to([x_bar, y2, 0], aligned_edge=LEFT)
        sa_v = mixed(f"30²·512 ≈ {sa_cost / 1e6:.2f} million", 24, NEEDLE).next_to(sa_bar, RIGHT, buff=0.22)
        rnn_v = mixed(f"30·512² ≈ {rnn_cost / 1e6:.1f} million", 24, INK).next_to(rnn_bar, UP, buff=0.1) \
            .align_to(rnn_bar, RIGHT)
        sep = Line([RULE_X[0], -1.42, 0], [RULE_X[1], -1.42, 0], stroke_color=FAINT, stroke_width=1.2)
        self.wait_to(c.at("self-attention turns out"))
        self.play(Create(sep), FadeIn(rnn_l), GrowFromEdge(rnn_bar, LEFT), FadeIn(rnn_v),
                  FadeIn(sa_l), GrowFromEdge(sa_bar, LEFT), FadeIn(sa_v), run_time=1.0)
        self.play_until(c.after("per layer"), sa_cx.animate.set_color(NEEDLE), self.hl(sa_cx),
                        cells["sa"][0].animate.set_color(NEEDLE))
        self.play(sa_path.animate.set_color(NEEDLE), sa_seq.animate.set_color(NEEDLE),
                  self.hl(VGroup(*cells["sa"]), pad=0.2), run_time=0.8)

        self.wait_to(c.dur - 0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.45)
        self.finish()
