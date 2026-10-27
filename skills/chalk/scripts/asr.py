"""Shared ASR helper: faster-whisper with ffmpeg decoding (avoids PyAV version clashes with manim)."""
import subprocess
import numpy as np
from faster_whisper import WhisperModel

_models = {}


def load_audio(path, sr=16000):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"])
    return np.frombuffer(raw, np.float32)


def transcribe(path, model="small.en", words=True):
    if model not in _models:
        _models[model] = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = _models[model].transcribe(load_audio(path), beam_size=5, word_timestamps=words, vad_filter=False)
    return list(segs)
