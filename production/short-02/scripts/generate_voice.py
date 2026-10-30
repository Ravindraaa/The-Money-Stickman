import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "Stop! Before you buy that thing online, try this simple rule. Your brain wants the reward right now, and that is exactly how impulse spending wins. Add the item to your cart, but do not check out. Wait twenty-four hours. Tomorrow, ask yourself three questions. Do I actually need it? Can I afford it without using a credit card or skipping a bill? And will I still want it next week? If the answer is no, close that tab and keep your money. If you still want it, compare prices and make a plan before you buy. One pause can prevent a purchase you regret. Follow The Money Stickman for simple money rules that actually stick."
)

def main():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading Chatterbox on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    print("Generating Short 02 narration with approved Voice B settings")
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().cpu().squeeze().numpy()
    sf.write("short-02-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved short-02-voice.wav at {model.sr} Hz; duration: {duration:.2f}s")
    if not 27 <= duration <= 42:
        raise SystemExit(f"Narration duration {duration:.2f}s outside expected 27–42s range")

if __name__ == "__main__":
    main()
