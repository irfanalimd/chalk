# Voice, pauses, music

## ElevenLabs voice

`script/narration.json` holds the voice, settings and one entry per narrated beat (`id` = beat id).
`tts.py` calls `/v1/text-to-speech/{voice}/with-timestamps` per section with `previous_text`/`next_text`
for continuity, caches raw takes in `build/audio/raw/`, then writes edited WAVs and `build/timing.json`
(word start/end times, voice and scene durations).

- Scoped keys are common. A key may allow TTS but not `voices_read`, `user_read` or
  `music_generation`. Do not rely on listing voices; use premade IDs:
  George `JBFqnCBsd6RMkjVDRZzb` (warm, older British, the default),
  Daniel `onwK4e9ZLuTAKqWW03F9` (authoritative British), Brian `nPczCjzI2devNBz1zQrb` (deep American).
  Generate one sentence with each and let the user choose if they care.
- Free and lower tiers reject `mp3_44100_192`; use `mp3_44100_128` (`output_format` in narration.json).
- Settings that read as a professor: stability 0.55, similarity 0.8, style 0.2, speed 0.97 (~165 wpm).
- After synthesis run ASR over each section and compare with the script; fix spelling in the text
  (not phonetic hacks) unless a name is mispronounced.

## Pauses and tail clean-up

- `pauses` in narration.json: `{"section": "s3_x", "after": "it lives in", "sec": 0.6}`. Silence is
  inserted at the quietest point of the gap after the phrase and every later word time shifts, so scene
  cues follow. Use 0.35–0.7 s at changes of topic; `tail` (gap after each section) around 1.0 s.
- `previous_text`/`next_text` sometimes leave a clipped fragment (a breath or the onset of the next
  sentence) in the last ~100 ms of a section. It sounds like audio cut off before the next scene.
  `tts.py` detects sound that starts after a silence and runs into the file end, cuts it and fades.
- To change pacing, edit pauses and rerun `tts.py`; it re-edits the cached takes without new TTS calls.
  Only `--force <ids>` resynthesizes.

## Music

`music.py` (ElevenLabs): one composition plan whose sections match the beats; per-beat moods in
`project.json` `music.moods`. Sections must be ≥ 3 s (short beats are merged into the next). Needs the
`music_generation` permission; a 401 names the missing permission.

`music.py --library`: licensed tracks with cue points. Each cue is loudness-matched and crossfaded so
the change lands on a story turn (`at_beat`), e.g. soft piano for the setup and a fuller arrangement
from the reveal. Kevin MacLeod's catalogue (incompetech.com, CC BY 4.0, credit required) has direct MP3
URLs: `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<Title%20With%20Spaces>.mp3`.
Without listening, compare candidates by 5-second loudness envelopes: a quiet, varied envelope suits
narration; a flat, loud one is a full arrangement for the climax.

`assemble.py` mixes the score at `music.gain_db` (−9 dB), side-chain ducks it under the voice, fades
it out over the last 3 s, and normalises the mix to −14 LUFS / −1.5 dBTP.
