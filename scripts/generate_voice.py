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
    lang = voice_cfg.get("lang", "en-us")
    voice = voice_cfg.get("voice", "af_heart")
    speed = float(voice_cfg.get("speed", 1.0))
    pipeline = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    chunks: list[np.ndarray] = []
    pauses: list[np.ndarray] = []
    sample_rate = 24000

    for scene in PLAN["scenes"]:
        text = scene["voice"]
        scene_audio: list[np.ndarray] = []
        for _, _, audio in pipeline(text, voice=voice, speed=speed):
            if audio is not None:
                scene_audio.append(np.asarray(audio, dtype=np.float32).reshape(-1))
        if not scene_audio:
            raise RuntimeError(f"No speech generated for scene {scene['id']}")
        speech = np.concatenate(scene_audio)
        target = max(0.5, float(scene["end"]) - float(scene["start"]) - 0.35)
        # Preserve natural voice speed; only pad short lines, never time-stretch aggressively.
        chunks.append(speech)
        gap = max(0.0, float(scene["end"]) - float(scene["start"]) - len(speech) / sample_rate)
        pauses.append(np.zeros(int(gap * sample_rate), dtype=np.float32))

    final = np.concatenate([part for pair in zip(chunks, pauses) for part in pair])
    peak = float(np.max(np.abs(final))) if final.size else 0.0
    if peak > 0.98:
        final *= 0.98 / peak
    path = OUT / "voice.wav"
    sf.write(path, final, sample_rate, subtype="PCM_16")
    print(f"Voice saved: {path} ({len(final)/sample_rate:.1f}s)")

if __name__ == "__main__":
    main()
