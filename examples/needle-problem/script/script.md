# The Needle Problem — script (as produced)

Target: ~2:30 (delivered 2:43 with pauses) · narrator: ElevenLabs "George" (warm British, professorial) · 1080p60 · 3Blue1Brown-style dark canvas

Narration rules: speak like a university professor explaining to a curious friend. Flowing sentences of
varied length, no dramatic fragments, no lists of statistics, years only where they carry the story.

---

## 1 · The puzzle  (~0:00–0:16)
> In nineteen seventeen, the mathematician Sōichi Kakeya asked a question that sounds like a puzzle for
> children. Imagine a needle lying on a table. What is the smallest region in which you can turn it all
> the way around?

**Visual:** black canvas, a single glowing yellow needle fades in on a faint grid. Small serif caption
"Sōichi Kakeya, 1917". The needle rotates slowly, leaving a translucent trail.

## 2 · No smallest area  (~0:16–0:40)
> Spinning it about its centre sweeps out a disc, and a curved, three-pointed shape called a deltoid
> manages with half the area. But then Abram Besicovitch showed something unsettling, which is that
> there is no smallest area at all: by slicing the motion into ever thinner slivers and sliding them
> over one another, you can make the area as close to zero as you like.

**Visual:** the needle sweeps a blue disc; the disc morphs into a deltoid with the needle gliding inside
it (real deltoid geometry), area bars compare the two. Then a triangle is cut into 2, 4, 8, 16, 32
slivers that slide together into a spiky "Perron tree" — a live area meter (computed from the actual
shapes) falls toward zero.

## 3 · The Kakeya conjecture  (~0:40–1:12)
> So mathematicians asked a subtler question. A set that holds a needle pointing in every direction can
> have almost no area, but can it truly be thin? The Kakeya conjecture says it cannot, and that,
> measured by dimension, a finer notion of size, it must fill out the space it lives in. In the plane
> this was settled long ago, and in three dimensions it was proven only last year, by Hong Wang and
> Joshua Zahl, in work that helped earn Wang a Fields Medal this summer. Beyond that, it remained open.

**Visual:** a fan of needles in every direction, coloured by angle. Zoom into the thin set — it never
becomes "thin" in dimension. A dimension staircase appears: 2D ✓ → 3D (rotating 3D needle fan, short
real clip of Hong Wang / Quanta coverage) ✓ → 4D, 5D, … n D shown as "?" fading into the dark.

## 4 · Waves  (~1:12–1:40)
> Kakeya turns out to be the shadow of a deeper question about waves. When a wave converges, its energy
> can pile up into an intense peak, and in the early nineties Christopher Sogge conjectured that this
> extreme focusing can only last an instant, so that on average a wave is far gentler than at its
> worst. Prove this local smoothing conjecture, and the Kakeya conjecture follows, along with Stein's
> restriction conjecture. Even in two dimensions, it was only proven in twenty nineteen.

**Visual:** a ring wave (simulated) converges to a bright point and disperses; below it a graph of peak
intensity vs time shows one sharp spike and a low average line. Then a diagram: "Local smoothing" on top
with arrows down to "Kakeya" and "Restriction".

## 5 · The result  (~1:40–2:00)
> Today, OpenAI announced that its models have produced a proof of local smoothing in every dimension,
> built on a new kind of auxiliary equation, which would settle Kakeya and restriction in every dimension
> at once. The day after the proof appeared, it had been formalized in Lean, a language in which a
> computer checks each logical step.

**Visual:** the staircase lights up all the way to n. Screenshot of the manuscript title page and
abstract (highlighting "every spatial dimension" and "every Euclidean Kakeya set has full Hausdorff
dimension"). Then the real Lean statement `theorem kakeya` types on, with a green "checked" tick.

## 6 · Close  (~2:00–2:20)
> The mathematical community has only begun to verify it, and that will take time. But consider what is
> being claimed: a problem that has been climbed one dimension at a time, by some of the finest
> analysts alive, carried all the way to the top in a single proof written by a machine. And it was
> one of three such results announced today.

**Visual:** the caution sentence plays over the staircase assembling with "?" on every step (no text slide). Pull back to the staircase climbed in one stroke. Three
cards slide in: Kakeya (maths) · Exponential Time Hypothesis (computer science) · Quantum chromodynamics
(physics). Final shot: the lone needle turning once more, then the title and source line.

---
Sources: OpenAI, "Working with academic communities to build scientific understanding" (Oct 26 2026);
github.com/openai/math — preprints/Local-smoothing-for-the-Euclidean-wave-equation-October-25-2026,
lean/ComparatorChallenges/LocalSmoothing.lean, history.md.
