import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

# Audition B: brighter, more expressive delivery for The Money Stickman.
TEXT = "Your paycheck just hit. Nice! But wait... where did ALL that money go? Let's break it down."

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating higher-energy voice audition B")
    wav = model.generate(
        TEXT,
        exaggeration=0.82,
        cfg_weight=0.28,
    )
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("voice-audition-b.wav", audio, model.sr, subtype="PCM_16")
    print(f"Saved voice-audition-b.wav at {model.sr} Hz")

if __name__ == "__main__":
    main()
