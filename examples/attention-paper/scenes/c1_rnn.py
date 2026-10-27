from style import *

EN = ["The", "cat", "sat", "on", "the", "mat"]
DE = ["Die", "Katze", "saß", "auf", "der", "Matte"]
# word tints for "what the hidden state remembers" (teal → coral sweep; avoids the q/k/v and gold roles)
TINTS = ["#5CD0B3", "#7DB0EE", "#A58BE0", "#D184D0", "#EE7F9A", "#F3967A"]

N = 6
XS = [(i - 2.5) * 1.75 for i in range(N)]
Y_CHIP, Y_CELL, Y_VEC = -2.2, -0.8, 0.95
CELL = 0.85


# ── data: a real (tiny) RNN, and real dot-product attention ─────────────────────────────────
def rnn_data():
    """h_t = tanh(W h_{t-1} + U x_t), d_h = 6. Per-cell share of each word in h_t is the
    gradient×input attribution |∂h_t/∂x_j · x_j|, normalised over words. Seed chosen as the first
    whose overall influence on the final state rises monotonically with position."""
    vocab = sorted(set(w.lower() for w in EN))
    for seed in range(200):
        rng = np.random.default_rng(seed)
        dh, dx = 6, 8
        Q, _ = np.linalg.qr(rng.normal(size=(dh, dh)))
        W = 0.85 * Q
        U = rng.normal(size=(dh, dx)) / np.sqrt(dx) * 0.8
        emb = {w: rng.normal(size=dx) for w in vocab}
        X = np.array([emb[w.lower()] for w in EN])
        h, D = np.zeros(dh), []
        for t in range(N):
            h = np.tanh(W @ h + U @ X[t])
            D.append(np.diag(1 - h ** 2))
        shares, contrib = [], []
        for t in range(N):
            C = []
            for j in range(t + 1):
                J = D[j] @ U
                for k in range(j + 1, t + 1):
                    J = D[k] @ W @ J
                C.append(J @ X[j])
            C = np.abs(np.array(C))
            contrib.append(C)
            shares.append(C / C.sum(0))
        infl = np.linalg.norm(contrib[-1], axis=1)
        infl = infl / infl.sum()
        if np.all(np.diff(infl) > 0):
            # how much of word 1 ("cat") survives in h_t, relative to when it was read
            cat = np.array([np.linalg.norm(contrib[t][1]) for t in range(1, N)])
            return shares, infl, cat / cat[0]
    raise RuntimeError("no seed")


def attention_weights(q_word):
    """Toy bilingual embeddings: a word and its translation share a concept vector (plus noise).
    Weights = softmax(q·k / √d) over the English tokens."""
    rng = np.random.default_rng(17)
    d = 16
    concept = {c: 0.6 * rng.normal(size=d) for c in ["art", "cat", "sit", "on", "mat"]}
    en_c = ["art", "cat", "sit", "on", "art", "mat"]
    de_c = dict(zip(DE, ["art", "cat", "sit", "on", "art", "mat"]))
    K = np.array([concept[c] + 0.3 * rng.normal(size=d) for c in en_c])
    q = concept[de_c[q_word]] + 0.3 * rng.normal(size=d)
    s = K @ q / np.sqrt(d)
    w = np.exp(s - s.max())
    return w / w.sum()


# ── drawing helpers ─────────────────────────────────────────────────────────────────────────
def token(s, size=24):
    t = sans(s, size=size, color=INK)
    box = RoundedRectangle(corner_radius=0.12, width=max(t.width + 0.44, 0.78), height=0.56,
                           stroke_color=MUTED, stroke_width=1.6, stroke_opacity=0.75,
                           fill_color=INK, fill_opacity=0.04)
    t.move_to(box)
    return VGroup(box, t)


def state_vector(share, w=0.8, h=0.235, gap=0.05):
    """Six cells; each cell is split left→right (oldest→newest word) by that word's share."""
    rows = VGroup()
    for k in range(6):
        y = (2.5 - k) * (h + gap)
        frame = Rectangle(width=w, height=h, stroke_color=INK, stroke_width=1.3, stroke_opacity=0.6)
        frame.move_to([0, y, 0])
        slices = VGroup()
        x = -w / 2
        for j in range(N):
            sw = max(share[j][k] if j < len(share) else 0.0, 1e-3) * w
            r = Rectangle(width=sw, height=h, stroke_width=0, fill_color=TINTS[j], fill_opacity=0.9)
            r.move_to([x + sw / 2, y, 0])
            slices.add(r)
            x += sw
        rows.add(VGroup(slices, frame))
    return rows


def keyhole(scale=1.0):
    ring = Circle(radius=0.62 * scale).move_to([0, Y_CELL, 0])
    slot = Polygon([-0.26 * scale, Y_CELL - 0.3, 0], [0.26 * scale, Y_CELL - 0.3, 0],
                   [0.68 * scale, Y_CHIP - 0.4 * scale, 0], [-0.68 * scale, Y_CHIP - 0.4 * scale, 0])
    return Union(ring, slot)


class C1RNN(BeatScene):
    BEAT = "c1_rnn"

    def construct(self):
        c = self.cues
        shares, infl, cat_left = rnn_data()

        # ── 1. sequence transduction: English → German ───────────────────────────────────
        en = VGroup(*[token(w) for w in EN]).arrange(RIGHT, buff=0.16).move_to(UP * 1.15)
        de = VGroup(*[token(w) for w in DE]).arrange(RIGHT, buff=0.16).move_to(DOWN * 0.95)
        arrow = Arrow(UP * 0.62, DOWN * 0.42, buff=0, stroke_width=3, color=MUTED,
                      max_tip_length_to_length_ratio=0.25)
        kicker = eyebrow("sequence transduction", color=MUTED, size=16).move_to(UP * 2.75)
        lx = min(en.get_left()[0], de.get_left()[0]) - 0.35
        lab_en = eyebrow("English", size=13).move_to([lx, en.get_y(), 0], aligned_edge=RIGHT)
        lab_de = eyebrow("German", size=13).move_to([lx, de.get_y(), 0], aligned_edge=RIGHT)

        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.15) for t in en], lag_ratio=0.1), run_time=1.0)
        self.play_from(c.at("sequence transduction") - 0.1, FadeIn(kicker, shift=UP * 0.1), run_time=0.8)
        self.wait_to(c.at("turning") - 0.1)
        self.play(GrowArrow(arrow), run_time=0.5)
        self.play_until(c.after("another") + 0.2,
                        LaggedStart(*[FadeIn(t, shift=DOWN * 0.15) for t in de], lag_ratio=0.12))
        self.wait_to(c.at("translating") - 0.1)
        self.play(ShowPassingFlash(arrow.copy().set_stroke(INK, 5, 1), time_width=0.8), run_time=0.7)
        self.wait_to(c.at("english") - 0.1)
        self.play(FadeIn(lab_en, shift=RIGHT * 0.1), run_time=0.45)
        self.play_from(c.at("german") - 0.05, FadeIn(lab_de, shift=RIGHT * 0.1), run_time=0.45)

        # ── 2. "the best systems ... were recurrent neural networks" ────────────────────────
        cells = VGroup(*[RoundedRectangle(corner_radius=0.14, width=CELL, height=CELL, stroke_color=INK,
                                          stroke_width=2, stroke_opacity=0.6, fill_color="#141821",
                                          fill_opacity=1).move_to([x, Y_CELL, 0]) for x in XS])
        ups = VGroup(*[Arrow([x, Y_CHIP + 0.3, 0], [x, Y_CELL - CELL / 2, 0], buff=0.06, stroke_width=2.5,
                             color=MUTED, max_tip_length_to_length_ratio=0.3) for x in XS])
        links = VGroup(*[Arrow(cells[i].get_right(), cells[i + 1].get_left(), buff=0.06, stroke_width=3,
                               color=INK, stroke_opacity=0.7, max_tip_length_to_length_ratio=0.18)
                         for i in range(N - 1)])
        kicker2 = eyebrow("recurrent neural network", color=MUTED, size=16).move_to(UP * 2.75)

        self.wait_to(c.at("at the time") - 0.1)
        self.play(FadeOut(VGroup(de, arrow, lab_en, lab_de), shift=DOWN * 0.15),
                  FadeOut(kicker, shift=UP * 0.1),
                  *[en[i].animate.move_to([XS[i], Y_CHIP, 0]) for i in range(N)], run_time=1.2)
        self.wait_to(c.at("recurrent neural") - 0.2)
        self.play(FadeIn(kicker2, shift=UP * 0.1),
                  LaggedStart(*[AnimationGroup(GrowArrow(ups[i]), FadeIn(cells[i], scale=0.85)) for i in range(N)],
                              lag_ratio=0.15),
                  run_time=1.1)
        self.play(LaggedStart(*[GrowArrow(l) for l in links], lag_ratio=0.2), run_time=0.8)

        # ── 3. the keyhole: one word at a time into the hidden state ─────────────────────────
        # Feathered mask: stacked cut-outs, each a little larger, so the hole has a soft edge.
        mask = VGroup(*[Cutout(Rectangle(width=60, height=40), keyhole(1 + 0.09 * k),
                               fill_color=BG, fill_opacity=0.42, stroke_width=0) for k in range(4)])
        mask.shift(RIGHT * XS[0]).set_z_index(5)
        rim = keyhole(1.0).set_fill(opacity=0).set_stroke(NEEDLE, 1.2, 0.35).shift(RIGHT * XS[0]).set_z_index(6)

        # "A recurrent network reads a sentence": a signal runs along the chain, left to right
        self.wait_to(c.at("reads") - 0.1)
        self.play(LaggedStart(*[ShowPassingFlash(l.copy().set_stroke(INK, 5, 1), time_width=0.7) for l in links],
                              lag_ratio=0.35), run_time=1.3)
        self.wait_to(c.at("like reading") - 0.2)
        self.play(FadeIn(mask), FadeIn(rim), FadeOut(kicker2), run_time=c.after("keyhole") - self.now)

        vec = state_vector(shares[0]).move_to([XS[0], Y_VEC, 0]).set_z_index(10)
        vec_lab = sans("hidden state", size=22, color=MUTED).set_z_index(10)
        vec_lab.add_updater(lambda m: m.next_to(vec, UP, buff=0.22))
        tether = always_redraw(lambda: Line(vec.get_bottom() + DOWN * 0.06,
                                            [vec.get_x(), Y_CELL + CELL / 2 + 0.06, 0],
                                            stroke_color=INK, stroke_width=2, stroke_opacity=0.45).set_z_index(10))

        def read(i):
            """Fold word i: the keyhole slides over, then the chip takes its tint and the state updates."""
            if i > 0:
                d = RIGHT * (XS[i] - XS[i - 1])
                self.play(mask.animate.shift(d), rim.animate.shift(d), cells[i - 1].animate.set_stroke(INK, opacity=0.6),
                          run_time=0.3)
            anims = [en[i][0].animate.set_stroke(TINTS[i], opacity=1).set_fill(TINTS[i], 0.14),
                     ShowPassingFlash(ups[i].copy().set_stroke(TINTS[i], 5).set_z_index(7), time_width=0.6),
                     cells[i].animate.set_stroke(TINTS[i], opacity=0.95)]
            if i > 0:
                anims.append(Transform(vec, state_vector(shares[i]).move_to([XS[i], Y_VEC, 0]).set_z_index(10)))
            else:
                anims += [FadeIn(vec, shift=UP * 0.2), Create(tether)]
            self.play(*anims, run_time=0.45)

        t0, t1 = c.at("one word") - 0.15, c.at("called the hidden") - 0.15
        for i in range(N):
            self.wait_to(t0 + i * (t1 - t0) / (N - 1) - (0.3 if i else 0))
            read(i)
        self.add(vec_lab)
        vec_lab.set_opacity(0)
        self.play_from(c.at("hidden state") - 0.1, vec_lab.animate.set_opacity(1), run_time=0.6)

        # "That design has two costs." — lift the keyhole
        self.wait_to(c.at("that design") - 0.1)
        self.play(FadeOut(mask), FadeOut(rim), cells[N - 1].animate.set_stroke(INK, opacity=0.6), run_time=1.0)

        # ── 4. speed: each step waits for the last; one GPU core busy at a time ───────────────
        chain = VGroup(en, ups, cells, links)
        shift = LEFT * 1.75
        cores = VGroup(*[Square(0.24, stroke_width=0, fill_color=FAINT, fill_opacity=1) for _ in range(64)])
        cores.arrange_in_grid(8, 8, buff=0.085).move_to([4.95, -0.35, 0])
        board = SurroundingRectangle(cores, buff=0.16, corner_radius=0.1, stroke_color=MUTED, stroke_width=1.5,
                                     stroke_opacity=0.6)
        gpu_lab = eyebrow("GPU cores", size=14).next_to(board, UP, buff=0.22)
        gpu = VGroup(board, cores, gpu_lab)

        self.wait_to(c.at("first is speed") - 0.1)
        tether.clear_updaters()
        rest = VGroup(ups, cells, links, *[e[1] for e in en])
        self.play(FadeOut(VGroup(vec, vec_lab, tether)), rest.animate.shift(shift), FadeIn(gpu, shift=LEFT * 0.3),
                  *[en[i][0].animate.shift(shift).set_stroke(MUTED, opacity=0.75).set_fill(INK, 0.04)
                    for i in range(N)],
                  run_time=1.1)
        vec_lab.clear_updaters()

        hot = cells.copy().set_fill(INK, 0.16).set_stroke(INK, 3, 1).set_opacity(0)
        self.add(hot)
        lit = [cores[i].copy().set_fill(INK, 1) for i in range(N)]
        t0, t1 = c.at("every step") - 0.1, c.at("so a long")
        dt = (t1 - t0) / N
        for i in range(N):
            self.wait_to(t0 + i * dt)
            anims = [hot[i].animate.set_opacity(1).set_fill(INK, 0.16), FadeIn(lit[i])]
            if i:
                pulse = Dot(radius=0.07, color=INK).move_to(links[i - 1].get_start())
                anims += [hot[i - 1].animate.set_opacity(0), FadeOut(lit[i - 1]),
                          MoveAlongPath(pulse, Line(links[i - 1].get_start(), links[i - 1].get_end())),
                          ]
            self.play(*anims, run_time=min(0.55, dt * 0.9))
            if i:
                self.remove(pulse)
        # "...the thousands of cores in a modern graphics card": the idle capacity shimmers
        self.wait_to(c.at("thousands") - 0.1)
        self.play(LaggedStart(*[cores[k].animate(rate_func=there_and_back).set_fill(MUTED, 1)
                                for k in range(64)], lag_ratio=0.03), run_time=1.9)

        # ── 5. memory: what it knew about the beginning fades ───────────────────────────────
        self.wait_to(c.at("second is memory") - 0.1)
        self.play(FadeOut(gpu, shift=RIGHT * 0.3), FadeOut(lit[N - 1]), FadeOut(hot[N - 1]),
                  chain.animate.shift(-shift), run_time=1.1)
        self.remove(hot)

        # final hidden state, at the end of the chain, with every word's tint on its chip
        vec = state_vector(shares[N - 1]).move_to([XS[-1], Y_VEC, 0])
        tether = Line(vec.get_bottom() + DOWN * 0.06, [XS[-1], Y_CELL + CELL / 2 + 0.06, 0], stroke_color=INK,
                      stroke_width=2, stroke_opacity=0.45)
        vec_lab = sans("hidden state", size=22, color=MUTED).next_to(vec, UP, buff=0.22)
        self.wait_to(c.at("reaches") - 0.2)
        self.play(FadeIn(vec, shift=UP * 0.2), Create(tether), FadeIn(vec_lab),
                  *[en[i][0].animate.set_stroke(TINTS[i], opacity=1).set_fill(TINTS[i], 0.14) for i in range(N)],
                  run_time=1.0)

        # "what it knew about the beginning": "cat" lights up
        self.wait_to(c.at("beginning") - 0.3)
        self.play(Indicate(en[1], color=TINTS[1], scale_factor=1.12), run_time=0.8)

        # "squeezed through every step in between": its trace hops cell to cell, shrinking by the
        # computed fraction of its influence that survives each step
        r0 = 0.16
        blob = Dot(cells[1].get_center(), radius=r0, color=TINTS[1]).set_z_index(3)
        bglow = glow(Circle(radius=r0, stroke_color=TINTS[1]).move_to(blob), layers=5, max_width=18)[0]
        trace = VGroup(bglow, blob)
        self.play(FadeIn(trace, scale=0.5), run_time=0.4)
        t0, t1 = c.at("squeezed") - 0.1, c.after("between")
        dt = (t1 - t0) / (N - 2)
        for k, j in enumerate(range(2, N)):
            self.wait_to(t0 + k * dt)
            f = max(cat_left[j - 1], 0.04)
            tgt = VGroup(glow(Circle(radius=r0 * np.sqrt(f), stroke_color=TINTS[1]).move_to(cells[j]), layers=5,
                              max_width=18, max_opacity=0.18 * (0.3 + 0.7 * f))[0],
                         Dot(cells[j].get_center(), radius=r0 * np.sqrt(f), color=TINTS[1]).set_opacity(0.3 + 0.7 * f))
            self.play(Transform(trace, tgt, path_arc=-0.6), run_time=dt * 0.85)
        # "... and it fades": chips keep only as much tint as their measured influence on the end state
        self.wait_to(c.at("and it fades") - 0.1)
        m = infl.max()
        self.play(FadeOut(trace),
                  *[en[i][0].animate.set_stroke(TINTS[i], opacity=0.2 + 0.8 * infl[i] / m)
                    .set_fill(TINTS[i], 0.16 * infl[i] / m) for i in range(N)],
                  run_time=c.after("fades") + 0.4 - self.now)

        # ── 6. attention, bolted onto the RNN ───────────────────────────────────────────────
        Y_DCELL, Y_DCHIP = 1.25, 2.7
        dcells = VGroup(*[cells[0].copy().set_stroke(INK, opacity=0.6).move_to([x, Y_DCELL, 0]) for x in XS])
        dlinks = VGroup(*[Arrow(dcells[i].get_right(), dcells[i + 1].get_left(), buff=0.06, stroke_width=3,
                                color=INK, stroke_opacity=0.7, max_tip_length_to_length_ratio=0.18)
                          for i in range(N - 1)])
        de2 = VGroup(*[token(w) for w in DE])
        for i, t in enumerate(de2):
            t.move_to([XS[i], Y_DCHIP, 0])
        douts = VGroup(*[Arrow([x, Y_DCELL + CELL / 2, 0], [x, Y_DCHIP - 0.3, 0], buff=0.06, stroke_width=2.5,
                               color=MUTED, max_tip_length_to_length_ratio=0.3) for x in XS])

        def focus(q):
            """German chips: written ones plain, the current one bright, future ones faint."""
            anims = []
            for i, t in enumerate(de2):
                op = 1.0 if i <= q else 0.28
                anims.append(t[1].animate.set_opacity(op))
                anims.append(t[0].animate.set_stroke(NEEDLE if i == q else MUTED, opacity=0.95 if i == q else 0.7 * op)
                             .set_fill(NEEDLE if i == q else INK, 0.1 if i == q else 0.04 * op))
            return anims

        def arcs_for(q):
            w = attention_weights(DE[q])
            g = VGroup()
            for j in range(N):
                a = ArcBetweenPoints(dcells[q].get_bottom() + DOWN * 0.04, cells[j].get_top() + UP * 0.04,
                                     angle=-0.1 * np.sign(XS[j] - XS[q] + 1e-6))
                a.set_stroke(NEEDLE, width=1.8 + 9 * w[j], opacity=0.4 + 0.6 * w[j] / w.max())
                g.add(a)
            return g, w

        self.wait_to(c.at("researchers") - 0.1)
        self.play(FadeOut(VGroup(vec, vec_lab, tether), shift=UP * 0.15),
                  *[en[i][0].animate.set_stroke(MUTED, opacity=0.75).set_fill(INK, 0.04) for i in range(N)],
                  run_time=0.9)
        for i, t in enumerate(de2):
            op = 1.0 if i <= 1 else 0.28
            t[1].set_opacity(op)
            t[0].set_stroke(NEEDLE if i == 1 else MUTED, opacity=0.95 if i == 1 else 0.7 * op)
            t[0].set_fill(NEEDLE if i == 1 else INK, 0.1 if i == 1 else 0.04 * op)
        self.play_until(c.after("remedy"),
                        LaggedStart(*[AnimationGroup(FadeIn(dcells[i], scale=0.85), GrowArrow(douts[i]),
                                                     FadeIn(de2[i], shift=UP * 0.1)) for i in range(N)],
                                    lag_ratio=0.12),
                        LaggedStart(*[GrowArrow(l) for l in dlinks], lag_ratio=0.2))

        arcs, w = arcs_for(1)
        self.wait_to(c.at("attention") - 0.15)
        self.play(LaggedStart(*[Create(a) for a in arcs], lag_ratio=0.12), run_time=1.1)
        # "look back at every input word directly": a gold pulse runs down every arc at once
        self.wait_to(c.at("look back") - 0.1)
        self.play(*[ShowPassingFlash(a.copy().set_stroke(NEEDLE, width=a.get_stroke_width() + 3, opacity=1),
                                     time_width=0.5) for a in arcs],
                  *[cells[j].animate(rate_func=there_and_back).set_stroke(NEEDLE, opacity=0.4 + 0.6 * w[j] / w.max())
                    for j in range(N)],
                  run_time=1.2)
        # a different output word looks somewhere else: "Matte" ← "mat"
        arcs5, w5 = arcs_for(5)
        self.wait_to(c.at("every input word") + 0.1)
        self.play(Transform(arcs, arcs5), *focus(5), run_time=c.after("directly") + 0.2 - self.now)

        # "But attention was always added on top of a recurrent network": the recurrence glows
        self.wait_to(c.at("always added") - 0.2)
        self.play(*[ShowPassingFlash(l.copy().set_stroke(INK, 6, 1), time_width=0.8) for l in (*links, *dlinks)],
                  VGroup(links, dlinks).animate.set_stroke(INK, opacity=1),
                  VGroup(cells, dcells).animate.set_stroke(INK, opacity=0.95), run_time=1.0)
        self.play_until(c.after("recurrent network", 2) + 0.2,
                        *[ShowPassingFlash(l.copy().set_stroke(INK, 6, 1), time_width=0.8) for l in (*links, *dlinks)])

        # "This paper asks a simple question": the recurrent machinery dissolves; only attention stays
        rnn_parts = VGroup(cells, dcells, links, dlinks, ups, douts)
        Y_EN2, Y_DE2 = -1.7, 1.0
        new_arcs = VGroup()
        for j in range(N):
            a = ArcBetweenPoints([XS[5], Y_DE2 - 0.32, 0], [XS[j], Y_EN2 + 0.32, 0],
                                 angle=-0.1 * np.sign(XS[j] - XS[5] + 1e-6))
            a.set_stroke(NEEDLE, width=1.8 + 9 * w5[j], opacity=0.4 + 0.6 * w5[j] / w5.max())
            new_arcs.add(a)
        self.wait_to(c.at("this paper") - 0.1)
        self.play(LaggedStart(*[FadeOut(m, scale=0.7) for m in rnn_parts], lag_ratio=0.08),
                  *[en[i].animate.move_to([XS[i], Y_EN2, 0]) for i in range(N)],
                  *[de2[i].animate.move_to([XS[i], Y_DE2, 0]) for i in range(N)],
                  Transform(arcs, new_arcs), run_time=c.after("question") - self.now)

        q = MarkupText(f'What if <span foreground="{NEEDLE}">attention</span> were the whole model?',
                       font=SERIF, font_size=42, color=INK, slant=ITALIC).move_to(UP * 2.65)
        self.wait_to(c.at("what if") - 0.1)
        self.play(FadeIn(q, shift=UP * 0.15), run_time=c.after("model") - self.now)

        self.wait_to(c.dur - 0.5)
        self.play(FadeOut(VGroup(q, arcs, en, de2)), run_time=c.dur - self.now)
        self.finish()
