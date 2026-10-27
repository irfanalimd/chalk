# Assembly, captions, critic, revisions

## Assembly (`assemble.py`)

Builds `build/edit.otio` (OpenTimelineIO) and renders it with ffmpeg:

- V1 scenes, each trimmed or padded to its beat; optional `fade_in` per beat.
- V2 inserts from `project.json` overlays, with rounded corners and alpha fades.
- A1 narration at each beat's voice start; A2 score, ducked under the voice.
- Finishing: subtle vignette and fine luma grain (also hides banding on dark gradients).
- Two-pass loudnorm to −14 LUFS integrated, −1.5 dBTP; H.264 CRF 16, AAC 320k, faststart.

`--draft` renders 720p30 and falls back to preview renders, for checking cuts before final renders
finish. The `.otio` file opens in DaVinci Resolve or Premiere if someone wants to hand-edit the cut.
ffmpeg 8 removed `-filter_complex_script`; the script uses `-/filter_complex <file>`.

## Captions (`captions.py`)

- faster-whisper (small.en) word timestamps on the finished mix.
- Aligned to the script with difflib: script spelling wins for names; numerals heard as digits stay
  digits; words the script never says are dropped (Whisper invents "Thank you." in trailing silence).
- Whisper's word-timestamp pass occasionally skips a whole segment (it dropped 15 words at 4:33 of the
  Transformer video). Script words it never heard are filled from the planned TTS timings in
  `build/timing.json`, which match the final mix to within ~70 ms; the script prints how many it filled.
- Lines of ≤ 34 characters and ≤ 7 words, broken at punctuation and pauses, no one-word orphans.
- Active word gold, spoken words white, upcoming words dimmed; translucent dark box.
- Placement: for each line the script samples the clean master and picks the lowest of four bottom
  margins whose box (with clearance) overlaps the least on-screen content.
- Writes `build/captions.srt` too. Keep a no-captions master for platforms that take sidecar files.

## Critic (`critic.py`)

Reports format vs plan, loudness, black frames (true black, below the background colour), freezes over
3 s, transcript WER vs script with every mismatch listed, voice sync drift, and writes contact sheets
every 2.5 s plus a frame either side of every cut to `build/critic/`.

Spelling variants (center/centre, 1917/nineteen seventeen) appear as transcript edits; read the list
rather than the number. A long run of script words "heard" as nothing is usually that ASR segment
skip, not missing audio: confirm with a plain transcription of that section's WAV.

Then read the sheets. Look for: text clipped by the frame edge, captions touching labels, frames that sit empty for more than ~2 s, abrupt cuts, a footage box showing the
wrong shot, small text that should be smaller (credits) or larger (labels).

## Revisions

- Before changing a delivered video, copy its MP4s, `.srt`, `edit.otio`, `timing.json` and the
  `scenes/`, `script/`, `project.json` into `versions/vN/`. Deliver the revision under a new name.
- Map each note to the smallest change: pacing → pauses; a wrong visual → that scene only; an audio
  artefact → the audio edit, not a new TTS take.
- Re-render only the scenes whose beats changed length or content (`render_scenes.py <ids>`), then
  update any `PIP` windows the renderer prints, rebuild music if beat times moved, and rerun
  assemble → captions → critic.
