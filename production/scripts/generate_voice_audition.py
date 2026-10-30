import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = "Your paycheck just hit. Nice! But wait… where did all that money go? Let’s break it down."

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating voice audition")
    wav = model.generate(
        TEXT,
        exaggeration=0.65,
        cfg_weight=0.35,
    )
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("voice-audition.wav", audio, model.sr, subtype="PCM_16")
    print(f"Saved voice-audition.wav at {model.sr} Hz")

if __name__ == "__main__":
    main()
