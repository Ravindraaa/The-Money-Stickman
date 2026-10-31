import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "Only paying the minimum on your credit card? That small payment can keep you in debt longer than you expect. "
    "Here's why. Your minimum payment covers only part of what you owe. The rest of your balance can keep collecting interest month after month. "
    "So even after making a payment, your debt may shrink much more slowly than you think. "
    "Check your balance, know your interest rate, and pay more than the minimum when you can. "
    "And try not to add new charges while paying it down. "
    "Your credit card should work for you, not against you. Follow The Money Stickman for money moves that make sense."
)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating Short 04 narration with approved Voice B settings")
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("short-04-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved short-04-voice.wav at {model.sr} Hz; duration: {duration:.2f}s")
    if not 27 <= duration <= 42:
        raise SystemExit(f"Narration duration {duration:.2f}s outside expected 27–42s range")

if __name__ == "__main__":
    main()
