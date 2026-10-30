from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
TEXT = "Your paycheck just hit. But watch what happens next."
pipeline = KPipeline(lang_code="a")
chunks = []
for _, _, audio in pipeline(TEXT, voice="am_michael", speed=1.08):
    if audio is not None:
        chunks.append(np.asarray(audio, dtype=np.float32).reshape(-1))
if not chunks:
    raise RuntimeError("Kokoro returned no narration audio")
speech = np.concatenate(chunks)
sr = 24000
target = int(4.8 * sr)
if len(speech) > target:
    # Keep the complete line; slight speed-up only, never truncate.
    idx = np.linspace(0, len(speech)-1, target)
    speech = np.interp(idx, np.arange(len(speech)), speech).astype(np.float32)
audio = np.zeros(int(5.0*sr), dtype=np.float32)
audio[int(.12*sr):int(.12*sr)+len(speech)] = speech
sf.write(OUT/"pilot_voice.wav", audio, sr)
print(f"Saved pilot voice: {len(audio)/sr:.2f}s")
