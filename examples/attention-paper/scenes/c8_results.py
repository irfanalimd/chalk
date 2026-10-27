"""c8_results — training and results (Table 2, Sections 5–6 of the paper)."""
from style import *

DIM = "#5B6270"        # bars for earlier systems
CARD = "#141821"       # dark fill for hardware icons
SHEET = "#10131A"


# ── small helpers ────────────────────────────────────────────────────────────
def mk(markup, size=20, color=INK, font=SANS, weight=NORMAL, slant=NORMAL):
    """Pango markup text (for <sup>/<sub>); no LaTeX."""
    return MarkupText(markup, font=font, font_size=size, color=color, weight=weight, slant=slant)


def sci(m, e, size=18, color=MUTED, weight=NORMAL):
    return mk(f"{m} · 10<sup>{e}</sup>", size, color, weight=weight)


def hbar(x0, y, w, h, color, opacity=0.9):
    return Rectangle(width=max(w, 1e-3), height=h, stroke_width=0, fill_color=color,
                     fill_opacity=opacity).move_to([x0 + max(w, 1e-3) / 2, y, 0])


def vbar(x, y0, h, w, color, opacity=0.9):
    return Rectangle(width=w, height=max(h, 1e-3), stroke_width=0, fill_color=color,
                     fill_opacity=opacity).move_to([x, y0 + max(h, 1e-3) / 2, 0])


def token_row(words, size=22, color=INK, gap=0.38, pad=0.2):
    """Token chips that share one text baseline and one box height."""
    full = sans(" ".join(words), size, color, weight=MEDIUM)
    H = full.height + 2 * pad
    yc = full.get_center()[1]
    chips, k = VGroup(), 0
    for w in words:
        g = VGroup(*full[k:k + len(w)]); k += len(w)
        box = RoundedRectangle(corner_radius=0.12, width=g.width + 2 * pad + 0.1, height=H, stroke_color=color,
                               stroke_width=1.5, stroke_opacity=0.7, fill_color=color, fill_opacity=0.08)
        box.move_to([g.get_center()[0], yc, 0])
        chips.add(VGroup(box, g))
    x = 0.0
    for ch in chips:
        ch.shift(RIGHT * (x - ch.get_left()[0])); x = ch.get_right()[0] + gap
    return chips


def gpu_icon(w=1.2, h=0.62):
    body = RoundedRectangle(corner_radius=0.07, width=w, height=h, stroke_color=MUTED, stroke_width=1.4,
                            fill_color=CARD, fill_opacity=1)
    fc = body.get_center() + LEFT * w * 0.2
    fan = Circle(radius=h * 0.31, stroke_color=MUTED, stroke_width=1.3).move_to(fc)
    blades = VGroup(*[Line(ORIGIN, UP * h * 0.25, stroke_color=INK, stroke_width=1.6, stroke_opacity=0.8)
                      .rotate(k * TAU / 5, about_point=ORIGIN) for k in range(5)]).shift(fc)
    hub = Dot(fc, radius=0.03, color=INK)
    vents = VGroup(*[Line(UP * h * 0.22, DOWN * h * 0.22, stroke_color=MUTED, stroke_width=1.1)
                     .shift(body.get_center() + RIGHT * (w * 0.12 + i * 0.075)) for i in range(4)])
    pins = VGroup(*[Rectangle(width=0.05, height=0.06, stroke_width=0, fill_color=NEEDLE, fill_opacity=0.55)
                    .move_to(body.get_bottom() + DOWN * 0.03 + RIGHT * (-w * 0.3 + i * 0.075)) for i in range(9)])
    g = VGroup(body, fan, blades, hub, vents, pins)
    g.blades = blades
    return g


class C8Results(BeatScene):
    BEAT = "c8_results"

    def construct(self):
        c = self.cues
        self.camera.frame.save_state()

        # ── A. benchmarks + hardware ───────────────────────────────────────────
        kicker = eyebrow("WMT 2014 translation").move_to(UP * 3.25)
        de = chip("English → German", color=INK, size=22)
        fr = chip("English → French", color=INK, size=22)
        pair = VGroup(de, fr).arrange(RIGHT, buff=0.5).move_to(UP * 2.45)
        self.play(FadeIn(kicker, shift=DOWN * 0.1), run_time=0.7)
        self.play_until(c.after("german"), FadeIn(de, shift=UP * 0.15))
        self.play_until(c.after("french"), FadeIn(fr, shift=UP * 0.15))

        gpus = VGroup(*[gpu_icon() for _ in range(8)]).arrange_in_grid(2, 4, buff=(0.3, 0.38))
        chassis = RoundedRectangle(corner_radius=0.16, width=gpus.width + 0.7, height=gpus.height + 0.75,
                                   stroke_color=MUTED, stroke_width=1.6, stroke_opacity=0.8,
                                   fill_color=SHEET, fill_opacity=1)
        leds = VGroup(*[Dot(radius=0.035, color=TEAL) for _ in range(3)]).arrange(RIGHT, buff=0.09)
        rack = VGroup(chassis, gpus.move_to(chassis.get_center() + DOWN * 0.03))
        leds.move_to(chassis.get_corner(UR) + LEFT * 0.4 + DOWN * 0.17)
        machine = VGroup(rack, leds).move_to(UP * 0.15)
        hw = sans("8 × NVIDIA P100", 20, MUTED).next_to(chassis, DOWN, buff=0.25)

        self.play_until(c.at("with eight"), Create(chassis), FadeIn(leds))
        self.play_until(c.after("graphics cards") + 0.15,
                        LaggedStart(*[FadeIn(g, shift=UP * 0.15) for g in gpus], lag_ratio=0.18),
                        FadeIn(hw, run_time=0.8))

        # make room: the machine moves up, timeline bars below it
        self.play_until(c.at("base model") + 0.1,
                        FadeOut(kicker), FadeOut(pair, shift=UP * 0.2),
                        VGroup(machine, hw).animate.scale(0.72).move_to(UP * 1.95))

        def spin(m, dt):
            for g in m:
                g.blades.rotate(-4.0 * dt, about_point=g[3].get_center())
        gpus.add_updater(spin)

        # 12 h vs 84 h on a shared hours axis
        X0, SPAN = -3.4, 9.0
        per_h = SPAN / 84
        yb, yB = -0.55, -1.5
        lab_base = sans("Base model", 22, INK).next_to([X0 - 0.25, yb, 0], LEFT, buff=0)
        lab_big = sans("Big model", 22, INK).next_to([X0 - 0.25, yB, 0], LEFT, buff=0)
        t_base = hbar(X0, yb, 12 * per_h, 0.42, NEEDLE, 0.55)
        t_big = hbar(X0, yB, 84 * per_h, 0.42, NEEDLE, 0.9)
        v_base = sans("12 hours", 22, INK, weight=MEDIUM).next_to(t_base, RIGHT, buff=0.2)
        v_big = sans("3.5 days", 22, INK, weight=MEDIUM).next_to(t_big, RIGHT, buff=0.2)
        days = VGroup(*[Line(UP * 0.07, DOWN * 0.07, stroke_color=MUTED, stroke_width=1.2)
                        .move_to([X0 + 24 * k * per_h, yB - 0.38, 0]) for k in range(4)])
        axis = Line([X0, yB - 0.38, 0], [X0 + SPAN, yB - 0.38, 0], stroke_color=FAINT, stroke_width=1.4)
        daylab = VGroup(*[sans(f"day {k}", 14, MUTED).next_to(days[k], DOWN, buff=0.1) for k in range(1, 4)])

        self.play(FadeIn(lab_base), Create(axis), FadeIn(days), FadeIn(daylab), run_time=0.5)
        self.play_until(c.after("twelve hours") + 0.1, GrowFromEdge(t_base, LEFT), rate_func=smooth)
        self.play(FadeIn(v_base, shift=RIGHT * 0.1), run_time=0.4)
        self.wait_to(c.at("and the larger") + 0.05)
        self.play(FadeIn(lab_big), run_time=0.35)
        self.play_until(c.after("half days"), GrowFromEdge(t_big, LEFT), rate_func=smooth)
        self.play(FadeIn(v_big, shift=RIGHT * 0.1), run_time=0.4)

        # ── B. training cost on a log axis (Table 2, EN-DE) ────────────────────
        L0, DEC = -1.9, 2.6            # x of 10^18, units per decade
        def lx(v):
            return L0 + np.log10(v / 1e18) * DEC
        rows = [("Transformer (base)", 3.3e18, ("3.3", "18"), NEEDLE, 0.55),
                ("Transformer (big)", 2.3e19, ("2.3", "19"), NEEDLE, 0.9),
                ("ConvS2S Ensemble", 7.7e19, ("7.7", "19"), DIM, 1.0),
                ("GNMT + RL Ensemble", 1.8e20, ("1.8", "20"), DIM, 1.0)]
        ys = [1.55, 0.65, -0.25, -1.15]
        c_lab, c_bar, c_val = VGroup(), VGroup(), VGroup()
        for (name, v, (m, e), col, op), y in zip(rows, ys):
            c_lab.add(sans(name, 20, INK if col == NEEDLE else MUTED).next_to([L0 - 0.3, y, 0], LEFT, buff=0))
            b = hbar(L0, y, lx(v) - L0, 0.42, col, op)
            c_bar.add(b)
            c_val.add(sci(m, e, 18, INK if col == NEEDLE else MUTED).next_to(b, RIGHT, buff=0.18))
        ax_y = -1.72
        c_axis = Line([L0, ax_y, 0], [L0 + 3 * DEC, ax_y, 0], stroke_color=MUTED, stroke_width=1.4)
        c_ticks = VGroup(*[Line(UP * 0.07, DOWN * 0.07, stroke_color=MUTED, stroke_width=1.4)
                           .move_to([L0 + k * DEC, ax_y, 0]) for k in range(4)])
        c_grid = VGroup(*[DashedLine([L0 + k * DEC, ax_y, 0], [L0 + k * DEC, 1.95, 0], dash_length=0.06,
                                     stroke_color=FAINT, stroke_width=1.2) for k in range(1, 4)]).set_z_index(-2)
        c_tl = VGroup(*[mk(f"10<sup>{18 + k}</sup>", 17, MUTED).next_to(c_ticks[k], DOWN, buff=0.13)
                        for k in range(4)])
        c_title = eyebrow("Training cost · FLOPs · EN→DE").move_to(UP * 2.75)
        c_note = sans("log scale", 14, MUTED).next_to(c_axis, DOWN, buff=0.5).align_to(c_axis, RIGHT)

        self.wait_to(c.at("which was still") - 0.1)
        gpus.clear_updaters()
        self.play_until(c.after("small fraction"),
                        FadeOut(VGroup(machine, hw), shift=UP * 0.2),
                        FadeOut(VGroup(axis, days, daylab, v_base, v_big)),
                        ReplacementTransform(t_base, c_bar[0]), ReplacementTransform(t_big, c_bar[1]),
                        ReplacementTransform(lab_base, c_lab[0]), ReplacementTransform(lab_big, c_lab[1]),
                        FadeIn(VGroup(c_axis, c_ticks, c_tl, c_grid, c_title, c_note)))
        self.play_until(c.after("computation"), FadeIn(c_val[0]), FadeIn(c_val[1]))
        self.wait_to(c.at("spent on") - 0.1)
        self.play_until(c.after("earlier systems"),
                        LaggedStart(*[AnimationGroup(FadeIn(c_lab[i]), GrowFromEdge(c_bar[i], LEFT), FadeIn(c_val[i]))
                                      for i in (2, 3)], lag_ratio=0.35))
        # ratio: big Transformer vs GNMT + RL Ensemble (2.3e19 / 1.8e20 ≈ 1/7.8)
        ry = ys[3] + 0.4
        ratio_ref = DashedLine([lx(2.3e19), ys[1] - 0.24, 0], [lx(2.3e19), ry, 0], dash_length=0.06,
                               stroke_color=NEEDLE, stroke_width=1.4, stroke_opacity=0.7).set_z_index(-1)
        ratio_line = DoubleArrow([lx(2.3e19), ry, 0], [lx(1.8e20), ry, 0], buff=0, stroke_width=2,
                                 color=NEEDLE, tip_length=0.12, max_tip_length_to_length_ratio=0.12)
        ratio_t = sans("≈ 1/8", 18, NEEDLE, weight=MEDIUM).next_to(ratio_line, RIGHT, buff=0.15)
        self.play(Create(ratio_ref), GrowFromCenter(ratio_line), FadeIn(ratio_t), run_time=0.5)
        self.wait_to(c.at("a few of") - 0.1)

        cost_all = VGroup(c_lab, c_bar, c_val, c_axis, c_ticks, c_tl, c_grid, c_title, c_note, ratio_ref, ratio_line, ratio_t)

        # ── C. training recipe: warmup schedule, dropout, label smoothing ──────
        h_lr = sans("Learning rate", 24, MUTED, weight=MEDIUM).move_to([-3.5, 3.1, 0])
        h_do = sans("Dropout", 24, MUTED, weight=MEDIUM)
        h_ls = sans("Label smoothing", 24, MUTED, weight=MEDIUM)
        h_do.move_to([3.6, 3.1, 0])
        h_ls.move_to([3.6, 0.15, 0])
        divider = Line([0.45, 3.3, 0], [0.45, -2.75, 0], stroke_color=FAINT, stroke_width=1.2)
        divider2 = Line([1.0, 0.6, 0], [6.3, 0.6, 0], stroke_color=FAINT, stroke_width=1.2)

        self.play(FadeOut(cost_all), run_time=0.55)
        self.play_until(c.at("standard practice"),
                        LaggedStart(FadeIn(h_lr), FadeIn(h_do), FadeIn(h_ls), lag_ratio=0.3))
        self.play_until(c.after("standard practice"), Create(divider), Create(divider2))

        # learning-rate schedule (Eq. 3): d_model = 512, warmup_steps = 4000, x in steps, y in 1e-4
        ax = Axes(x_range=[0, 60000, 20000], y_range=[0, 8, 2], x_length=5.6, y_length=3.3, tips=False,
                  axis_config={"stroke_color": MUTED, "stroke_width": 1.4, "tick_size": 0.05})
        ax.move_to([-3.35, 0.65, 0])

        def lrate(s):
            s = max(s, 1.0)
            return 512 ** -0.5 * min(s ** -0.5, s * 4000 ** -1.5) * 1e4
        warm = ax.plot(lrate, x_range=[0, 4000, 40], use_smoothing=False, color=TEAL, stroke_width=4)
        decay = ax.plot(lrate, x_range=[4000, 60000, 200], use_smoothing=False, color=TEAL, stroke_width=4)
        xt = VGroup(*[sans(t, 15, MUTED).next_to(ax.c2p(v, 0), DOWN, buff=0.15)
                      for v, t in ((20000, "20K"), (40000, "40K"), (60000, "60K"))])
        xl = sans("training step", 15, MUTED).next_to(ax.c2p(60000, 0), UP, buff=0.15).align_to(ax.c2p(60000, 0), RIGHT)
        peak = ax.c2p(4000, lrate(4000))
        pk_line = DashedLine(ax.c2p(4000, 0), peak, dash_length=0.06, stroke_color=TEAL, stroke_width=1.5,
                             stroke_opacity=0.7)
        pk_lab = sans("warmup: 4000 steps", 16, TEAL).next_to(peak, RIGHT, buff=0.25).shift(UP * 0.05)
        tracer = Dot(ax.c2p(0, 0), radius=0.07, color=WHITE)
        formula = mk('lrate = d<sub>model</sub><sup>−0.5</sup> · min(step<sup>−0.5</sup>, step · warmup<sup>−1.5</sup>)',
                     20, INK, font=SERIF, slant=ITALIC).move_to([-3.35, -1.95, 0])
        if formula.width > 6.0:
            formula.scale_to_fit_width(6.0)

        self.play_until(c.at("learning rate") + 0.2, h_lr.animate.set_color(INK), Create(ax), FadeIn(xt), FadeIn(xl))
        self.add(tracer)
        self.play_until(c.after("warms up"), Create(warm), MoveAlongPath(tracer, warm), rate_func=linear)
        self.play(Create(pk_line), FadeIn(pk_lab, shift=RIGHT * 0.1), run_time=0.35)
        self.play_until(c.after("decays") + 0.3, Create(decay), MoveAlongPath(tracer, decay), rate_func=smooth)

        # dropout: two layers of ten units, one unit per layer zeroed per step (P_drop = 0.1)
        n = 10
        xs = np.linspace(1.55, 5.75, n)
        top = VGroup(*[Circle(0.12, stroke_color=INK, stroke_width=1.5, fill_color=INK, fill_opacity=0.15)
                       .move_to([x, 2.35, 0]) for x in xs])
        bot = VGroup(*[Circle(0.12, stroke_color=INK, stroke_width=1.5, fill_color=INK, fill_opacity=0.15)
                       .move_to([x, 1.3, 0]) for x in xs])
        links = VGroup(*[Line(a.get_center(), b.get_center(), buff=0.13, stroke_color=MUTED, stroke_width=0.8,
                              stroke_opacity=0.28) for a in bot for b in top])
        p_lab = mk("P<sub>drop</sub> = 0.1", 20, MUTED, font=SERIF, slant=ITALIC).next_to(h_do, RIGHT, buff=0.35)
        rng = np.random.default_rng(7)
        masks = [(rng.integers(n), rng.integers(n)) for _ in range(40)]
        t_do = c.at("dropout")
        period = 0.75

        def set_mask(_):
            k = int(max(self.now - t_do, 0) / period) % len(masks)
            mb, mt = masks[k]
            for i, u in enumerate(bot):
                off = i == mb
                u.set_fill(RED if off else INK, 0.0 if off else 0.15).set_stroke(RED if off else INK, opacity=0.5 if off else 1)
            for i, u in enumerate(top):
                off = i == mt
                u.set_fill(RED if off else INK, 0.0 if off else 0.15).set_stroke(RED if off else INK, opacity=0.5 if off else 1)
            for j, l in enumerate(links):
                bi, ti = divmod(j, n)
                l.set_stroke(opacity=0.03 if (bi == mb or ti == mt) else 0.28)

        net = VGroup(links, bot, top)
        self.wait_to(t_do - 0.15)
        self.play_until(c.after("dropout") + 0.1, h_do.animate.set_color(INK), FadeIn(net), FadeIn(p_lab),
                        FadeIn(formula, shift=UP * 0.1))
        net.add_updater(set_mask)

        # label smoothing: one-hot target → 0.9 on the right word, 0.1 spread over the rest (ε_ls = 0.1)
        words = ["Katze", "Hund", "Maus", "Haus", "Tisch"]
        bx = np.linspace(1.75, 5.55, 5)
        base_y, H = -2.2, 1.95
        wl = VGroup(*[sans(w, 17, INK if i == 0 else MUTED).move_to([x, base_y - 0.27, 0]) for i, (w, x) in enumerate(zip(words, bx))])
        baseline = Line([1.25, base_y, 0], [6.05, base_y, 0], stroke_color=MUTED, stroke_width=1.2)
        onehot = [1.0, 0, 0, 0, 0]
        smooth_t = [0.9] + [0.1 / 4] * 4
        bars1 = VGroup(*[vbar(x, base_y, p * H, 0.5, PURPLE if i == 0 else DIM, 0.9) for i, (x, p) in enumerate(zip(bx, onehot))])
        bars2 = VGroup(*[vbar(x, base_y, p * H, 0.5, PURPLE if i == 0 else DIM, 0.9) for i, (x, p) in enumerate(zip(bx, smooth_t))])
        val1 = sans("1.0", 18, INK).next_to(bars1[0], RIGHT, buff=0.12).align_to(bars1[0], UP)
        val2 = sans("0.9", 18, INK).next_to(bars2[0], RIGHT, buff=0.12).align_to(bars2[0], UP)
        sh_y = base_y + 0.3
        share = VGroup(Line([bx[1] - 0.25, sh_y, 0], [bx[4] + 0.25, sh_y, 0], stroke_color=MUTED, stroke_width=1.4),
                       Line([bx[1] - 0.25, sh_y, 0], [bx[1] - 0.25, sh_y - 0.1, 0], stroke_color=MUTED, stroke_width=1.4),
                       Line([bx[4] + 0.25, sh_y, 0], [bx[4] + 0.25, sh_y - 0.1, 0], stroke_color=MUTED, stroke_width=1.4))
        share_t = sans("0.1 spread over the rest", 15, MUTED).next_to(share, UP, buff=0.1)
        eps = mk("ε<sub>ls</sub> = 0.1", 20, MUTED, font=SERIF, slant=ITALIC).next_to(h_ls, RIGHT, buff=0.35)

        self.wait_to(c.at("label smoothing") - 0.1)
        self.play_until(c.after("label smoothing") + 0.2, h_ls.animate.set_color(INK), Create(baseline), FadeIn(wl),
                        GrowFromEdge(bars1[0], DOWN), FadeIn(val1))
        self.add(*bars1[1:])
        self.wait_to(c.at("slightly less") - 0.2)
        self.play_until(c.after("certain") + 0.1, *[Transform(a, b) for a, b in zip(bars1, bars2)],
                        Transform(val1, val2), FadeIn(eps), FadeIn(VGroup(share, share_t)))
        self.wait_to(c.at("the results") - 0.2)

        recipe = VGroup(h_lr, h_do, h_ls, divider, divider2, ax, warm, decay, xt, xl, pk_line, pk_lab, tracer,
                        formula, net, p_lab, wl, baseline, bars1, val1, eps, share, share_t)

        # ── D. the real Table 2 ─────────────────────────────────────────────────
        net.clear_updaters()
        crop = (100, 66, 512, 246)
        card = paper_card(pdf_png(7, crop, name="c8_table2"), height=4.3).move_to(UP * 0.5)
        img = card[1]
        def pdf2xy(x, y):
            return np.array([img.get_left()[0] + (x - crop[0]) / (crop[2] - crop[0]) * img.width,
                             img.get_top()[1] - (y - crop[1]) / (crop[3] - crop[1]) * img.height, 0])
        hl = Rectangle(width=(pdf2xy(505, 0) - pdf2xy(104, 0))[0], height=(pdf2xy(0, 228.6) - pdf2xy(0, 242))[1],
                       stroke_color=NEEDLE, stroke_width=3, fill_color=NEEDLE, fill_opacity=0.14)
        hl.move_to((pdf2xy(104, 228.6) + pdf2xy(505, 242)) / 2)
        cred = sans("Vaswani et al., 2017 · Table 2", 14, MUTED).set_opacity(0.7)
        cred.next_to(card, DOWN, buff=0.12).align_to(img, RIGHT)

        self.play_until(c.after("striking") - 0.1, FadeOut(recipe, run_time=0.5),
                        FadeIn(card, shift=UP * 0.2), FadeIn(cred))
        self.play_until(c.at("on english") + 0.15, Create(hl))

        # ── E. BLEU charts ──────────────────────────────────────────────────────
        def bleu_chart(title, rows, lo, hi, ticks, ys):
            BX0, BW = -0.55, 3.15
            def bx(v):
                return BX0 + (v - lo) / (hi - lo) * BW
            g = VGroup()
            labs, bars, vals = VGroup(), VGroup(), VGroup()
            for (name, sub, v, hero), y in zip(rows, ys):
                nm = sans(name, 19, INK if hero else INK)
                parts = [nm]
                if sub:
                    parts.append(sans(sub, 14, NEEDLE if hero else MUTED))
                lab = VGroup(*parts).arrange(DOWN, aligned_edge=RIGHT, buff=0.07)
                lab.next_to([BX0 - 0.25, y, 0], LEFT, buff=0)
                b = hbar(BX0, y, bx(v) - BX0, 0.4, NEEDLE if hero else DIM, 1.0)
                vt = (sans(f"{v}", 24, NEEDLE, weight=BOLD) if hero else sans(f"{v:.2f}", 18, MUTED))
                vt.next_to(b, RIGHT, buff=0.15)
                labs.add(lab); bars.add(b); vals.add(vt)
            yb_ = ys[-1] - 0.5
            ytop = ys[0] + 0.4
            baseline = Line([BX0, yb_, 0], [BX0, ytop, 0], stroke_color=MUTED, stroke_width=1.4)
            axis_ = Line([BX0, yb_, 0], [BX0 + BW, yb_, 0], stroke_color=MUTED, stroke_width=1.4)
            grid_ = VGroup(*[DashedLine([bx(t), yb_, 0], [bx(t), ytop, 0], dash_length=0.06, stroke_color=FAINT,
                                        stroke_width=1.2) for t in ticks[1:]]).set_z_index(-2)
            tl = VGroup(*[sans(str(t), 15, MUTED).next_to([bx(t), yb_, 0], DOWN, buff=0.13) for t in ticks])
            ttl = eyebrow(title).move_to([0.2, 2.65, 0])
            frame_ = VGroup(baseline, axis_, grid_, tl, ttl)
            g.add(frame_, labs, bars, vals)
            g.bx, g.labs, g.bars, g.vals, g.frame_ = bx, labs, bars, vals, frame_
            return g

        de_rows = [("ConvS2S", "ensemble", 26.36, False), ("GNMT + RL", "ensemble", 26.30, False),
                   ("MoE", None, 26.03, False), ("Transformer (big)", None, 28.4, True)]
        ende = bleu_chart("BLEU · EN → DE", de_rows, 25, 29, [25, 26, 27, 28, 29],
                          [1.65, 0.75, -0.15, -1.05])
        fr_rows = [("ConvS2S", "ensemble", 41.29, False), ("GNMT + RL", "ensemble", 41.16, False),
                   ("Transformer (big)", "single model", 41.8, True)]
        enfr = bleu_chart("BLEU · EN → FR", fr_rows, 40, 42.2, [40, 41, 42], [0.75, -0.15, -1.05])
        enfr.shift(RIGHT * 3.45)
        fr_single = enfr.labs[2][1]
        enfr.labs[2].remove(fr_single)

        self.play_until(c.at("the big transformer"),
                        FadeOut(VGroup(hl, cred)), FadeOut(card, shift=UP * 0.2), FadeIn(ende.frame_),
                        LaggedStart(*[AnimationGroup(FadeIn(ende.labs[i]), GrowFromEdge(ende.bars[i], LEFT),
                                                     FadeIn(ende.vals[i]))
                                      for i in range(3)], lag_ratio=0.25))
        self.play_until(c.at("scored") + 0.1, FadeIn(ende.labs[3]))
        self.play_until(c.after("four bleu"), GrowFromEdge(ende.bars[3], LEFT), rate_func=smooth)
        self.play(FadeIn(ende.vals[3], scale=1.2), run_time=0.45)

        # "+2.04" over the best previous result
        x_prev, x_new = ende.bx(26.36), ende.bx(28.4)
        yT = -1.05
        ref = DashedLine([x_prev, yT + 0.52, 0], [x_prev, yT - 0.28, 0], dash_length=0.06,
                         stroke_color=INK, stroke_width=1.4, stroke_opacity=0.6)
        gap = DoubleArrow([x_prev, yT + 0.36, 0], [x_new, yT + 0.36, 0], buff=0, stroke_width=2, color=NEEDLE,
                          tip_length=0.11, max_tip_length_to_length_ratio=0.15)
        gap_t = sans("+2.04", 17, NEEDLE, weight=MEDIUM).next_to(gap, UP, buff=0.06)
        self.wait_to(c.at("more than two") - 0.1)
        self.play_until(c.after("two points") + 0.2, Create(ref), ende.vals[0].animate.set_color(INK))
        self.play_until(c.after("above"), GrowFromCenter(gap), FadeIn(gap_t))
        self.wait_to(c.at("including ensembles") - 0.1)
        ens = VGroup(ende.labs[0][1], ende.labs[1][1])
        self.play_until(c.after("ensembles") + 0.1, ens.animate.set_color(INK))
        ens_bars = VGroup(ende.bars[0], ende.bars[1])
        self.play_until(c.after("models combined") + 0.2, ens_bars.animate.set_fill("#7E8594"))
        self.play(ens.animate.set_color(MUTED), ens_bars.animate.set_fill(DIM), run_time=0.4)

        # EN-FR beside it
        ende_all = VGroup(ende, ref, gap, gap_t)
        self.wait_to(c.at("on english to french") - 0.15)
        self.play_until(c.after("on english to french") + 0.1, ende_all.animate.shift(LEFT * 3.45))
        self.play_until(c.at("singlemodel") - 0.05, FadeIn(enfr.frame_),
                        LaggedStart(*[AnimationGroup(FadeIn(enfr.labs[i]), GrowFromEdge(enfr.bars[i], LEFT),
                                                     FadeIn(enfr.vals[i])) for i in range(2)], lag_ratio=0.3),
                        FadeIn(enfr.labs[2]))
        self.play_until(c.after("record"), FadeIn(fr_single, shift=DOWN * 0.08))
        self.play_until(c.after("point eight") + 0.1, GrowFromEdge(enfr.bars[2], LEFT), rate_func=smooth)
        self.play(FadeIn(enfr.vals[2], scale=1.2), run_time=0.45)
        self.wait_to(c.at("and to show") - 0.1)

        # ── F. constituency parsing ─────────────────────────────────────────────
        self.play(FadeOut(VGroup(ende_all, enfr, fr_single)), run_time=0.6)
        kick2 = eyebrow("Beyond translation").move_to(UP * 3.1)
        toks = ["The", "cat", "sat", "on", "the", "mat"]
        chips = token_row(toks, size=24, gap=0.42).move_to([-1.6, -2.15, 0])
        tx = [ch.get_x() for ch in chips]
        self.play_until(c.after("specific to translation"), FadeIn(kick2),
                        LaggedStart(*[FadeIn(ch, shift=UP * 0.12) for ch in chips], lag_ratio=0.15))

        self.camera.frame.add_updater(lambda m, dt: m.scale(1 - 0.005 * dt))

        pos = ["DT", "NN", "VBD", "IN", "DT", "NN"]
        py = -1.2
        pnodes = VGroup(*[sans(p, 17, MUTED, weight=MEDIUM).move_to([x, py, 0]) for p, x in zip(pos, tx)])
        pedges = VGroup(*[Line(pnodes[i].get_bottom() + DOWN * 0.06, chips[i].get_top() + UP * 0.06,
                               stroke_color=FAINT, stroke_width=1.6) for i in range(6)])

        def node(label, x, y):
            return sans(label, 20, INK, weight=MEDIUM).move_to([x, y, 0])
        np1 = node("NP", (tx[0] + tx[1]) / 2, -0.3)
        np2 = node("NP", (tx[4] + tx[5]) / 2, -0.3)
        pp = node("PP", (tx[3] + np2.get_x()) / 2, 0.55)
        vp = node("VP", (tx[2] + pp.get_x()) / 2, 1.4)
        s = node("S", (np1.get_x() + vp.get_x()) / 2, 2.25)

        def edge(a, b, col=MUTED):
            return Line(a.get_bottom() + DOWN * 0.06, b.get_top() + UP * 0.06, stroke_color=col, stroke_width=1.6,
                        stroke_opacity=0.8)
        lvl1 = VGroup(edge(np1, pnodes[0]), edge(np1, pnodes[1]), edge(np2, pnodes[4]), edge(np2, pnodes[5]))
        lvl2 = VGroup(edge(pp, pnodes[3]), edge(pp, np2))
        lvl3 = VGroup(edge(vp, pnodes[2]), edge(vp, pp))
        lvl4 = VGroup(edge(s, np1), edge(s, vp))
        cap = eyebrow("English constituency parsing", color=INK).move_to(UP * 3.1)

        self.wait_to(c.at("applied it") - 0.1)
        self.play_until(c.after("parsing"), FadeIn(pnodes, shift=UP * 0.1), Create(pedges),
                        FadeOut(kick2), FadeIn(cap))
        self.play_until(c.after("grammatical structure"),
                        LaggedStart(AnimationGroup(FadeIn(np1), FadeIn(np2), Create(lvl1)),
                                    AnimationGroup(FadeIn(pp), Create(lvl2)), lag_ratio=0.6))
        self.play_until(c.after("english sentences"),
                        LaggedStart(AnimationGroup(FadeIn(vp), Create(lvl3)),
                                    AnimationGroup(FadeIn(s), Create(lvl4)), lag_ratio=0.6))

        # Table 4 (WSJ section 23, F1) — Transformer (4 layers)
        st_t = eyebrow("WSJ §23 · F1").move_to([4.35, 1.35, 0])
        r1n, r1v = sans("WSJ only", 19, MUTED), sans("91.3", 30, INK, weight=BOLD)
        r2n, r2v = sans("semi-supervised", 19, MUTED), sans("92.7", 30, NEEDLE, weight=BOLD)
        for nn, vv, y in ((r1n, r1v, 0.55), (r2n, r2v, -0.3)):
            vv.move_to([2.9, y, 0], aligned_edge=LEFT)
            nn.next_to(vv, RIGHT, buff=0.3)
        st_t.align_to([2.9, 0, 0], LEFT)
        stats_rule = Line([2.9, 1.05, 0], [6.0, 1.05, 0], stroke_color=FAINT, stroke_width=1.2)
        self.wait_to(c.at("where it performed") - 0.1)
        self.play_until(c.after("surprisingly well") + 0.1,
                        LaggedStart(FadeIn(VGroup(st_t, stats_rule)), FadeIn(VGroup(r1n, r1v), shift=LEFT * 0.1),
                                    FadeIn(VGroup(r2n, r2v), shift=LEFT * 0.1), lag_ratio=0.3))
        self.wait_to(self.cues.dur - 0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.45)
        self.finish()
