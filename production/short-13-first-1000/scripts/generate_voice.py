import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = """Your first thousand dollars won't make you rich, but it could change how you handle money. Imagine your car suddenly breaks down, and a four-hundred-dollar repair bill lands out of nowhere. Without savings, you're reaching for a credit card, and paying for that repair long after it's fixed. But with a thousand dollars saved, that surprise doesn't have to become a financial disaster. Start small. Save twenty-five dollars a week, and that's thirteen hundred dollars in a year. Your first goal isn't to look rich. It's to stop one bad day from becoming months of debt. Start your thousand-dollar fund today."""
def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.78, cfg_weight=0.28)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice-original.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Narration duration: {duration:.2f}s")
    if not 32.0 <= duration <= 44.0: raise SystemExit(f"Voice duration {duration:.2f}s outside target.")
if __name__ == "__main__": main()