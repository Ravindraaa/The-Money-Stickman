import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "That five-dollar purchase feels harmless, right? A coffee on the way to work, a snack between errands, or one little convenience you barely think about. "
    "But when that same five-dollar purchase happens every single day, the total gets surprisingly big. You are spending eighteen hundred and twenty-five dollars in one year. "
    "Here is the math. Five dollars, multiplied by three hundred and sixty-five days, equals eighteen hundred and twenty-five dollars. "
    "And that is the point. It is not one huge purchase that drains your wallet. It is a tiny habit, repeated so often that you stop noticing it. "
    "You do not have to cut every little joy, and you do not need to feel guilty about buying coffee. Just choose one daily expense you barely notice. "
    "Ask yourself: is this small habit really worth eighteen hundred dollars a year? If it is, enjoy it. If not, make a different choice and keep that money for something you actually want. "
    "Small spends add up. Follow The Money Stickman for money moves that make sense."
)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating Short 03 narration with approved Voice B settings")
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("short-03-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved short-03-voice.wav at {model.sr} Hz; duration: {duration:.2f}s")
    if not 27 <= duration <= 42:
        raise SystemExit(f"Narration duration {duration:.2f}s outside expected 27–42s range")

if __name__ == "__main__":
    main()
