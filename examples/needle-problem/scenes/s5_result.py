import json

from style import *
from staircase import Staircase, LABELS

MONO = "Menlo"
PANEL = "#11141B"

# The real Lean statement (lean/ComparatorChallenges/LocalSmoothing.lean), token-coloured by hand.
LEAN = [
    [("theorem", PURPLE), (" ", None), ("kakeya", BLUE), (" :", MUTED)],
    [("    ", None), ("∀", ORANGE), (" n ", INK), (":", MUTED), (" ℕ", TEAL), (",", MUTED), (" 2", ORANGE),
     (" ≤", ORANGE), (" n ", INK), ("→", MUTED), (" ∀", ORANGE), (" F ", INK), (":", MUTED), (" Set", TEAL),
     (" (", MUTED), ("Space", TEAL), (" n", INK), (")", MUTED), (",", MUTED), (" IsKakeyaSet", BLUE),
     (" F ", INK), ("→", MUTED), (" dimH", BLUE), (" F ", INK), ("=", ORANGE), (" n", INK)],
]


def lean_line(tokens, size=26):
    markup = "".join(
        f'<span foreground="{c}">{t}</span>' if c else t for t, c in tokens
    )
    return MarkupText(markup, font=MONO, font_size=size, color=INK)


def paper_card(width=11.0):
    meta = json.loads((ROOT / "assets/img/ls_abstract.json").read_text())
    img = ImageMobject(str(ROOT / "assets/img/ls_abstract.png")).set_width(width)
    shadow = VGroup(*[
        RoundedRectangle(corner_radius=0.08, width=img.width + 0.12 * i, height=img.height + 0.12 * i,
                         stroke_width=0, fill_color=BLACK, fill_opacity=0.10).shift(DOWN * 0.06 * i)
        for i in range(1, 6)
    ])
    sheet = RoundedRectangle(corner_radius=0.04, width=img.width + 0.1, height=img.height + 0.1,
                             stroke_width=0, fill_color=WHITE, fill_opacity=1)
    card = Group(shadow, sheet, img)

    def boxes(key, color=NEEDLE, pad=0.04):
        W, H = img.width, img.height
        tl = img.get_corner(UL)
        out = VGroup()
        for x0, y0, x1, y1 in meta["boxes"][key]:
            r = Rectangle(width=(x1 - x0) / meta["w"] * W + 2 * pad, height=(y1 - y0) / meta["h"] * H + 2 * pad,
                          stroke_width=0, fill_color=color, fill_opacity=0.38)
            r.move_to(tl + RIGHT * ((x0 + x1) / 2 / meta["w"] * W) + DOWN * ((y0 + y1) / 2 / meta["h"] * H))
            out.add(r)
        return out

    return card, img, boxes


def s4_diagram():
    """Exact rebuild of S4's closing implication diagram (scenes/s4_waves.py §5–6), for continuity."""
    def node(text, color, w=4.4, icon=None):
        t = serif(text, size=38, color=INK)
        content = VGroup(icon, t).arrange(RIGHT, buff=0.3) if icon is not None else t
        box = RoundedRectangle(corner_radius=0.18, width=max(w, content.width + 0.9), height=1.15,
                               stroke_color=color, stroke_width=2.5, fill_color=color, fill_opacity=0.07)
        return VGroup(box, content.move_to(box))

    star = VGroup(*[Line(LEFT * 0.28, RIGHT * 0.28, stroke_color=NEEDLE, stroke_width=3).rotate(k * PI / 6)
                    for k in range(6)])
    cap = Arc(radius=0.34, start_angle=PI * 0.15, angle=PI * 0.7, stroke_color=BLUE, stroke_width=3.5)
    cap_dots = VGroup(*[Dot(cap.point_from_proportion(q), radius=0.035, color=BLUE) for q in (0.15, 0.5, 0.85)])
    top = node("Local smoothing", NEEDLE, w=5.0).move_to(UP * 1.75)
    top_g = VGroup(glow(top[0], color=NEEDLE, max_opacity=0.12), top[1])
    kak = node("Kakeya", INK, icon=star).move_to(DOWN * 1.55 + LEFT * 3.4)
    res = node("Restriction (Stein)", INK, w=5.0, icon=VGroup(cap, cap_dots)).move_to(DOWN * 1.55 + RIGHT * 3.4)
    a1 = Arrow(top.get_bottom() + LEFT * 1.2, kak.get_top(), buff=0.12, stroke_width=4, color=INK,
               max_tip_length_to_length_ratio=0.12)
    a2 = Arrow(top.get_bottom() + RIGHT * 1.2, res.get_top(), buff=0.12, stroke_width=4, color=INK,
               max_tip_length_to_length_ratio=0.12)
    sub = sans("Sogge, 1991", size=20, color=MUTED).next_to(top, UP, buff=0.2)
    note = chip("proven in 2D only · Guth–Wang–Zhang, 2019", color=GREEN, size=19).move_to(DOWN * 3.15)
    return {"all": VGroup(top_g, sub, a1, a2, kak, res, note), "top": top, "arrows": [a1, a2],
            "leaves": [kak, res], "note": note}


class S5Result(BeatScene):
    BEAT = "s5_result"

    def construct(self):
        c = self.cues
        frame = self.camera.frame

        # ── opening state = S4's closing frame ─────────────────────────────────
        d = s4_diagram()
        self.add(d["all"])

        # ── "Today, OpenAI announced…": the whole chain ignites gold ──────────────
        kicker = eyebrow("OpenAI · October 26, 2026", color=NEEDLE, size=18).to_corner(UL, buff=0.6)
        gold_note = chip("claimed in every dimension · OpenAI, 2026", color=NEEDLE, size=19).move_to(d["note"])
        flashes = [ShowPassingFlash(a.copy().set_stroke(color=NEEDLE, width=9), time_width=0.6) for a in d["arrows"]]
        self.wait_to(c.at("OpenAI") - 0.3)
        self.play(FadeIn(kicker, shift=RIGHT * 0.2), Flash(d["top"].get_center(), color=NEEDLE, line_length=0.35,
                                                         flash_radius=2.7, num_lines=16), run_time=0.7)
        d["all"].remove(d["note"])
        self.play(*flashes, *[a.animate.set_color(NEEDLE) for a in d["arrows"]],
                  *[n[0].animate.set_stroke(color=NEEDLE).set_fill(color=NEEDLE, opacity=0.09) for n in d["leaves"]],
                  Succession(FadeOut(d["note"], shift=UP * 0.12, run_time=0.4), FadeIn(gold_note, shift=UP * 0.12, run_time=0.5)), run_time=0.9)

        # ── clear into the staircase; the climb lands on "every dimension" ─────────
        st = Staircase()
        self.play(FadeOut(VGroup(d["all"], gold_note), shift=UP * 0.4), st.build(run_time=1.2), run_time=1.2)
        self.play(st.mark("2D", "proven", run_time=0.35), st.mark("3D", "proven", run_time=0.35),
                  LaggedStart(*[st.mark(l, "open", run_time=0.35) for l in LABELS[2:]], lag_ratio=0.12))

        head = serif("A proof of local smoothing", size=44, color=INK)
        sub = serif("in every dimension", size=44, color=NEEDLE, slant=ITALIC)
        heading = VGroup(head, sub).arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(kicker, DOWN, buff=0.45, aligned_edge=LEFT)
        self.play_until(c.after("smoothing"), FadeIn(head, shift=UP * 0.15))
        self.wait_to(c.at("every") - 0.1)
        self.play(st.climb(run_time=1.5), FadeIn(sub, shift=UP * 0.15, run_time=0.8))
        self.wait_to(c.at("built") - 0.3)

        # ── the manuscript itself, with the key phrases lit ─────────────────────
        card, img, boxes = paper_card()
        card.move_to(DOWN * 0.35)
        cite = credit("Manuscript: github.com/openai/math")
        idea = chip("Key idea: a new auxiliary PDE", color=NEEDLE, size=19).to_corner(UR, buff=0.55)
        self.play(FadeOut(VGroup(st, *st.marks.values(), heading), shift=LEFT * 0.6),
                  FadeIn(card, shift=LEFT * 0.8), FadeIn(cite), run_time=0.9)
        self.play_until(c.after("equation"), FadeIn(idea, shift=DOWN * 0.1))
        hl_dim, hl_kak = boxes("dim"), boxes("kak")
        self.add(hl_dim, hl_kak)
        hl_dim.set_opacity(0)
        hl_kak.set_opacity(0)
        self.play(LaggedStart(*[GrowFromEdge(r.set_fill(opacity=0.38), LEFT) for r in hl_dim], lag_ratio=0.6),
                  run_time=0.8)

        # "settle Kakeya … in every dimension at once": push in on the Kakeya sentence.
        # Overlays (kicker, chip, citation) leave first so nothing is cropped by the pushed frame.
        self.wait_to(c.at("settle") - 0.5)
        self.play(FadeOut(VGroup(kicker, idea, cite)), run_time=0.4)
        frame.save_state()
        focus = np.array([card.get_center()[0], hl_kak.get_center()[1] + 0.75, 0])
        self.play(frame.animate.scale(0.82).move_to(focus),
                  LaggedStart(*[GrowFromEdge(r.set_fill(opacity=0.38), LEFT) for r in hl_kak], lag_ratio=0.6),
                  run_time=1.3)
        self.wait_to(c.at("every", 2) - 0.1)
        self.play(*[Indicate(r, color=NEEDLE, scale_factor=1.04) for r in [*hl_kak, *hl_dim]], run_time=0.9)
        self.wait_to(c.at("The day") - 0.55)
        self.play(Restore(frame), FadeOut(Group(card, hl_dim, hl_kak), shift=LEFT * 0.6), run_time=0.7)

        # ── timeline: proof on the 18th, Lean on the 19th ────────────────────────
        d1, d2 = Dot(LEFT * 2.2, radius=0.07, color=NEEDLE), Dot(RIGHT * 2.2, radius=0.07, color=GREEN)
        link = Line(d1.get_center(), d2.get_center(), stroke_color=MUTED, stroke_width=2)
        l1 = VGroup(sans("Oct 18", size=20, color=NEEDLE, weight=MEDIUM), sans("proof found", size=17, color=MUTED)).arrange(DOWN, buff=0.08).next_to(d1, DOWN, buff=0.18)
        l2 = VGroup(sans("Oct 19", size=20, color=GREEN, weight=MEDIUM), sans("formalized in Lean", size=17, color=MUTED)).arrange(DOWN, buff=0.08).next_to(d2, DOWN, buff=0.18)
        timeline = VGroup(link, d1, d2, l1, l2).scale(1.35).move_to(UP * 0.4)
        self.play(FadeIn(d1, scale=0.5), FadeIn(l1, shift=UP * 0.1), run_time=0.5)
        self.play(Create(link), run_time=0.6)
        self.play_until(c.after("formalized"), FadeIn(d2, scale=0.5), FadeIn(l2, shift=UP * 0.1))

        # ── the Lean statement, typed on ────────────────────────────────────────
        lines = VGroup(*[lean_line(t, size=30) for t in LEAN]).arrange(DOWN, aligned_edge=LEFT, buff=0.32)
        lines[1].shift(RIGHT * 0.7)  # Text drops leading spaces; restore the indent
        lines.scale_to_fit_width(11.2)
        header = sans("Lean 4  ·  github.com/openai/math", size=16, color=MUTED)
        body = VGroup(header, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        panel = RoundedRectangle(corner_radius=0.18, width=body.width + 0.9, height=body.height + 0.8,
                                 fill_color=PANEL, fill_opacity=1, stroke_color=FAINT, stroke_width=1.5)
        rule = Line(panel.get_corner(UL) + RIGHT * 0.18, panel.get_corner(UR) + LEFT * 0.18,
                    stroke_color=GREEN, stroke_width=2.5, stroke_opacity=0.0)
        body.move_to(panel)
        code = VGroup(panel, body, rule).move_to(DOWN * 0.15)
        gloss = serif("every Kakeya set, in every dimension n ≥ 2, has full dimension", size=30,
                      color=INK, slant=ITALIC).next_to(panel, DOWN, buff=0.45)

        self.play(timeline.animate.scale(1 / 1.35).move_to(UP * 2.9), FadeIn(panel, shift=UP * 0.15), FadeIn(header), run_time=0.6)
        for ln, rt in zip(lines, (0.45, 1.2)):
            self.play(ShowIncreasingSubsets(ln, rate_func=linear), run_time=rt)
        self.play(FadeIn(gloss, shift=UP * 0.1), run_time=0.6)

        # "…a computer checks each logical step": a green verification sweep, then the seal.
        self.wait_to(c.at("checks") - 0.15)
        scan = Rectangle(width=0.05, height=panel.height - 0.1, stroke_width=0, fill_color=GREEN, fill_opacity=0.9)
        scan.move_to(panel.get_left() + RIGHT * 0.1)
        tint = Rectangle(width=0.01, height=panel.height - 0.1, stroke_width=0, fill_color=GREEN, fill_opacity=0.07)
        tint.move_to(scan, aligned_edge=LEFT)
        left_x = panel.get_left()[0] + 0.08
        self.add(tint, scan)
        tint.add_updater(lambda m: m.stretch_to_fit_width(max(0.01, scan.get_center()[0] - left_x)).move_to(
            [left_x + max(0.01, scan.get_center()[0] - left_x) / 2, scan.get_center()[1], 0]))
        self.play(scan.animate.move_to(panel.get_right() + LEFT * 0.1),
                  lines.animate.set_opacity(1), run_time=1.1, rate_func=smooth)
        tint.clear_updaters()
        seal = chip("✓  checked by Lean", color=GREEN, size=19).next_to(panel, UP, buff=-0.0).align_to(panel, RIGHT).shift(UP * 0.32)
        self.play(FadeOut(scan), rule.animate.set_stroke(opacity=0.9), FadeIn(seal, shift=DOWN * 0.1), run_time=0.5)

        self.wait_to(c.dur - 0.55)
        self.play(*[FadeOut(m) for m in (timeline, code, gloss, seal, tint)], run_time=0.5)
        self.finish()
