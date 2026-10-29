# Scene brief — "Attention Is All You Need", a guided reading (≈9.5 min, long mode)

You are building Manim Community scenes for an animated explainer of Vaswani et al. (2017).
Project root: `~/videos/attention-paper`. Audience: people with a basic STEM degree. Quality bar: a
premium documentary — precise, calm, uncluttered, nothing clipped, every frame intentional.

## Read first
- `scenes/style.py` — palette, type helpers (`serif`, `sans`, `eyebrow`, `chip`, `credit`, `glow`),
  the timing API (`BeatScene`, `self.cues.at/after`, `wait_to`, `play_until`, `play_from`, `drift`,
  `finish`), and paper helpers (`pdf_png(page, clip)`, `paper_card(path, height)`, `unicode_math(s)`).
- `~/videos/chalk/skills/chalk/references/scenes.md` — house rules and gotchas.
- `script/narration.json` — the exact narration of your sections. `build/timing.json` has word times.
- `research/attention.pdf` (15 pages) and `research/attention.txt`. Page indexes are 0-based:
  Figure 1 (architecture) p2; Eq. 1 + Figure 2 (scaled dot-product / multi-head) p3; Table 1 p5;
  Table 2 p7; Figure 3 p12; Figure 4 (anaphora heads, "The Law will never be perfect…") p13;
  Figure 5 p14. Use `pymupdf` `page.search_for(text)` to find exact rects for crops/highlights.
  Google permits reproducing the paper's tables and figures with attribution: any paper crop gets a
  small `credit("Vaswani et al., 2017")` (or put it under the crop in 11-px sans, MUTED, opacity 0.7).

## Hard rules
- Only create your own scene files (and private helper modules prefixed with your scene id). Do not
  edit `style.py`, `project.json`, `narration.json`, timing files, or anyone else's scenes.
- Class/file names exactly as assigned. `BEAT` = the section id.
- Cue every change to words with `self.cues`; never hard-code seconds. End with `self.finish()`.
  Rendered length must equal the beat (check with ffprobe; `python ~/videos/chalk/skills/chalk/scripts/render_scenes.py <id>` reports `ok`/`LEN`).
- Each section follows a chapter title card that fades to background, and is followed by another one:
  start from an empty background (fade things in within the first second) and fade everything out in
  the last ~0.5 s.
- No LaTeX: no `MathTex`, `Tex`, `DecimalNumber`, `Integer`, `Variable`, `Matrix` (it uses LaTeX).
  Math via `unicode_math("softmax(QKᵀ / √dₖ) V")`; build matrices from `Square`/`Rectangle` grids.
- Real content only: numbers, formulas, sentences and figures must match the paper exactly. Simulated
  data (e.g. attention weights) must be computed (numpy softmax of actual dot products), not drawn by hand.
- Keep ≥0.4 units margin inside the camera frame at all times; keep the bottom ~1.1 units calm
  (captions are burned in there later). Text minimal; never more than ~8 words of on-screen text at once
  except short labelled diagrams. Never let text overlap other elements.
- Palette: BG `#0B0D12`. Fixed role colouring everywhere:
  **query = BLUE `#58C4DD`, key = GREEN `#83C167`, value = ORANGE `#F0AC5F`, attention weight / highlight = gold NEEDLE `#FFD45A`, heads = a hue sweep**. Words as rounded "token chips" (`chip()`-like, sans 22–26).

## Process
1. Preview: from `scenes/`: `../.venv/bin/manim -ql --config_file ../manim.cfg <file>.py <Class>`
2. Contact sheet: `../.venv/bin/python ~/videos/chalk/skills/chalk/scripts/sheet.py <mp4> ../build/sheet_<id>.png 16` and Read the PNG.
   Check clipping, overlaps, empty stretches (>2 s with nothing changing), legibility, sync.
3. Iterate until it is genuinely good. Then final: same command without `-ql` → `build/manim/videos/<file>/1080p60/<Class>.mp4`.
4. Report: paths, durations vs beats, what is on screen when (with trigger phrases), any known issues.

## Sections and visual plans

### c0_open — `c0_open.py:C0Open`
"June 2017… eight researchers at Google… Attention Is All You Need… Transformer… foundation for almost every large language model… read that paper together."
- The real title page (p0, crop title+authors+abstract top) as a paper card sliding in; highlight the title.
  Small eyebrow "ARXIV 1706.03762 · JUNE 2017".
- "eight researchers": the eight author names (exact, from p0) appear as a tidy grid of small sans labels.
- "Transformer … foundation": a single glowing block labelled "Transformer"; on "large language model"
  a family of text-only labels grows from it (GPT, BERT, T5, ViT, Claude, Gemini, Llama — text only, no logos).
- "read that paper together": camera returns to the paper card; fade out.

### c1_rnn — `c1_rnn.py:C1RNN`
- "sequence transduction … English into German": token chips "The cat sat on the mat" → arrow → "Die Katze saß auf der Matte".
- "recurrent neural networks … keyhole … hidden state": a chain of RNN cells left to right, a keyhole/
  spotlight mask reveals one token at a time; a small coloured vector (stack of 6 cells) labelled "hidden state" is updated at each step.
- "speed": a grid of ~64 tiny GPU cores, only one lit at a time while the RNN steps.
- "memory … fades": the hidden state's colours from early words fade as later words enter.
- "attention … look back at every input word": decoder arcs back to every encoder token (gold weights).
- "added on top of a recurrent network" → "what if attention were the whole model?": the RNN chain
  dissolves, leaving only the arcs; serif italic question on screen.

### c2_attention — `c2_attention.py:C2Attention`
- "dictionary in a programming language": code-like `{"cat": 7, "dog": 3}["dog"] → 3` (monospace Text).
- "soft version": the exact match becomes a soft match — bars of similarity.
- "query / key / value": one word chip emits three small vectors coloured by role (BLUE/GREEN/ORANGE), labelled.
- "compare its query with the key of every word … dot product": query arrow vs key arrows in 2D, dot products as bars (computed).
- "softmax … add up to one": bars become positive weights summing to 1 (show the sum).
- "weighted average of all the values": value vectors scale by weight and merge into the new vector.
- "the law will never be perfect, but its application should be just": token row (exact sentence);
  arcs from "its" to every word, thickness = computed weights with "Law" dominant; then cut to the paper's Figure 4 crop (p13) briefly.

### c3_scaled — `c3_scaled.py:C3Scaled`
- "Stack the queries into a matrix Q …": token vectors stack into Q, K, V grids (n×d), Kᵀ rotates.
- "softmax of Q times K transpose, divided by the square root of d k, multiplied by V": the formula
  `Attention(Q, K, V) = softmax(QKᵀ / √dₖ) V` builds term by term, then the paper's Eq. 1 crop (p3) beside it.
- "two matrix multiplications and a softmax": QKᵀ → n×n score heatmap → row softmax → ×V → output.
- "dot product … grows with their dimension … softmax turns extremely peaked": two bar charts of the
  softmax of real random dot products for d=4 and d=512 (seeded numpy); the second is one spike.
- "Dividing by the square root": the d=512 chart relaxes after scaling.
- "mask hides the words that come later": the n×n heatmap with the upper triangle greyed out (−∞).

### c4_heads — `c4_heads.py:C4Heads`
- "eight smaller subspaces": the 512-wide vector splits into 8 slices of 64 (label "d_model = 512", "h = 8", "dₖ = 64").
- each head = small attention heatmap in its own hue (computed from different random projections), then "Concat" → "Linear" boxes.
- "cost about as much as one": a simple balance/equal-area graphic (8 thin vs 1 wide).
- "heads had specialised … pronoun refers to": paper Figure 4 crop (p13) with highlight on "its"/"Law"; a
  glimpse of Figure 5 (p14) for "grammatical structure".

### c5_position — `c5_position.py:C5Position`
- "nothing … knows the order": token chips; shuffle animation; the attention output bars stay identical.
- "dog bites man / man bites dog": the two sentences side by side → "≡" for attention (same multiset).
- "sine and cosine waves": the real PE matrix (pos 0–50 × dim 0–128, PE formula from the paper) as a
  heatmap built row by row; then 3–4 individual sinusoids of different frequency drawn as curves.
- "clock with many hands": a row of small dials rotating at geometrically decreasing speeds.
- "linear transformation": a 2D rotation of one (sin, cos) pair by a fixed angle for a fixed shift k.
- Show the formula `PE(pos, 2i) = sin(pos / 10000^(2i/d_model))` in unicode_math, small.

### c6_arch — `c6_arch.py:C6Arch`
The centrepiece. Draw the Figure 1 architecture yourself, cleanly, built in sync with the narration:
inputs → input embedding (+ positional encoding ⊕) → encoder block [Multi-Head Attention → Add & Norm →
Feed Forward → Add & Norm] with "N×" (6); outputs (shifted right) → output embedding (+ PE) → decoder
block [Masked Multi-Head Attention → Add & Norm → Multi-Head (cross) Attention ← from encoder →
Add & Norm → Feed Forward → Add & Norm] "N×"; Linear → Softmax → output probabilities.
- Residual connections as curved bypass arrows ("adds the input back"). Highlight each part as it is named.
- "cross-attention, whose queries come from the decoder while its keys and values come from the encoder":
  colour the three arrows by role (BLUE query from decoder; GREEN/ORANGE key/value from encoder).
- "probability for every word": a small bar chart over a few German words.
- End: the paper's own Figure 1 crop (p2) fades in beside yours for a beat, then fade out.

### c7_why — `c7_why.py:C7Why`
- Recreate Table 1 (p5) as a clean table: rows Self-Attention, Recurrent, Convolutional; columns
  "Complexity per layer" O(n²·d), O(n·d²), O(k·n·d²); "Sequential ops" O(1), O(n), O(1); "Max path length"
  O(1), O(n), O(logₖ(n)). (Check exact entries in the paper.) Reveal row by row with the narration.
- "pass through every word in between": a chain graph with a signal hopping n steps; "every pair directly":
  a complete graph, signal in one hop.
- "grows with the square": n×n grid growing; "shorter than the vectors": compare n (~30 words) to d=512.

### c8_results — `c8_results.py:C8Results`
- "eight graphics cards": 8 GPU icons; "twelve hours" / "three and a half days" as two timeline bars.
- "small fraction of the computation": training-cost bars on a log axis from Table 2 (p7) — EN-DE: ConvS2S
  Ensemble 7.7·10¹⁹, GNMT+RL Ensemble 1.8·10²⁰, Transformer (big) 2.3·10¹⁹, Transformer (base) 3.3·10¹⁸.
- "learning rate that warms up before it decays": plot lrate = d_model^-0.5 · min(step^-0.5, step·warmup^-1.5),
  warmup 4000, real curve. "label smoothing": one-hot bar vs 0.9 with 0.1 spread (ε_ls = 0.1).
- "twenty eight point four BLEU": BLEU bars EN-DE: ConvS2S Ensemble 26.36, GNMT+RL Ensemble 26.30,
  MoE 26.03, Transformer (big) 28.4 (gold). "forty one point eight": EN-FR: ConvS2S Ensemble 41.29,
  GNMT+RL Ensemble 41.16, Transformer (big) 41.8 (gold, "single model").
- "parsing": a small constituency tree of a short sentence; caption "English constituency parsing".
- Optionally a quick look at the real Table 2 crop.

### c9_legacy — `c9_legacy.py:C9Legacy`
- "conclusion is modest … images, audio and video": the conclusion sentence crop (p9/p10; search for
  "We are excited about the future") with highlight on "images, audio and video".
- "understatement": a timeline 2017 → 2018 (GPT: decoder, BERT: encoder) → 2020 (Vision Transformer:
  image patches) → AlphaFold 2 (attention in protein structure) → "today's language models". Text labels only.
  Show encoder/decoder halves of a mini Transformer splitting into BERT and GPT.
- "single operation that lets every word look at every other word": return to a token row with full
  all-pairs attention arcs, the formula glowing above; slow pull-back; fade out.
