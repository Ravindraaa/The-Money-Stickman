import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "That five-dollar purchase feels harmless, right? A coffee, a snack, one little convenience. "
    "But do it every single day, and you're spending eighteen hundred and twenty-five dollars a year. "
    "Here's the math: five dollars times three hundred sixty-five days. "
    "That's not a random big purchase. It's a tiny habit on repeat. "
    "You don't have to cut every little joy. Just pick one daily expense you barely notice, "
    "and decide if it's worth eighteen hundred dollars a year. "
    "Small spends add up. Follow The Money Stickman for money moves that make sense."
)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating Short 03 narration with locked Voice B settings")
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("short-03-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved short-03-voice.wav at {model.sr} Hz; duration: {duration:.2f}s")
    if not 27 <= duration <= 42:
        raise SystemExit(f"Narration duration {duration:.2f}s outside expected 27–42s range")

if __name__ == "__main__":
    main()
