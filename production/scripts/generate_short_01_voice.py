import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

# Short 01 — full narration. Voice B settings approved by the channel owner.
TEXT = (
    "Your paycheck hits... and somehow, it's already gone. Where did it all go? "
    "Let's say you bring home two thousand dollars. Rent and utilities take a thousand and fifty. "
    "Food and transportation? Four-twenty. Debt payments and subscriptions? Three-ten. "
    "That leaves just two hundred and twenty dollars. And that's before the random stuff life throws at you. "
    "Try this on your next payday: automatically move even twenty dollars into savings first. "
    "Start small, make it a habit, then build from there. "
    "Follow The Money Stickman for money moves that actually make sense."
)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating complete Short 01 narration with approved Voice B settings")
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("short-01-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved short-01-voice.wav at {model.sr} Hz; narration duration: {duration:.2f}s")
    if duration > 40:
        raise SystemExit(f"Narration is {duration:.2f}s; exceeds 40-second maximum")
    if duration < 30:
        raise SystemExit(f"Narration is {duration:.2f}s; below 30-second minimum")

if __name__ == "__main__":
    main()
