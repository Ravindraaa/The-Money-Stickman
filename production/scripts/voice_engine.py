#!/usr/bin/env python3
"""Reusable Chatterbox narration engine for The Money Stickman.

Accepts a plain-text script, generates the approved Voice B style, validates
the actual waveform, and writes a WAV plus JSON QA report. It deliberately
does not time-stretch speech to force a target duration.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS

DEFAULT_EXAGGERATION = 0.82
DEFAULT_CFG_WEIGHT = 0.28
MIN_SECONDS = 30.0
MAX_SECONDS = 40.0


def load_script(path: Path | None, inline_text: str | None) -> str:
    if path:
        if not path.is_file():
            raise FileNotFoundError(f"Script file not found: {path}")
        text = path.read_text(encoding="utf-8")
    else:
        text = inline_text or ""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise ValueError("Script is empty. Supply --script-file or --text.")
    if len(text) > 5000:
        raise ValueError("Script exceeds 5,000 characters; split it into episodes.")
    return text


def waveform_report(audio: np.ndarray, sample_rate: int) -> dict:
    if audio.ndim != 1:
        audio = np.asarray(audio).reshape(-1)
    if audio.size == 0 or not np.isfinite(audio).all():
        raise ValueError("Generated audio is empty or contains NaN/Inf values.")

    duration = float(audio.size / sample_rate)
    peak = float(np.max(np.abs(audio)))
    rms = float(np.sqrt(np.mean(np.square(audio, dtype=np.float64))))
    # Measure 100ms windows; flag a suspiciously silent generation.
    frame = max(1, int(sample_rate * 0.1))
    windows = [float(np.sqrt(np.mean(np.square(audio[i:i+frame], dtype=np.float64))))
               for i in range(0, len(audio), frame)]
    silent_ratio = float(sum(v < 0.001 for v in windows) / max(1, len(windows)))

    if not MIN_SECONDS <= duration <= MAX_SECONDS:
        raise ValueError(
            f"Narration is {duration:.2f}s; production gate is "
            f"{MIN_SECONDS:.0f}-{MAX_SECONDS:.0f}s. Rewrite the script; "
            "the engine will not unnaturally time-stretch it."
        )
    if peak < 0.02 or rms < 0.003:
        raise ValueError("Narration level is too low; reject this generation.")
    if silent_ratio > 0.35:
        raise ValueError(f"Too much near-silence in narration ({silent_ratio:.0%}).")

    clipping_detected = peak >= 1.0
    # Prevent clipping while retaining the natural dynamic range.
    if peak > 0.98:
        audio = audio * (0.98 / peak)
        peak = float(np.max(np.abs(audio)))

    return audio, {
        "duration_seconds": round(duration, 3),
        "sample_rate": int(sample_rate),
        "peak": round(peak, 5),
        "rms": round(rms, 5),
        "near_silence_ratio": round(silent_ratio, 4),
        "clipping_detected_before_protection": clipping_detected,
        "voice_engine": "Chatterbox TTS",
        "voice_profile": "Voice B creative profile",
        "exaggeration": DEFAULT_EXAGGERATION,
        "cfg_weight": DEFAULT_CFG_WEIGHT,
        "human_listening_review_required": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate validated Money Stickman narration.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--script-file", type=Path, help="UTF-8 plain-text narration file")
    source.add_argument("--text", help="Narration text")
    parser.add_argument("--output", type=Path, default=Path("output/narration.wav"))
    parser.add_argument("--report", type=Path, default=None)
    parser.add_argument("--device", choices=("auto", "cuda", "cpu"), default="auto")
    args = parser.parse_args()

    try:
        script = load_script(args.script_file, args.text)
        device = "cuda" if args.device == "auto" and torch.cuda.is_available() else args.device
        if device == "auto":
            device = "cpu"
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA was requested but is not available.")

        print(f"Loading Chatterbox on {device}...")
        model = ChatterboxTTS.from_pretrained(device=device)
        print("Generating narration with approved Voice B settings...")
        generated = model.generate(
            script,
            exaggeration=DEFAULT_EXAGGERATION,
            cfg_weight=DEFAULT_CFG_WEIGHT,
        )
        audio = generated.detach().float().cpu().squeeze().numpy().astype(np.float32)
        audio, report = waveform_report(audio, int(model.sr))

        args.output.parent.mkdir(parents=True, exist_ok=True)
        sf.write(args.output, audio, int(model.sr), subtype="PCM_16")
        report["script_characters"] = len(script)
        report["script_words"] = len(script.split())
        report["audio_file"] = str(args.output)
        report_path = args.report or args.output.with_suffix(".qa.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        print(f"\nPASS: narration saved to {args.output}")
        print(f"QA report: {report_path}")
        return 0
    except Exception as exc:
        print(f"VOICE GATE FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
