from style import *

# Title-page crop of the paper (PDF points, page 0): title rule through the end of the abstract.
CLIP = (100, 124, 512, 584)

NAMES = [  # exact, in the paper's order, with their rects on p0
    ("Ashish Vaswani", (132.9, 235.8, 199.8, 244.8)),
    ("Noam Shazeer", (239.1, 235.8, 300.8, 244.8)),
    ("Niki Parmar", (338.7, 235.8, 392.5, 244.8)),
    ("Jakob Uszkoreit", (424.3, 235.8, 493.1, 244.8)),
    ("Llion Jones", (144.3, 285.8, 193.1, 294.8)),
    ("Aidan N. Gomez", (248.8, 285.8, 319.3, 294.8)),
    ("Łukasz Kaiser", (394.1, 285.8, 455.8, 294.8)),
    ("Illia Polosukhin", (268.8, 335.8, 335.9, 344.8)),
]
TITLE_WORDS = [("Attention", (211.5, 150.2, 281.3, 165.6)), ("Is", (285.6, 150.2, 299.0, 165.6)),
               ("All", (303.3, 150.2, 325.3, 165.6)), ("You", (329.6, 150.2, 358.3, 165.6)),
               ("Need", (362.6, 150.2, 399.9, 165.6))]
R_TRANSFORMER = (400.9, 446.9, 467.2, 455.8)       # "the Transformer," in the abstract
R_TASK = (203.3, 414.2, 293.6, 423.1)              # "sequence transduction"
R_IDEA = (143.9, 457.8, 290.4, 466.8)              # "based solely on attention mechanisms"
R_RESULT = (305.0, 490.6, 352.4, 499.5)            # "28.4 BLEU"

FAMILY = ["GPT", "BERT", "T5", "ViT", "Claude", "Gemini", "Llama"]


class C0Open(BeatScene):
    BEAT = "c0_open"

    def construct(self):
        c = self.cues
        frame = self.camera.frame
        home_w = frame.width

        # ── the paper card ───────────────────────────────────────────────
        H = 6.3
        card = paper_card(pdf_png(0, CLIP, dpi=400, name="c0_title_card_124"), height=H)
        card.move_to(LEFT * 3.25 + UP * 0.35)
        img = card[1]
        s = H / (CLIP[3] - CLIP[1])
        x0, y0 = img.get_left()[0], img.get_top()[1]

        def pt(x, y):
            return np.array([x0 + (x - CLIP[0]) * s, y0 - (y - CLIP[1]) * s, 0])

        def rect_of(r, pad=1.2):
            a, b = pt(r[0] - pad, r[1] - pad), pt(r[2] + pad, r[3] + pad)
            return np.array([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2, 0]), b[0] - a[0], a[1] - b[1]

        def highlight(r, opacity=0.38):
            ctr, w, h = rect_of(r)
            hl = Rectangle(width=w, height=h, stroke_width=0, fill_color=NEEDLE, fill_opacity=opacity)
            return hl.move_to(ctr)

        src = sans("Vaswani et al., 2017", size=11, color=MUTED).set_opacity(0.7)
        src.next_to(img, DOWN, buff=0.07, aligned_edge=RIGHT)

        self.drift(0.004)
        self.play(FadeIn(card, shift=LEFT * 0.5), FadeIn(src), run_time=1.0)

        # ── right column: eyebrow, then the eight authors ───────────────
        col_x = 0.75
        brow = MarkupText('<span letter_spacing="1600">ARXIV 1706.03762  ·  JUNE 2017</span>', font=SANS,
                          font_size=16, color=MUTED, weight=MEDIUM)
        brow.set_width(min(brow.width, 5.6))
        brow.move_to([col_x, 2.35, 0], aligned_edge=LEFT)
        rule = Line(ORIGIN, RIGHT * 0.7, stroke_color=NEEDLE, stroke_width=2)
        rule.next_to(brow, DOWN, buff=0.16, aligned_edge=LEFT)
        self.play_until(c.after("seventeen") + 0.15, FadeIn(brow, shift=UP * 0.12), Create(rule))

        names, flights = VGroup(), []
        for i, (n, r) in enumerate(NAMES):
            tgt = sans(n, size=24, color=INK)
            tgt.move_to([col_x + (i % 2) * 3.05, 1.25 - (i // 2) * 0.62, 0], aligned_edge=LEFT)
            names.add(tgt)
            ctr, w, h = rect_of(r, pad=0)
            ghost = tgt.copy().set_color("#222222").set_opacity(0).set_width(w).move_to(ctr)
            flights.append(ReplacementTransform(ghost, tgt, path_arc=-0.35))
        self.wait_to(c.at("eight") - 0.1)
        self.play(LaggedStart(*flights, lag_ratio=0.12), run_time=c.after("google") + 0.3 - self.now)

        # ── "...playful title: Attention Is All You Need" ────────────────
        hl_title = highlight((205, 147, 406, 169), opacity=0.35)
        self.wait_to(c.at("playful") - 0.1)
        self.play(GrowFromEdge(hl_title, LEFT),
                  LaggedStart(*[FadeOut(n, shift=DOWN * 0.15) for n in names], lag_ratio=0.06),
                  run_time=c.after("title") - self.now)

        words = VGroup(*[serif(w, size=50, weight=BOLD) for w, _ in TITLE_WORDS])
        words.arrange(RIGHT, buff=0.2, aligned_edge=DOWN)
        if words.width > 6.0:
            words.set_width(6.0)
        words.move_to([col_x, 0.95, 0], aligned_edge=LEFT)
        t_start = c.at("attention")
        anims = []
        for i, (wd, r) in enumerate(TITLE_WORDS):
            ctr, w, h = rect_of(r, pad=0)
            ghost = words[i].copy().set_color("#222222").set_opacity(0).set_width(w).move_to(ctr)
            delay = c.at(wd) - t_start if i else 0.0
            anims.append(Succession(Wait(delay), ReplacementTransform(ghost, words[i],
                                                                       run_time=0.9)))
        self.wait_to(t_start - 0.15)
        self.play(*anims, run_time=c.at("need") - t_start + 0.9)

        # ── "a new model ... which they called the Transformer" ──────────
        hl_tf = highlight(R_TRANSFORMER)
        self.wait_to(c.at("new model") - 0.05)
        self.play(GrowFromEdge(hl_tf, LEFT), run_time=0.7)

        # Camera flies right to a fresh stage; the word "Transformer" lifts off the page with it.
        stage = np.array([14.5, 0.0, 0])
        block = RoundedRectangle(corner_radius=0.2, width=3.3, height=1.2, stroke_color=NEEDLE,
                                 stroke_width=2.5, fill_color=NEEDLE, fill_opacity=0.07)
        block.move_to(stage + LEFT * 3.4 + UP * 0.3)
        halo = glow(block.copy(), color=NEEDLE, layers=8, max_width=36, max_opacity=0.22)[0]
        label = serif("Transformer", size=42, color=INK).move_to(block)
        ctr, w, h = rect_of((416.8, 446.9, 466.6, 455.8), pad=0)   # "Transformer" (without the comma)
        lift = label.copy().set_color("#222222").set_width(w).move_to(ctr)

        self.wait_to(c.at("translating") + 0.2)
        frame.clear_updaters()
        fly = c.after("transformer") - self.now
        self.play(frame.animate.set_width(home_w).move_to(stage),
                  ReplacementTransform(lift, label, rate_func=smooth),
                  FadeIn(block, rate_func=lambda t: smooth(max(0, (t - 0.55) / 0.45))),
                  run_time=fly)
        self.play(FadeIn(halo), run_time=0.6)
        # off-stage now: clear the left column so the return framing is clean
        self.remove(brow, rule, *words)
        frame.add_updater(lambda m, dt: m.scale(1 - 0.004 * dt))

        # "...the foundation": the glow breathes once
        self.wait_to(c.at("foundation") - 0.1)
        bright = glow(block.copy(), color=NEEDLE, layers=8, max_width=48, max_opacity=0.32)[0]
        self.play(FadeIn(bright), rate_func=there_and_back, run_time=1.2)
        self.remove(bright)

        # "...almost every large language model": a family of descendants grows out of the block
        n = len(FAMILY)
        ys = np.linspace(2.75, -2.15, n) + 0.3
        root = block.get_right()
        branches, kids, dots = VGroup(), VGroup(), VGroup()
        for i, (nm, y) in enumerate(zip(FAMILY, ys)):
            bend = abs(y - 0.3) / 2.5
            end = np.array([stage[0] + 1.6 - 0.55 * bend ** 2, y, 0])
            br = CubicBezier(root, root + RIGHT * 1.6, end + LEFT * 1.6, end,
                             stroke_color=MUTED, stroke_width=2, stroke_opacity=0.55)
            d = Dot(end, radius=0.05, color=NEEDLE)
            kid = sans(nm, size=28, color=INK).next_to(end, RIGHT, buff=0.22)
            branches.add(br)
            dots.add(d)
            kids.add(kid)
        self.wait_to(c.at("large") - 0.2)
        grow = [Succession(Create(br, run_time=0.7), AnimationGroup(FadeIn(d, scale=0.5), FadeIn(k, shift=RIGHT * 0.12),
                                                                     run_time=0.45))
                for br, d, k in zip(branches, dots, kids)]
        self.play(LaggedStart(*grow, lag_ratio=0.16), run_time=c.after("today") + 0.3 - self.now)

        # ── "...read that paper together": back to the page, in to the abstract ──
        tree = VGroup(branches, dots, kids)
        self.wait_to(c.at("in the next") - 0.1)
        frame.clear_updaters()
        read_w = 6.3                    # frame top falls in the white space above "Abstract"
        read_ctr = pt(306, 362) + DOWN * read_w * 9 / 16 / 2
        self.play(frame.animate.set_width(read_w).move_to(read_ctr), run_time=c.after("together") + 0.6 - self.now,
                  rate_func=rate_functions.ease_in_out_cubic)
        self.remove(tree, block, halo, label)
        frame.add_updater(lambda m, dt: m.scale(1 - 0.004 * dt))

        # "from the problem ... through each of its ideas ... to the results"
        for phrase, r in (("problem", R_TASK), ("ideas", R_IDEA), ("results", R_RESULT)):
            hl = highlight(r)
            self.wait_to(c.at(phrase) - 0.05)
            self.play(GrowFromEdge(hl, LEFT), run_time=0.6)
            card.add(hl)

        self.wait_to(c.dur - 0.5)
        frame.clear_updaters()
        self.play(FadeOut(Group(card, src, hl_title, hl_tf)), run_time=self.cues.dur - self.now)
        self.finish()
