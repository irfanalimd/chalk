"""c9_legacy — the conclusion, what came next, and the one operation behind it all."""
from style import *

ENC = TEAL       # encoder half of the mini Transformer
DEC = PURPLE     # decoder half
CROP = (100, 358, 512, 524)   # p9 (0-based): "7 Conclusion" through the third paragraph


def mk(markup, size=20, color=INK, font=SANS, weight=NORMAL, slant=NORMAL):
    return MarkupText(markup, font=font, font_size=size, color=color, weight=weight, slant=slant)


def block(color, w=0.62, h=1.25, layers=3):
    """A stack block (encoder or decoder) with faint layer rules."""
    body = RoundedRectangle(corner_radius=0.1, width=w, height=h, stroke_color=color, stroke_width=2,
                            fill_color=color, fill_opacity=0.16)
    rules = VGroup(*[Line(LEFT * (w / 2 - 0.1), RIGHT * (w / 2 - 0.1), stroke_color=color, stroke_width=1.2,
                          stroke_opacity=0.55).shift(UP * (h / 2 - (k + 1) * h / (layers + 1)))
                     for k in range(layers)])
    return VGroup(body, rules)


def token_row(words, size=26, color=INK, gap=0.42, pad=0.2):
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


def year_pill(s):
    t = sans(s, 17, INK, weight=MEDIUM)
    box = RoundedRectangle(corner_radius=0.16, width=t.width + 0.36, height=0.36, stroke_color=MUTED,
                           stroke_width=1.3, fill_color=BG, fill_opacity=1)
    return VGroup(box, t.move_to(box))


def name_label(name, sub=None, sub_color=MUTED, above=True, line_y=0.0):
    """Name on a fixed row (0.95 above / 0.62 below the line); sub-label between name and line (above),
    or under the name (below)."""
    nm = sans(name, 22, INK, weight=MEDIUM)
    g = VGroup(nm)
    if above:
        nm.move_to([0, line_y + 0.98, 0])
        if sub:
            g.add(sans(sub, 15, sub_color).move_to([0, line_y + 0.6, 0]))
    else:
        nm.move_to([0, line_y - 0.62, 0])
        if sub:
            g.add(sans(sub, 15, sub_color).move_to([0, line_y - 0.95, 0]))
    return g


class C9Legacy(BeatScene):
    BEAT = "c9_legacy"

    def construct(self):
        c = self.cues

        # ── 1. the paper's conclusion ──────────────────────────────────────────
        card = paper_card(pdf_png(9, CROP, name="c9_conclusion"), height=4.0).move_to(UP * 0.45)
        img = card[1]

        def p2xy(x, y):
            return np.array([img.get_left()[0] + (x - CROP[0]) / (CROP[2] - CROP[0]) * img.width,
                             img.get_top()[1] - (y - CROP[1]) / (CROP[3] - CROP[1]) * img.height, 0])

        def prect(x0, y0, x1, y1, color=NEEDLE, op=0.3):
            a, b = p2xy(x0, y0), p2xy(x1, y1)
            return Rectangle(width=b[0] - a[0], height=a[1] - b[1], stroke_width=0, fill_color=color,
                             fill_opacity=op).move_to((a + b) / 2)

        cred = sans("Vaswani et al., 2017 · Section 7", 14, MUTED).set_opacity(0.7)
        cred.next_to(card, DOWN, buff=0.12).align_to(img, RIGHT)
        dim = prect(CROP[0], CROP[1], CROP[2], 474.5, BG, 0.55)
        hl1 = prect(106.5, 476.5, 337.5, 487.2, NEEDLE, 0.32)
        hl_words = [prect(138.4, 509.3, 170.6, 519.6), prect(170.6, 509.3, 195.0, 519.6),
                    prect(195.0, 509.3, 235.2, 519.6)]
        und = Line(p2xy(139, 520.6), p2xy(235, 520.6), stroke_color=NEEDLE, stroke_width=3)

        self.play(FadeIn(card, shift=UP * 0.15), FadeIn(cred), run_time=0.9)
        frame = self.camera.frame
        frame.save_state()
        push = lambda fr, dt: fr.scale(1 - 0.006 * dt)
        frame.add_updater(push)
        self.play_until(c.after("is modest"), FadeIn(dim))
        self.wait_to(c.at("excited") - 0.15)
        self.play_until(c.after("attentionbased models"), GrowFromEdge(hl1, LEFT), rate_func=linear)
        for w, r in zip(("images", "audio", "video"), hl_words):
            self.wait_to(c.at(w) - 0.1)
            self.play(GrowFromEdge(r, LEFT), run_time=0.4, rate_func=linear)
        self.play(Create(und), run_time=0.5)
        paper = Group(card, dim, hl1, *hl_words, und)

        # ── 2. timeline: 2017 → today ─────────────────────────────────────────
        LY = -0.25                                  # timeline y
        X = {"2017": -5.2, "2018": -2.55, "2020": 0.25, "2021": 2.85, "today": 5.3}
        UPY, DNY = LY + 0.62, LY - 0.62             # label rows just above / below the line
        GUP, GDN = LY + 1.95, LY - 1.95             # glyph centres

        line_start = np.array([-6.55, LY, 0])
        def seg(x0, x1):
            return Line([x0, LY, 0], [x1, LY, 0], stroke_color=MUTED, stroke_width=2, stroke_opacity=0.7)

        pills = {k: year_pill(k).move_to([x, LY, 0]) for k, x in X.items()}
        for p in pills.values():
            p.set_z_index(2)

        # 2017: mini Transformer (encoder | decoder) above, the paper below
        enc = block(ENC).move_to([X["2017"] - 0.4, GUP, 0])
        dec = block(DEC).move_to([X["2017"] + 0.4, GUP, 0])
        xattn = Arrow(enc.get_right(), dec.get_left(), buff=0.04, stroke_width=2, color=MUTED,
                      tip_length=0.1, max_tip_length_to_length_ratio=0.5)
        tf_lab = name_label("Transformer", line_y=LY).set_x(X["2017"])
        enc_t = sans("enc", 13, ENC).next_to(enc, UP, buff=0.08)
        dec_t = sans("dec", 13, DEC).next_to(dec, UP, buff=0.08)
        mini = VGroup(enc, dec, xattn, enc_t, dec_t)
        thumb_h = 0.95

        self.wait_to(c.at("that turned out") - 0.05)
        frame.remove_updater(push)
        self.play_until(c.after("understatement") - 0.35,
                        paper.animate.scale(thumb_h / img.height).move_to([X["2017"], GDN + 0.1, 0]), FadeOut(cred),
                        frame.animate.restore(),
                        Create(seg(-6.55, X["2017"])), FadeIn(pills["2017"], scale=0.8),
                        LaggedStart(FadeIn(tf_lab), FadeIn(mini, shift=UP * 0.15), lag_ratio=0.4))

        # 2018: GPT from the decoder, BERT from the encoder
        self.play_until(c.after("a year"), Create(seg(X["2017"], X["2018"])),
                        FadeIn(pills["2018"], scale=0.8))
        gpt_lab = name_label("GPT", "decoder", DEC, line_y=LY).set_x(X["2018"])
        bert_lab = name_label("BERT", "encoder", ENC, above=False, line_y=LY).set_x(X["2018"])
        gpt_blk = dec.copy()
        bert_blk = enc.copy()
        self.wait_to(c.at("gpt") - 0.15)
        self.play(FadeIn(gpt_lab[0], shift=UP * 0.1), run_time=0.5)
        self.wait_to(c.at("transformer's decoder"))
        self.play_until(c.after("decoder") + 0.15, Indicate(dec, color=DEC, scale_factor=1.08),
                        gpt_blk.animate.move_to([X["2018"], GUP, 0]), FadeIn(gpt_lab[1]))
        self.play_until(c.after("bert") + 0.05, FadeIn(bert_lab[0], shift=DOWN * 0.1))
        bert_target = [X["2018"], GDN, 0]
        self.play_until(c.after("its encoder") + 0.2, Indicate(enc, color=ENC, scale_factor=1.08),
                        bert_blk.animate.move_to(bert_target), FadeIn(bert_lab[1]))

        # 2020: Vision Transformer — an image cut into patches, fed to the same block
        vit_lab = name_label("Vision Transformer", line_y=LY).set_x(X["2020"])
        n = 4
        ps = 0.27
        yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
        img_cols = []
        for i in range(n):
            for j in range(n):
                t = 0.55 * yy[i, j] + 0.45 * xx[i, j]          # smooth "landscape" gradient
                col = interpolate_color(ManimColor(BLUE), ManimColor(ORANGE), t)
                if i == n - 1 and j in (1, 2):
                    col = interpolate_color(ManimColor(GREEN), ManimColor(BG), 0.2)
                img_cols.append(col)
        patches = VGroup(*[Square(ps, stroke_width=0, fill_color=col, fill_opacity=0.85)
                           for col in img_cols]).arrange_in_grid(n, n, buff=0)
        patches.move_to([X["2020"] - 0.55, GUP, 0])
        vit_blk = block(ENC).move_to([X["2020"] + 0.75, GUP, 0])
        frame_img = SurroundingRectangle(patches, buff=0, stroke_color=INK, stroke_width=1.2, stroke_opacity=0.5)

        self.wait_to(c.at("vision transformers") - 0.35)
        self.play_until(c.after("vision transformers"), Create(seg(X["2018"], X["2020"])),
                        FadeIn(pills["2020"], scale=0.8), FadeIn(vit_lab), FadeIn(patches), FadeIn(frame_img))
        self.wait_to(c.at("the same blocks") - 0.1)
        self.play_until(c.after("same blocks"), FadeIn(vit_blk, shift=LEFT * 0.15))
        exploded = patches.copy().arrange_in_grid(n, n, buff=0.06).move_to(patches)
        self.play_until(c.after("patches of images"), Transform(patches, exploded), FadeOut(frame_img))
        # patch tokens stream into the block
        stream = VGroup(*[p.copy() for p in patches])
        self.play(LaggedStart(*[p.animate.scale(0.5).move_to(vit_blk.get_center()).set_opacity(0)
                                for p in stream], lag_ratio=0.06), run_time=1.0)
        self.remove(stream)

        # 2021: AlphaFold 2 — a residue chain with attention between residue pairs
        af_lab = name_label("AlphaFold 2", "protein structure", above=False, line_y=LY).set_x(X["2021"])
        cx, cy = X["2021"], GDN - 0.02
        th = np.linspace(0, 1, 70)
        hel = [np.array([cx - 0.95 + 1.6 * t, cy + 0.3 + 0.12 * np.sin(2 * PI * 4.0 * t), 0]) for t in th]
        loop = [np.array([cx + 0.65 + 0.32 * np.sin(PI * u), cy + 0.3 - 0.62 * u, 0]) for u in np.linspace(0, 1, 18)[1:]]
        strand = [np.array([cx + 0.65 - 1.6 * t, cy - 0.32 + 0.05 * np.sin(2 * PI * 7 * t), 0])
                  for t in np.linspace(0, 1, 40)[1:]]
        path_pts = hel + loop + strand
        chain = VMobject(stroke_color=INK, stroke_width=2, stroke_opacity=0.75, fill_opacity=0).set_points_smoothly(path_pts)
        m = 22
        pts = [chain.point_from_proportion(t) for t in np.linspace(0.02, 0.98, m)]
        residues = VGroup(*[Dot(p, radius=0.045, color=INK) for p in pts])
        # pairwise "attention" between residues: softmax over -distance² (computed), local neighbours masked
        P = np.array([p[:2] for p in pts])
        D2 = ((P[:, None, :] - P[None, :, :]) ** 2).sum(-1)
        logits = -D2 / 0.03
        for k in range(m):
            for l in range(m):
                if abs(k - l) < 7:
                    logits[k, l] = -np.inf
        W = np.exp(logits - logits.max(1, keepdims=True))
        W /= W.sum(1, keepdims=True)
        contacts = VGroup()
        n_hel = sum(1 for t in np.linspace(0.02, 0.98, m) if t < 0.42)   # residues on the helix
        for k in range(n_hel):
            l = int(np.argmax(W[k]))
            if l > n_hel + 1 and W[k, l] > 0.3:
                contacts.add(Line(pts[k], pts[l], buff=0.05, stroke_color=NEEDLE, stroke_width=1.6,
                                  stroke_opacity=0.25 + 0.6 * W[k, l]))

        self.wait_to(c.at("and attention became") - 0.1)
        self.play_until(c.after("central part"), Create(seg(X["2020"], X["2021"])),
                        FadeIn(pills["2021"], scale=0.8))
        self.play_until(c.after("protein structure prediction"), FadeIn(af_lab[0]), FadeIn(af_lab[1]),
                        Create(chain), LaggedStart(*[FadeIn(r, scale=0.5) for r in residues], lag_ratio=0.08))
        self.play(LaggedStart(*[Create(l) for l in contacts], lag_ratio=0.2), run_time=0.6)

        # today: language models — a tall decoder stack
        lm_lab = name_label("language models", line_y=LY).set_x(X["today"])
        slabs = VGroup(*[RoundedRectangle(corner_radius=0.05, width=0.9, height=0.17, stroke_color=DEC,
                                          stroke_width=1.5, fill_color=DEC, fill_opacity=0.18 + 0.05 * k)
                         for k in range(8)]).arrange(UP, buff=0.05)
        slabs.move_to([X["today"], GUP + 0.22, 0])
        end_seg = Arrow([X["2021"], LY, 0], [6.6, LY, 0], buff=0, stroke_width=2, color=MUTED,
                        tip_length=0.14, max_tip_length_to_length_ratio=0.1).set_opacity(0.7)
        self.wait_to(c.at("to the language") - 0.1)
        self.play_until(c.after("language models") + 0.1, GrowArrow(end_seg), FadeIn(pills["today"], scale=0.8),
                        FadeIn(lm_lab[0]))
        self.play_until(c.after("every day"),
                        LaggedStart(*[FadeIn(sl, shift=UP * 0.12) for sl in slabs], lag_ratio=0.25))

        # everything after 2017 recedes; the paper's own node stays lit
        veil = Rectangle(width=12.0, height=6.6, stroke_width=0, fill_color=BG, fill_opacity=0.68)
        veil.move_to([-3.85 + 6.0, LY, 0]).set_z_index(5)
        self.wait_to(c.at("most of what") - 0.05)
        self.play_until(c.after("possible"), FadeIn(veil, shift=LEFT * 0.4),
                        mini.animate.set_color(NEEDLE), tf_lab.animate.set_color(NEEDLE))
        pframe = SurroundingRectangle(paper, buff=0.07, stroke_color=NEEDLE, stroke_width=2.5, corner_radius=0.05)
        self.wait_to(c.at("in this short") - 0.2)
        self.play_until(c.after("short paper") + 0.1, Create(pframe))

        # ── 3. one operation: every word looks at every other word ──────────────
        tl_all = Group(*[m_ for m_ in self.mobjects if m_ is not mini])
        words = ["The", "Law", "will", "never", "be", "perfect"]
        chips = token_row(words).move_to(DOWN * 1.15)
        formula = mk(f'Attention(<span foreground="{BLUE}">Q</span>, <span foreground="{GREEN}">K</span>, '
                     f'<span foreground="{ORANGE}">V</span>) = softmax('
                     f'<span foreground="{BLUE}">Q</span><span foreground="{GREEN}">K</span><sup>\u2009T</sup> / √d<sub>k</sub>) '
                     f'<span foreground="{ORANGE}">V</span>', 40, INK, font=SERIF, slant=ITALIC)
        formula.move_to(UP * 2.55)
        halo = glow(formula.copy().set_stroke(NEEDLE, 0), color=NEEDLE, layers=6, max_width=16, max_opacity=0.10)[0]

        # self-attention weights for this sentence: seeded embeddings, random projections, real softmax
        rng = np.random.default_rng(2017)
        d = 16
        E = rng.normal(size=(len(words), d))
        Wq, Wk = rng.normal(size=(d, d)) * 0.5, rng.normal(size=(d, d)) * 0.5
        S = (E @ Wq) @ (E @ Wk).T / np.sqrt(d)
        A = np.exp(S - S.max(1, keepdims=True))
        A /= A.sum(1, keepdims=True)
        arcs = {}
        nw = len(words)
        for i in range(nw):
            for j in range(i + 1, nw):
                w = (A[i, j] + A[j, i]) / 2
                def port(k, other):
                    wk = chips[k].width * 0.32
                    return chips[k].get_top() + UP * 0.05 + RIGHT * wk * (other - k) / (nw - 1)
                a = ArcBetweenPoints(port(i, j), port(j, i), angle=-PI * 0.62)
                a.set_stroke(NEEDLE, 1.2 + 9 * w, 0.3 + 1.2 * w)
                arcs[(i, j)] = a
        arc_grp = VGroup(*arcs.values())

        self.play_until(c.at("a single operation") + 0.25, FadeOut(tl_all), FadeOut(mini, shift=UP * 0.1))
        self.play_until(c.after("single operation") + 0.1, FadeIn(formula, shift=DOWN * 0.1),
                        LaggedStart(*[FadeIn(ch, shift=UP * 0.1) for ch in chips], lag_ratio=0.1))
        # each word in turn looks at all the others
        steps = []
        for i in range(nw):
            mine = [arcs[(min(i, j), max(i, j))] for j in range(nw) if j > i]
            steps.append(AnimationGroup(Indicate(chips[i], color=NEEDLE, scale_factor=1.12),
                                        *[Create(a) for a in mine]))
        self.wait_to(c.at("lets every") - 0.05)
        self.play_until(c.after("other word"), LaggedStart(*steps, lag_ratio=0.55))
        # "at once": every pair lights together
        self.play_until(c.after("at once") + 0.25,
                        *[a.animate.set_stroke(opacity=1).set_stroke(width=a.get_stroke_width() + 1.5)
                          for a in arc_grp],
                        *[ch[0].animate.set_stroke(NEEDLE, opacity=1).set_fill(NEEDLE, 0.18) for ch in chips],
                        FadeIn(halo))
        self.play(*[a.animate.set_stroke(opacity=min(1, 0.3 + 1.2 * ((A[i, j] + A[j, i]) / 2)))
                    for (i, j), a in arcs.items()], run_time=0.6)

        # slow pull-back to the end
        self.camera.frame.add_updater(lambda fr, dt: fr.scale(1 + 0.03 * dt))
        self.wait_to(self.cues.dur - 0.55)
        self.play(*[FadeOut(m_) for m_ in self.mobjects], run_time=0.5)
        self.finish()
