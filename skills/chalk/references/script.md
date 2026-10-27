# Research, questions, script

## Research

- Save everything in `research/`: the pasted or fetched announcement, PDFs, code, release notes.
- Follow sublinks to the primary artifact. For the OpenAI Kakeya video the blog post blocked automated
  fetching, but its GitHub repo (`gh api repos/<org>/<repo>/contents/...`) held the manuscript, the Lean
  statement and dated release notes. Those gave the exact claim ("every spatial dimension at least two",
  restriction estimates "throughout the interior of the conjectured range") that press coverage blurred.
- Look for the human story around the result: who came closest before, what prize or recognition it
  carried (a search turned up the 2026 Fields Medal for Hong Wang, which became one strong line), and
  what earlier results have been withdrawn or corrected (useful for calibrating the caution line).
- Write down the 5–8 facts the video depends on, each with its source. Every on-screen year, name and
  quote must trace back to this list.

## Questions to ask (one round)

Offer a recommendation for each so the user can answer in a word:

1. Focus: one main result told well, or several covered briefly? (Recommend one, with a closing line
   that mentions the others.)
2. Caution: how much to say about verification? (Recommend one sober sentence.)
3. Voice: a preference, or pick a calm older narrator? Format: 16:9 1080p60 unless told otherwise.
4. Footage: Creative Commons only, or short fair-use clips too? How many? (Recommend one or two, a few
   seconds each.)

## Story shape for "how big is this breakthrough"

1. **The question in plain terms** (10–15 s). A concrete image a child could picture. Name and year of
   whoever posed it, with an archival photo if one is freely licensed.
2. **Why it is subtle** (20–25 s). The first surprise that made the problem hard.
3. **The real conjecture** (30–35 s). Stated in one sentence, then the ladder of human progress: who
   proved which case, when, and what it earned them. Real footage of a person belongs here.
4. **The deeper engine** (25–30 s). The more general statement the new result actually proves, and why
   it implies the famous one.
5. **The claim** (20–25 s). What was announced, the key idea in one phrase, the artifact (paper page,
   formal statement) on screen.
6. **Close** (20 s). The caution line, the scale of the jump (one proof for every case), and the wider
   context (other results announced alongside).

## Narration rules

- University professor, not a trailer voice. Sentences connect with "and", "but", "so that", "which".
- Avoid: fragments for drama, "Here's the thing", "Let that sink in", "In a world where", "game-changer",
  "mind-blowing", rhetorical triplets, more than one number per sentence, lists of statistics.
- Years only where they move the story; spell them for the TTS ("twenty nineteen").
- Write names the way they should be said; check them with ASR after synthesis.
- Budget ~150 words per minute. A 2:30 video is ~370 words across 6 sections.

## script.md format

```markdown
## 3 · The Kakeya conjecture  (~0:40–1:12)
> So mathematicians asked a subtler question. ...

**Visual:** a fan of needles in every direction ... staircase of dimensions: 2D ✓ → 3D ✓ (real clip of
Hong Wang) → 4D … nD "?".
```

Show the user the narration (all sections, verbatim) and a one-line visual per section, then wait.
