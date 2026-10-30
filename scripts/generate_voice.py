from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parents[1]
PLAN = json.loads((ROOT / "assets/short_001.json").read_text(encoding="utf-8"))
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)


def main() -> None:
    voice_cfg = PLAN["voice"]
    voice = voice_cfg.get("voice", "af_heart")
    speed = float(voice_cfg.get("speed", 1.0))
    # Kokoro's American English pipeline uses language code "a".
    pipeline = KPipeline(lang_code="a")
    sample_rate = 24000
    full = np.zeros(int(max(s["end"] for s in PLAN["scenes"]) * sample_rate), dtype=np.float32)

    for scene in PLAN["scenes"]:
        start = int(float(scene["start"]) * sample_rate)
        end = int(float(scene["end"]) * sample_rate)
        chunks: list[np.ndarray] = []
        for _, _, audio in pipeline(scene["voice"], voice=voice, speed=speed):
            if audio is not None:
                chunks.append(np.asarray(audio, dtype=np.float32).reshape(-1))
        if not chunks:
            raise RuntimeError(f"No speech generated for scene {scene['id']}")
        speech = np.concatenate(chunks)
        slot = end - start
        if len(speech) > slot:
            ratio = len(speech) / slot
            if ratio > 1.18:
                raise RuntimeError(
                    f"Scene {scene['id']} narration is too long ({ratio:.2f}x). "
                    "Shorten the line or extend its scene duration."
                )
            indices = np.linspace(0, len(speech) - 1, slot)
            speech = np.interp(indices, np.arange(len(speech)), speech).astype(np.float32)
        full[start:start + len(speech)] = speech

    peak = float(np.max(np.abs(full))) if full.size else 0.0
    if peak > 0.98:
        full *= 0.98 / peak
    path = OUT / "voice.wav"
    sf.write(path, full, sample_rate, subtype="PCM_16")
    print(f"Voice saved: {path} ({len(full)/sample_rate:.1f}s)")


if __name__ == "__main__":
    main()
