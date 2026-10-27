"""The recurring motif: a staircase of dimensions. Each step is one dimension; its marker shows status.

    st = Staircase()                       # 2D, 3D, 4D, 5D, 6D, …, nD
    self.play(st.build())                  # draw steps left to right
    self.play(st.mark("2D", "proven"))     # green tick
    self.play(st.mark("3D", "proven"))
    self.play(st.mark("4D", "open"))       # muted question mark
    self.play(st.climb())                  # gold cascade up every step (the AI result)
"""
from style import *

LABELS = ["2D", "3D", "4D", "5D", "6D", "…", "nD"]


class Staircase(VGroup):
    def __init__(self, step_w=1.25, step_h=0.62, origin=LEFT * 4.6 + DOWN * 2.4, **kw):
        super().__init__(**kw)
        self.steps, self.tags, self.marks = {}, {}, {}
        pts = [origin]
        for i, lab in enumerate(LABELS):
            x0, y0 = origin[0] + i * step_w, origin[1] + i * step_h
            pts += [np.array([x0, y0 + step_h, 0]), np.array([x0 + step_w, y0 + step_h, 0])]
            tread = Line([x0, y0 + step_h, 0], [x0 + step_w, y0 + step_h, 0], stroke_color=INK, stroke_width=3)
            tag = sans(lab, size=22, color=MUTED, weight=MEDIUM).move_to([x0 + step_w / 2, y0 + step_h - 0.28, 0])
            self.steps[lab], self.tags[lab] = tread, tag
        self.outline = VMobject(stroke_color=INK, stroke_width=3, stroke_opacity=0.85).set_points_as_corners(pts)
        self.add(self.outline, *self.tags.values())
        self.step_w, self.step_h = step_w, step_h
        self._w0 = self.outline.width

    def build(self, run_time=1.6):
        return AnimationGroup(Create(self.outline, run_time=run_time),
                              LaggedStart(*[FadeIn(t, shift=UP * 0.1) for t in self.tags.values()],
                                          lag_ratio=0.12, run_time=run_time))

    def _marker(self, lab, status):
        # Anchor to the tag (part of this group) so markers follow any move/scale of the staircase.
        k = self.outline.width / self._w0
        top = self.tags[lab].get_center() + UP * 0.70 * k
        if status == "proven":
            m = sans("✓", size=30, color=GREEN, weight=BOLD)
        elif status == "open":
            m = serif("?", size=34, color=MUTED)
        else:  # "ai": gold, glowing dot
            m = glow(Dot(radius=0.11, color=NEEDLE), color=NEEDLE, max_width=26, max_opacity=0.35)
        return m.scale(k).move_to(top)

    def mark(self, lab, status, run_time=0.6):
        anims = []
        if lab in self.marks:
            anims.append(FadeOut(self.marks[lab], scale=0.6))
        m = self._marker(lab, status)
        self.marks[lab] = m
        self.add(m)
        color = {"proven": GREEN, "open": MUTED, "ai": NEEDLE}[status]
        anims += [FadeIn(m, scale=1.4), self.tags[lab].animate.set_color(color if status != "open" else MUTED)]
        return AnimationGroup(*anims, run_time=run_time)

    def climb(self, start="4D", run_time=2.2):
        """Gold cascade from `start` to nD (the new result), with a tracer running up the outline."""
        labs = LABELS[LABELS.index(start):]
        tracer = self.outline.copy().set_stroke(color=NEEDLE, width=6, opacity=1)
        return AnimationGroup(
            ShowPassingFlash(tracer, time_width=0.35, run_time=run_time),
            LaggedStart(*[self.mark(l, "ai") for l in labs], lag_ratio=0.25, run_time=run_time),
        )
