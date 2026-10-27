"""c6_arch — the full Transformer (Figure 1), assembled part by part in sync with the narration."""
import numpy as np

from style import *

# ── palette for the parts (BLUE/GREEN/ORANGE/NEEDLE stay reserved for Q/K/V/highlight) ──────────
EMB = "#E58FA3"     # embeddings (rose, as in the paper)
ATT = PURPLE        # attention sub-layers
FFN = TEAL          # feed-forward
NRM = "#AEB4C0"     # add & norm (silver plumbing)
OUTC = "#9DB2C9"    # linear / softmax
GHOST = "#3A4150"
FRAME_FILL = "#12161E"
FRAME_LIT = "#4A5160"
LINE = INK

# ── geometry (world units) ──────────────────────────────────────────────────
XE, XD = -2.4, 2.4          # encoder / decoder column centres
W = 2.6                     # sub-layer box width
HW = W / 2
LANE = 1.55                 # residual lane offset from the column centre
B = 1.6                     # bottom of both blocks
ATT_H, NRM_H, FF_H, IO_H = 0.62, 0.30, 0.46, 0.42
FZ = 0.62                   # fork zone: the first sub-layer starts this far above the block bottom
FORK = 0.34                 # height of the Q/K/V fork bar above the block bottom
SPREAD = 0.55               # fork arrow spacing
STACK = np.array([0.06, 0.035, 0])   # offset between stacked copies of a block

# encoder column (centres)
E_MHA = B + FZ + ATT_H / 2
E_AN1 = B + FZ + ATT_H + 0.10 + NRM_H / 2
E_J2 = B + FZ + ATT_H + 0.10 + NRM_H + 0.10           # residual junction before the FFN
E_FF = E_J2 + 0.20 + FF_H / 2
E_AN2 = E_FF + FF_H / 2 + 0.10 + NRM_H / 2
E_TOP = E_AN2 + NRM_H / 2 + 0.15
# decoder column
D_MMHA = E_MHA
D_AN1 = E_AN1
Y_J = D_AN1 + NRM_H / 2 + 0.16                         # stream turns right here (residual + query)
Y_LINK = Y_J + 0.20                                     # encoder output arrives here (keys + values)
D_CMHA = Y_J + 0.60 + ATT_H / 2
D_AN2 = D_CMHA + ATT_H / 2 + 0.10 + NRM_H / 2
D_J3 = D_AN2 + NRM_H / 2 + 0.10
D_FF = D_J3 + 0.20 + FF_H / 2
D_AN3 = D_FF + FF_H / 2 + 0.10 + NRM_H / 2
D_TOP = D_AN3 + NRM_H / 2 + 0.15
LIN_Y, SOFT_Y = D_TOP + 0.47, D_TOP + 1.01
IO_Y, PLUS_Y, TOK_Y = 0.83, 1.32, 0.13
X_MID = 0.0


def view(x0, x1, y0, y1):
    """Camera (centre, height) that fits a box with 0.4/8 side+top margins and a calm bottom band."""
    h = max((y1 - y0) / (1 - 0.05 - 0.1375), (x1 - x0) / (16 / 9 - 0.1))
    yb = y0 - 0.1375 * h
    yt = yb + h
    extra = h - (y1 - y0) - 0.1375 * h - 0.05 * h  # leftover height: split evenly
    return np.array([(x0 + x1) / 2, (yb + yt) / 2 - extra / 2, 0]), h


def rpath(pts, r=0.14, color=LINE, width=2.4, opacity=0.8):
    """Open polyline with rounded corners."""
    pts = [np.array([p[0], p[1], 0.0]) for p in pts]
    m = VMobject(stroke_color=color, stroke_width=width, stroke_opacity=opacity)
    m.start_new_path(pts[0])
    for a, p, c in zip(pts, pts[1:], pts[2:]):
        u, v = (a - p) / np.linalg.norm(a - p), (c - p) / np.linalg.norm(c - p)
        rr = min(r, np.linalg.norm(a - p) / 2, np.linalg.norm(c - p) / 2)
        p1, p2 = p + rr * u, p + rr * v
        m.add_line_to(p1)
        m.add_cubic_bezier_curve_to(p1 + 2 / 3 * (p - p1), p2 + 2 / 3 * (p - p2), p2)
    m.add_line_to(pts[-1])
    m.set_z_index(1)
    return m


def tip_at(end, direction, color=LINE, size=0.11, opacity=0.9):
    d = np.array([direction[0], direction[1], 0.0])
    d /= np.linalg.norm(d)
    t = Triangle(fill_color=color, fill_opacity=opacity, stroke_width=0).set_height(size).stretch(0.85, 0)
    t.rotate(np.arctan2(d[1], d[0]) - PI / 2)
    t.move_to(np.array([end[0], end[1], 0]) - d * size * 0.45)
    t.set_z_index(1)
    return t


def parrow(pts, color=LINE, width=2.4, r=0.14, opacity=0.8, tip=0.11):
    """Rounded polyline ending in a small arrow tip. Returns VGroup(path, tip)."""
    pts = [np.array(p, dtype=float) for p in pts]
    d = pts[-1] - pts[-2]
    d = d / np.linalg.norm(d)
    body = rpath(pts[:-1] + [pts[-1] - d * tip * 0.7], r, color, width, opacity)
    return VGroup(body, tip_at(pts[-1], d, color, tip, min(1, opacity + 0.1)))


def seg(y0, y1, x, tip=True):
    """Straight stream segment up the column; optional arrow tip at the top."""
    if tip:
        return parrow([(x, y0), (x, y1)])
    return rpath([(x, y0), (x, y1)])


class Part(VGroup):
    """A sub-layer box: opaque backing + tinted body + label. Starts as a ghost outline."""

    def __init__(self, label, center, h, hue, w=W, size=18, corner=0.09):
        super().__init__()
        self.hue = hue
        self.back = RoundedRectangle(corner_radius=corner, width=w, height=h, stroke_width=0,
                                     fill_color=FRAME_FILL, fill_opacity=1)
        self.body = RoundedRectangle(corner_radius=corner, width=w, height=h,
                                     stroke_color=GHOST, stroke_width=1.3, stroke_opacity=1,
                                     fill_color=hue, fill_opacity=0)
        self.label = VGroup(*[sans(ln, size=size, color=INK) for ln in label.split("\n")]).arrange(DOWN, buff=0.07)
        if self.label.width > w - 0.25:
            self.label.scale_to_fit_width(w - 0.25)
        self.label.set_opacity(0)
        self.add(self.back, self.body, self.label)
        self.move_to([center[0], center[1], 0])
        self.label.move_to(self.body)
        self.back.set_z_index(2)
        self.body.set_z_index(3)
        self.label.set_z_index(4)

    def lit(self):
        return [self.body.animate.set_stroke(self.hue, 2.0, 0.95).set_fill(self.hue, 0.17),
                self.label.animate.set_opacity(1)]


def pe_icon(center, r=0.2):
    c = Circle(radius=r, stroke_color=INK, stroke_width=2, stroke_opacity=0.85)
    xs = np.linspace(-r * 0.72, r * 0.72, 40)
    wave = VMobject(stroke_color=INK, stroke_width=2, stroke_opacity=0.85)
    wave.set_points_smoothly([np.array([x, 0.42 * r * np.sin(x / (r * 0.72) * PI), 0]) for x in xs])
    g = VGroup(c, wave).move_to([center[0], center[1], 0])
    g.set_z_index(3)
    return g


def oplus(center, r=0.12):
    c = Circle(radius=r, stroke_color=INK, stroke_width=2, fill_color=FRAME_FILL, fill_opacity=1)
    h = Line(LEFT * r * 0.62, RIGHT * r * 0.62, stroke_color=INK, stroke_width=2)
    v = Line(DOWN * r * 0.62, UP * r * 0.62, stroke_color=INK, stroke_width=2)
    g = VGroup(c, h, v).move_to([center[0], center[1], 0])
    g.set_z_index(3)
    return g


def highlight_box(mob, pad=0.09, corner=0.13):
    r = RoundedRectangle(corner_radius=corner, width=mob.width + 2 * pad, height=mob.height + 2 * pad,
                         stroke_color=NEEDLE, stroke_width=3).move_to(mob)
    g = glow(r, NEEDLE, layers=5, max_width=16, max_opacity=0.22)
    g.set_z_index(8)
    return g


def token_row(words, x):
    row = VGroup(*[chip(w, color=INK, size=16, pad=0.11) for w in words]).arrange(RIGHT, buff=0.08)
    for t in row:
        t[0].set_fill(opacity=0.06).set_stroke(opacity=0.5)
    return row.move_to([x, TOK_Y, 0])


def dim_tokens(row, a):
    """Fade chip text/outline only (keeps the chip fill translucent)."""
    out = []
    for t in row:
        out += [t[1].animate.set_opacity(a), t[0].animate.set_stroke(opacity=0.5 * a)]
    return out


class C6Arch(BeatScene):
    BEAT = "c6_arch"

    # ── helpers ─────────────────────────────────────────────────────────────
    def cam(self, v):
        c, h = v
        return self.camera.frame.animate.move_to(c).set(height=h)

    def hl(self, target, pad=0.09):
        """Animation moving the gold reading-cursor onto target (creates it on first use)."""
        new = highlight_box(target, pad)
        if self.cursor is None:
            self.cursor = new
            return FadeIn(new, scale=1.04)
        return Transform(self.cursor, new)

    def hl_off(self):
        cur, self.cursor = self.cursor, None
        return FadeOut(cur)

    def flash(self, path, color=NEEDLE, width=6, tw=0.35):
        p = path.copy().set_stroke(color, width, 1)
        p.set_z_index(1.5)
        return ShowPassingFlash(p, time_width=tw)

    def construct(self):
        c = self.cues
        self.cursor = None
        fr = self.camera.frame

        # ── all parts, as ghosts ────────────────────────────────────────────
        e_emb = Part("Input Embedding", (XE, IO_Y), IO_H, EMB)
        d_emb = Part("Output Embedding", (XD, IO_Y), IO_H, EMB)
        e_mha = Part("Multi-Head\nAttention", (XE, E_MHA), ATT_H, ATT)
        e_an1 = Part("Add & Norm", (XE, E_AN1), NRM_H, NRM, size=16)
        e_ff = Part("Feed Forward", (XE, E_FF), FF_H, FFN)
        e_an2 = Part("Add & Norm", (XE, E_AN2), NRM_H, NRM, size=16)
        d_mmha = Part("Masked Multi-Head\nAttention", (XD, D_MMHA), ATT_H, ATT)
        d_an1 = Part("Add & Norm", (XD, D_AN1), NRM_H, NRM, size=16)
        d_cmha = Part("Multi-Head\nAttention", (XD, D_CMHA), ATT_H, ATT)
        d_an2 = Part("Add & Norm", (XD, D_AN2), NRM_H, NRM, size=16)
        d_ff = Part("Feed Forward", (XD, D_FF), FF_H, FFN)
        d_an3 = Part("Add & Norm", (XD, D_AN3), NRM_H, NRM, size=16)
        lin = Part("Linear", (XD, LIN_Y), 0.34, OUTC, size=17)
        soft = Part("Softmax", (XD, SOFT_Y), 0.34, OUTC, size=17)
        parts = [e_emb, d_emb, e_mha, e_an1, e_ff, e_an2, d_mmha, d_an1, d_cmha, d_an2, d_ff, d_an3, lin, soft]
        dec_parts = [d_emb, d_mmha, d_an1, d_cmha, d_an2, d_ff, d_an3]

        def frame(x0, x1, y0, y1):
            f = RoundedRectangle(corner_radius=0.2, width=x1 - x0, height=y1 - y0,
                                 stroke_color=GHOST, stroke_width=1.3, fill_color=FRAME_FILL, fill_opacity=0.0)
            return f.move_to([(x0 + x1) / 2, (y0 + y1) / 2, 0]).set_z_index(0)

        e_frame = frame(XE - 1.8, XE + 1.55, B, E_TOP)
        d_frame = frame(XD - 1.55, XD + 1.8, B, D_TOP)

        enc_lbl = serif("Encoder", 30, INK)
        n_e = unicode_math("N = 6", 26, MUTED)
        VGroup(enc_lbl, n_e).arrange(DOWN, buff=0.22, aligned_edge=RIGHT) \
            .next_to(e_frame, LEFT, buff=0.38).set_y(e_frame.get_y())
        dec_lbl = serif("Decoder", 30, INK)
        n_d = unicode_math("N = 6", 26, MUTED)
        VGroup(dec_lbl, n_d).arrange(DOWN, buff=0.22, aligned_edge=LEFT) \
            .next_to(d_frame, RIGHT, buff=0.38 + 5 * STACK[0]).set_y(d_frame.get_y())

        # camera views, fitted to the content they must show
        L = enc_lbl.get_left()[0]
        R = dec_lbl.get_right()[0]
        v_full0 = view(L - 0.1, R + 0.1, TOK_Y - 0.2, SOFT_Y + 0.17)
        v_enc = view(L - 0.1, -0.2, TOK_Y - 0.2, E_TOP + 0.4)
        v_dec = view(L - 0.1, R + 0.4, TOK_Y - 0.2, D_TOP + 5 * STACK[1] + 0.05)

        fr.move_to(v_full0[0]).set(height=v_full0[1])

        # ── "the whole machine, in the diagram most people remember" ────────
        ghosts = VGroup(e_frame, d_frame, *[p.body for p in parts])
        backs = VGroup(*[p.back for p in parts])
        self.play(FadeIn(backs, run_time=0.8),
                  LaggedStart(*[Create(g) for g in ghosts], lag_ratio=0.06, run_time=2.4))
        for p in parts:
            self.add(p)
        self.wait_to(c.at("diagram"))
        self.play(ghosts.animate.set_stroke(color="#59606F"), run_time=c.after("from the paper") - self.now,
                  rate_func=there_and_back_with_pause)

        # ── encoder ─────────────────────────────────────────────────────────
        far = VGroup(d_frame, *[p.body for p in dec_parts])
        self.wait_to(c.at("on the left"))
        self.play(self.cam(v_enc), e_frame.animate.set_stroke(FRAME_LIT, 1.6).set_fill(FRAME_FILL, 1),
                  far.animate.set_stroke(opacity=0.45), VGroup(lin, soft).animate.set_opacity(0),
                  FadeIn(enc_lbl, shift=RIGHT * 0.15), run_time=c.at("reads") - self.now)

        toks_in = token_row(["The", "cat", "sat", "on", "the", "mat"], XE)
        in_lbl = sans("Inputs", 15, MUTED).next_to(toks_in, LEFT, buff=0.25)
        self.play_until(c.after("input sentence"),
                        LaggedStart(*[FadeIn(t, shift=UP * 0.12) for t in toks_in], lag_ratio=0.12),
                        FadeIn(in_lbl))

        # embedding
        a_emb = parrow([(XE, TOK_Y + 0.25), (XE, IO_Y - IO_H / 2)])
        self.wait_to(c.at("each word becomes"))
        self.play(Create(a_emb), run_time=0.5)
        self.play_until(c.after("embedding vector"), *e_emb.lit(), self.hl(e_emb), *dim_tokens(toks_in, 0.6))

        # positional encoding
        e_plus = oplus((XE, PLUS_Y))
        e_pe = pe_icon((XE - 0.62, PLUS_Y))
        e_pe_line = rpath([(XE - 0.42, PLUS_Y), (XE - 0.12, PLUS_Y)])
        e_pe_lbl = sans("Positional\nEncoding", 15, MUTED).next_to(e_pe, LEFT, buff=0.18)
        e_a_plus = rpath([(XE, IO_Y + IO_H / 2), (XE, PLUS_Y - 0.12)])
        self.wait_to(c.at("plus its"))
        self.play(Create(e_a_plus), FadeIn(e_plus, scale=0.6), run_time=0.45)
        self.play_until(c.after("positional encoding"), FadeIn(e_pe, shift=RIGHT * 0.1), Create(e_pe_line),
                        FadeIn(e_pe_lbl, shift=RIGHT * 0.1), self.hl(VGroup(e_pe, e_plus), pad=0.1))

        # into the block
        stem_e = rpath([(XE, PLUS_Y + 0.12), (XE, B + FORK)])
        self.wait_to(c.at("passes through"))
        self.play(Create(stem_e), self.hl(e_frame, pad=0.06), run_time=c.after("two parts") - self.now)

        # multi-head self-attention
        self.wait_to(c.at("multi-head self-attention") - 0.2)
        self.play_until(c.after("multi-head self-attention"), *e_mha.lit(), self.hl(e_mha))

        def fork(xc, y_box):
            xs = (xc - SPREAD, xc, xc + SPREAD)
            arrows, labels = VGroup(), VGroup()
            for x, col, letter in zip(xs, (ORANGE, GREEN, BLUE), "VKQ"):
                pts = [(xc, B + FORK), (x, B + FORK), (x, y_box)] if abs(x - xc) > 1e-6 else [(xc, B + FORK), (x, y_box)]
                arrows.add(parrow(pts, color=col, width=2.6, r=0.1, opacity=0.95, tip=0.1))
                lab = sans(letter, 14, col, weight=BOLD).move_to([x + 0.15, (B + FORK + y_box) / 2 + 0.03, 0])
                labels.add(lab.set_z_index(4))
            return arrows, labels

        e_fork, e_fork_l = fork(XE, E_MHA - ATT_H / 2)
        self.wait_to(c.at("where every word"))
        self.play(LaggedStart(*[Create(a) for a in e_fork], lag_ratio=0.2), FadeIn(e_fork_l), run_time=0.9)
        att_glow = e_mha.body.copy().set_fill(opacity=0).set_stroke(ATT, 7, 0.0).set_z_index(5)
        self.add(att_glow)
        self.play(att_glow.animate.set_stroke(opacity=0.7), rate_func=there_and_back, run_time=1.3)
        self.remove(att_glow)

        # feed-forward
        e_s1 = seg(E_MHA + ATT_H / 2, E_AN1 - NRM_H / 2, XE)
        e_s2 = seg(E_AN1 + NRM_H / 2, E_FF - FF_H / 2, XE)
        self.wait_to(c.at("and a small"))
        self.play(Create(e_s1), Create(e_s2), run_time=0.5)
        self.play_until(c.after("feed-forward network"), *e_ff.lit(), self.hl(e_ff))

        # applied to each word on its own: one identical small network per word
        minis = VGroup(*[RoundedRectangle(corner_radius=0.04, width=0.3, height=0.26, stroke_color=FFN,
                                          stroke_width=1.6, fill_color=FFN, fill_opacity=0.25)
                         for _ in range(6)]).arrange(RIGHT, buff=0.1).move_to(e_ff).set_z_index(5)
        self.wait_to(c.at("applied to"))
        self.play(e_ff.label.animate.set_opacity(0),
                  LaggedStart(*[FadeIn(m, scale=0.5) for m in minis], lag_ratio=0.12), run_time=1.0)
        self.play(LaggedStart(*[Indicate(m, color=FFN, scale_factor=1.15) for m in minis], lag_ratio=0.15),
                  run_time=1.0)
        self.play(FadeOut(minis), e_ff.label.animate.set_opacity(1), run_time=0.6)

        # residual connections
        e_res1 = parrow([(XE, B + 0.14), (XE - LANE, B + 0.14), (XE - LANE, E_AN1), (XE - HW, E_AN1)])
        e_res2 = parrow([(XE, E_J2), (XE - LANE, E_J2), (XE - LANE, E_AN2), (XE - HW, E_AN2)])
        e_s3 = seg(E_FF + FF_H / 2, E_AN2 - NRM_H / 2, XE)
        self.wait_to(c.at("around each part"))
        self.play(Create(e_s3), run_time=0.4)
        self.play(LaggedStart(Create(e_res1), Create(e_res2), lag_ratio=0.35),
                  self.hl(VGroup(e_res1, e_res2, e_ff), pad=0.08), run_time=c.after("residual connection") - self.now)
        self.wait_to(c.at("adds the input"))
        self.play(self.flash(e_res1[0]), self.flash(e_res2[0]), run_time=1.2)
        self.play(self.flash(e_res1[0]), self.flash(e_res2[0]), run_time=1.0)
        # layer normalisation
        self.wait_to(c.at("followed by"))
        self.play_until(c.after("layer normalisation"), *e_an1.lit(), *e_an2.lit(),
                        self.hl(VGroup(e_an1, e_an2, e_res1)))
        # train stably: a signal runs cleanly up the whole layer
        spine_e = Line([XE, TOK_Y + 0.25, 0], [XE, E_TOP, 0])
        self.wait_to(c.at("together they"))
        self.play(self.flash(spine_e, tw=0.5), self.flash(e_res1[0]), self.flash(e_res2[0]), self.hl_off(),
                  run_time=1.8)

        # six blocks
        stack_e = VGroup(*[e_frame.copy().set_fill(FRAME_FILL, 1).set_stroke("#3A404D", 1.2, 1 - 0.13 * i)
                           .shift(STACK * i).set_z_index(-0.1 * i) for i in range(1, 6)])
        self.wait_to(c.at("the encoder stacks"))
        self.play(LaggedStart(*[FadeIn(s, shift=STACK) for s in stack_e], lag_ratio=0.25),
                  run_time=c.at("these blocks") - self.now)
        self.play(FadeIn(n_e, shift=UP * 0.1), run_time=0.6)
        self.play(*[m.animate(rate_func=there_and_back).set_stroke("#7A8394", 2.0, 1) for m in [e_frame, *stack_e]],
                  run_time=0.9)

        # ── decoder ─────────────────────────────────────────────────────────
        self.wait_to(c.at("on the right") - 0.3)
        self.play(self.cam(v_dec), d_frame.animate.set_stroke(FRAME_LIT, 1.6, 1).set_fill(FRAME_FILL, 1),
                  *[p.body.animate.set_stroke(opacity=1) for p in dec_parts],
                  FadeIn(dec_lbl, shift=LEFT * 0.15), run_time=c.after("decoder") - self.now + 0.3)

        toks_out = token_row(["<s>", "Die", "Katze", "saß", "auf", "der"], XD)
        out_lbl = sans("Outputs\n(shifted right)", 15, MUTED).next_to(toks_out, RIGHT, buff=0.25)
        self.wait_to(c.at("writes the translation"))
        self.play_until(c.after("at a time"),
                        LaggedStart(*[FadeIn(t, shift=UP * 0.12) for t in toks_out], lag_ratio=0.3),
                        FadeIn(out_lbl))

        a_demb = parrow([(XD, TOK_Y + 0.25), (XD, IO_Y - IO_H / 2)])
        d_plus = oplus((XD, PLUS_Y))
        d_pe = pe_icon((XD + 0.62, PLUS_Y))
        d_pe_line = rpath([(XD + 0.42, PLUS_Y), (XD + 0.12, PLUS_Y)])
        d_pe_lbl = sans("Positional\nEncoding", 15, MUTED).next_to(d_pe, RIGHT, buff=0.18)
        d_a_plus = rpath([(XD, IO_Y + IO_H / 2), (XD, PLUS_Y - 0.12)])
        stem_d = rpath([(XD, PLUS_Y + 0.12), (XD, B + FORK)])
        stack_d = VGroup(*[d_frame.copy().set_fill(FRAME_FILL, 1).set_stroke("#3A404D", 1.2, 1 - 0.13 * i)
                           .shift(STACK * i).set_z_index(-0.1 * i) for i in range(1, 6)])
        self.wait_to(c.at("its blocks"))
        self.play(*dim_tokens(toks_out, 0.6), Create(a_demb), *d_emb.lit(), Create(d_a_plus),
                  FadeIn(d_plus), FadeIn(d_pe), Create(d_pe_line), FadeIn(d_pe_lbl), Create(stem_d),
                  run_time=1.0)
        self.play(LaggedStart(*[FadeIn(s, shift=STACK) for s in stack_d], lag_ratio=0.2),
                  FadeIn(n_d, shift=UP * 0.1), run_time=c.at("masked") - self.now)

        # masked self-attention
        d_fork, d_fork_l = fork(XD, D_MMHA - ATT_H / 2)
        self.play_until(c.after("masked self-attention"), *d_mmha.lit(), self.hl(d_mmha),
                        LaggedStart(*[Create(a) for a in d_fork], lag_ratio=0.2), FadeIn(d_fork_l))
        # the mask: each position sees only the words written so far (lower triangle)
        cells = VGroup()
        for i in range(6):
            for j in range(6):
                ok = j <= i
                cells.add(Square(0.1, stroke_width=0.6, stroke_color=BG, fill_color=ATT if ok else FAINT,
                                 fill_opacity=0.85 if ok else 0.6).move_to([j * 0.1, -i * 0.1, 0]))
        cells.move_to([XD + 1.8 + 5 * STACK[0] + 0.5, D_MMHA + 0.06, 0]).set_z_index(5)
        mask_lbl = sans("mask", 13, MUTED).next_to(cells, DOWN, buff=0.08)
        self.wait_to(c.at("over the words"))
        self.play(LaggedStart(*[FadeIn(cl, scale=0.5) for cl in cells], lag_ratio=0.02), FadeIn(mask_lbl),
                  run_time=1.0)
        self.play(*[Indicate(t[1], color=INK, scale_factor=1.12) for t in toks_out],
                  run_time=c.after("so far") - self.now)

        # cross-attention
        d_s1 = seg(D_MMHA + ATT_H / 2, D_AN1 - NRM_H / 2, XD)
        y_cin = D_CMHA - ATT_H / 2
        d_stream2 = rpath([(XD, D_AN1 + NRM_H / 2), (XD, Y_J), (XD + LANE, Y_J)], r=0.1)
        d_res2 = parrow([(XD + LANE - 0.02, Y_J), (XD + LANE, Y_J), (XD + LANE, D_AN2), (XD + HW, D_AN2)])
        d_res1 = parrow([(XD, B + 0.14), (XD + LANE, B + 0.14), (XD + LANE, D_AN1), (XD + HW, D_AN1)])
        q_arrow = parrow([(XD + SPREAD, Y_J), (XD + SPREAD, y_cin)], color=BLUE, width=2.8, opacity=0.95, tip=0.1)
        link = rpath([(XE, E_AN2 + NRM_H / 2), (XE, E_TOP + 0.35), (X_MID, E_TOP + 0.35),
                      (X_MID, Y_LINK), (XD - 0.3, Y_LINK)], r=0.18)
        v_arrow = parrow([(XD - 0.75, Y_LINK), (XD - 0.75, y_cin)], color=ORANGE, width=2.8, opacity=0.95, tip=0.1)
        k_arrow = parrow([(XD - 0.45, Y_LINK), (XD - 0.3, Y_LINK), (XD - 0.3, y_cin)], color=GREEN, width=2.8,
                         opacity=0.95, tip=0.1, r=0.08)
        q_l = sans("Q", 15, BLUE, weight=BOLD).move_to([XD + SPREAD + 0.16, (Y_J + y_cin) / 2 + 0.04, 0])
        k_l = sans("K", 15, GREEN, weight=BOLD).move_to([XD - 0.3 + 0.16, (Y_LINK + y_cin) / 2 + 0.03, 0])
        v_l = sans("V", 15, ORANGE, weight=BOLD).move_to([XD - 0.75 - 0.16, (Y_LINK + y_cin) / 2 + 0.03, 0])
        for m in (q_l, k_l, v_l):
            m.set_z_index(4)

        self.wait_to(c.at("then cross-attention"))
        self.play(FadeOut(cells), FadeOut(mask_lbl), Create(d_s1), Create(d_stream2), Create(d_res1),
                  Create(d_res2), *d_cmha.lit(), self.hl(d_cmha), run_time=c.after("cross-attention") - self.now + 0.3)
        q_path = rpath([(XD, D_AN1), (XD, Y_J), (XD + SPREAD, Y_J), (XD + SPREAD, y_cin)], r=0.1)
        self.wait_to(c.at("whose queries"))
        self.play(Create(q_arrow), FadeIn(q_l), self.hl(VGroup(q_arrow, d_cmha), pad=0.1), run_time=0.7)
        self.play(self.flash(q_path, BLUE, 7, 0.6), run_time=c.after("from the decoder") - self.now)
        self.wait_to(c.at("while its keys"))
        self.play(Create(link), run_time=c.at("values") - self.now)
        self.play(Create(k_arrow), Create(v_arrow), FadeIn(k_l), FadeIn(v_l),
                  self.hl(VGroup(d_cmha, v_arrow, k_arrow, q_arrow), pad=0.1), run_time=0.6)
        self.play(self.flash(link, GREEN, 7, 0.4), run_time=c.after("from the encoder") - self.now)
        # consults the original sentence: the source words light up and flow across
        self.wait_to(c.at("which is how"))
        self.play(*dim_tokens(toks_in, 1.0), self.flash(spine_e, NEEDLE, 6, 0.5), run_time=1.0)
        self.play(self.flash(link, ORANGE, 7, 0.45), self.flash(link, GREEN, 4, 0.3), run_time=1.1)
        self.play(*dim_tokens(toks_in, 0.6), Indicate(d_cmha.label, color=INK, scale_factor=1.06),
                  run_time=min(1.0, c.at("and finally") - self.now))

        # final feed-forward ("the same"), with its norms and residual
        d_s2 = seg(D_CMHA + ATT_H / 2, D_AN2 - NRM_H / 2, XD)
        d_s3 = seg(D_AN2 + NRM_H / 2, D_FF - FF_H / 2, XD)
        d_s4 = seg(D_FF + FF_H / 2, D_AN3 - NRM_H / 2, XD)
        d_res3 = parrow([(XD, D_J3), (XD + LANE, D_J3), (XD + LANE, D_AN3), (XD + HW, D_AN3)])
        self.wait_to(c.at("and finally"))
        self.play(Create(d_s2), Create(d_s3), Create(d_s4), *d_an1.lit(), *d_an2.lit(), run_time=0.7)
        self.play_until(c.after("feed-forward network"), *d_ff.lit(), *d_an3.lit(), Create(d_res3), self.hl(d_ff))

        # ── top: linear, softmax, probabilities ────────────────────────────
        rng = np.random.default_rng(6)
        vocab = ["Matte", "Decke", "Bank", "Treppe", "Katze", "Wiese", "Tür", "Hund", "Straße", "Mauer",
                 "Couch", "Tisch"]
        dim = 64
        E = rng.normal(size=(len(vocab), dim))                                    # output word embeddings
        h = 0.3 * E[0] + 0.2 * E[1] + 0.15 * E[2] + rng.normal(scale=0.5, size=dim)  # decoder's final vector
        logits = E @ h / np.sqrt(dim)
        p = np.exp(logits - logits.max())
        p /= p.sum()
        order = np.argsort(-p)[:5]
        bw, gap = 0.62, 0.28
        base_y = E_TOP + 1.0
        hmax = SOFT_Y - 0.15 - base_y
        x_right = X_MID - 0.55
        x0 = x_right - 0.45 - 4 * (bw + gap) - bw / 2
        bars, blabels = VGroup(), VGroup()
        for k, idx in enumerate(order):
            x = x0 + k * (bw + gap)
            hgt = hmax * p[idx] / p[order[0]]
            col = NEEDLE if k == 0 else INK
            bar = Rectangle(width=bw, height=hgt, stroke_width=0, fill_color=col, fill_opacity=0.9 if k == 0 else 0.4)
            bars.add(bar.move_to([x, base_y + hgt / 2, 0]))
            blabels.add(sans(vocab[idx], 17, NEEDLE if k == 0 else MUTED).next_to([x, base_y, 0], DOWN, buff=0.12))
        dots = sans("…", 22, MUTED).move_to([x_right - 0.2, base_y + 0.12, 0])
        axis = Line([x0 - bw / 2 - 0.12, base_y, 0], [x_right, base_y, 0], stroke_color=FAINT, stroke_width=2)
        pct = sans(f"{p[order[0]] * 100:.0f}%", 18, NEEDLE).next_to(bars[0], UP, buff=0.1)
        chart_lbl = sans("Output Probabilities", 17, INK).move_to([0, SOFT_Y, 0]).align_to([x_right, 0, 0], RIGHT)
        a_prob = parrow([(XD - HW, SOFT_Y), (x_right + 0.15, SOFT_Y)], color=LINE)
        a_lin = parrow([(XD, D_AN3 + NRM_H / 2), (XD, LIN_Y - 0.17)])
        a_soft = parrow([(XD, LIN_Y + 0.17), (XD, SOFT_Y - 0.17)])
        v_full = view(L - 0.1, R + 0.1, TOK_Y - 0.2, max(SOFT_Y + 0.17, pct.get_top()[1]))

        self.wait_to(c.at("at the top") - 0.3)
        self.play(self.cam(v_full), self.hl_off(), VGroup(lin.back, soft.back).animate.set_opacity(1),
                  VGroup(lin.body, soft.body).animate.set_stroke(opacity=1), run_time=1.2)
        self.play_until(c.after("linear layer"), Create(a_lin), *lin.lit(), self.hl(lin))
        self.play_until(c.after("softmax"), Create(a_soft), *soft.lit(), self.hl(soft))
        self.wait_to(c.at("turn the result"))
        self.play(Create(a_prob), Create(axis), FadeIn(chart_lbl), self.hl_off(), run_time=0.8)
        self.wait_to(c.at("a probability") - 0.1)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.12),
                  LaggedStart(*[FadeIn(lb) for lb in blabels], lag_ratio=0.12), FadeIn(dots),
                  run_time=c.at("vocabulary") - self.now)
        self.play(FadeIn(pct, shift=UP * 0.1), run_time=0.4)

        # ── the paper's own Figure 1 beside ours ───────────────────────────
        crop = paper_card(pdf_png(2, (197, 70, 417, 397), name="c6_fig1"), height=SOFT_Y + 0.4)
        crop.move_to([R + 0.8 + crop.width / 2, (SOFT_Y + 0.3) / 2 + 0.05, 0])
        cr = sans("Figure 1 · Vaswani et al., 2017", 17, MUTED).set_opacity(0.7).next_to(crop, DOWN, buff=0.14)
        v_end = view(L - 0.1, crop.get_right()[0] + 0.1, cr.get_bottom()[1], crop.get_top()[1])
        self.play(self.cam(v_end), FadeIn(crop, shift=LEFT * 0.4), FadeIn(cr), run_time=1.1)
        self.wait_to(c.dur - 0.5)
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.45)
        self.finish()
