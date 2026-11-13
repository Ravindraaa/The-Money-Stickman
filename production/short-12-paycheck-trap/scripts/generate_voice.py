import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = """You bring home five thousand dollars a month. Sounds like good money, right? Then rent takes nineteen hundred. Your car takes six-fifty. Insurance, utilities, and groceries keep eating away at your paycheck. Credit card payments take another bite. And suddenly, that five thousand doesn't feel so big. Here's the scary part: one unexpected four-hundred-dollar bill can throw your whole month off. You're not necessarily bad with money. Your paycheck might just have too many jobs before it even reaches you. So, how much of your paycheck actually belongs to you?"""

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.72, cfg_weight=0.30)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice-original.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Voice B duration: {duration:.2f}s; final mix applies 0.9x speed.")
    if not 27.0 <= duration <= 39.0:
        raise SystemExit(f"Voice duration {duration:.2f}s outside target.")

if __name__ == "__main__":
    main()
