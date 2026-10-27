"""Private helpers for c2_attention and c3_scaled: token chips, shaded vectors, matrix grids."""
from style import *

MONO = "Menlo"
PANEL = "#11141B"


_LOW = set("gjpqy,;()[]{}|/@$·-–—'\"“”‘’*^~")  # glyphs that do not sit on the baseline


def baseline(t, s):
    """Baseline y of a Text built from string s (median bottom of glyphs that sit on the line)."""
    chars = [ch for ch in s if not ch.isspace()]
    ys = [m.get_bottom()[1] for m, ch in zip(t, chars) if ch not in _LOW]
    return float(np.median(ys)) if ys else t.get_bottom()[1]


def set_baseline(t, s, y):
    t.shift(UP * (y - baseline(t, s)))
    return t


def tchip(word, color=INK, size=24, pad=0.17, box_color=None):
    """Neutral token chip (rounded pill); every chip of a size has the same height and the text
    baseline sits at the same place, so a row of chips reads as one line of text."""
    t = sans(word, size=size, color=color, weight=MEDIUM)
    xh = sans("x", size=size, weight=MEDIUM).height
    bc = box_color or MUTED
    h = sans("Tg", size=size, weight=MEDIUM).height + 2 * pad
    box = RoundedRectangle(corner_radius=0.13, width=t.width + 2 * pad + 0.12, height=h,
                           stroke_color=bc, stroke_width=1.5, stroke_opacity=0.55,
                           fill_color=bc, fill_opacity=0.07)
    t.set_x(box.get_x())
    set_baseline(t, word, box.get_y() - xh / 2 - 0.01)
    return VGroup(box, t)


def tint_chip(ch, color, fill=0.14, stroke_opacity=0.95):
    """Animation target: recolour a tchip by role."""
    return [ch[0].animate.set_stroke(color=color, opacity=stroke_opacity).set_fill(color=color, opacity=fill),
            ch[1].animate.set_color(color)]


def _op(v, lo=0.10, hi=0.95, signed=True):
    """Map a value to a fill opacity."""
    if signed:
        x = 0.5 + 0.5 * np.tanh(v)
    else:
        x = float(np.clip(v, 0, 1))
    return lo + (hi - lo) * x


def vec_cells(vals, color, cell=0.2, horizontal=False, signed=True, stroke_w=1.0, gap=0.0, norm=True):
    vals = np.asarray(vals, dtype=float)
    if norm and signed:
        vals = vals / (np.abs(vals).max() + 1e-9) * 1.8   # per-vector contrast for display
    cells = VGroup()
    for v in vals:
        s = Square(side_length=cell, stroke_color=color, stroke_width=stroke_w, stroke_opacity=0.85,
                   fill_color=color, fill_opacity=_op(v, signed=signed))
        cells.add(s)
    cells.arrange(RIGHT if horizontal else DOWN, buff=gap)
    return cells


def grid_cells(M, color, cell=0.3, signed=True, lo=0.08, hi=0.95, stroke_w=1.0, stroke_op=0.6):
    """Matrix as a grid of shaded squares; returns VGroup of rows (each a VGroup of cells)."""
    M = np.asarray(M)
    rows = VGroup()
    for i in range(M.shape[0]):
        r = VGroup()
        for j in range(M.shape[1]):
            r.add(Square(side_length=cell, stroke_color=color, stroke_width=stroke_w, stroke_opacity=stroke_op,
                         fill_color=color, fill_opacity=_op(M[i, j], lo, hi, signed)))
        r.arrange(RIGHT, buff=0)
        rows.add(r)
    rows.arrange(DOWN, buff=0)
    return rows


def softmax(x, axis=-1):
    x = np.asarray(x, dtype=float)
    e = np.exp(x - x.max(axis=axis, keepdims=True))
    return e / e.sum(axis=axis, keepdims=True)


def num(x, size=20, color=INK, digits=2):
    s = f"{x:.{digits}f}".replace("-", "−")
    return sans(s, size=size, color=color)


def mt(markup, size=40, color=INK):
    """Math via Pango markup (LaTeX-like): <i>Q</i><sup><i>T</i></sup>, <i>d</i><sub><i>k</i></sub>."""
    return MarkupText(markup, font=SERIF, font_size=size, color=color)


def radical_bar(sqrt_glyph, radicand, color=None, width=2.0):
    """The vinculum over a √ radicand (Pango draws only the hook)."""
    top = sqrt_glyph.get_top()[1] - 0.012
    return Line([sqrt_glyph.get_right()[0] - 0.02, top, 0], [radicand.get_right()[0] + 0.03, top, 0],
                stroke_width=width, color=color or sqrt_glyph.get_fill_color())
