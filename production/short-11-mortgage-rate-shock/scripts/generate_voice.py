import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = "Want to know why buying a home in America still feels so expensive? Look at the mortgage rate. This week, the average thirty-year fixed rate was about seven point one one percent. That sounds like just a number. But on a four-hundred-thousand-dollar loan, the monthly payment can be roughly three hundred dollars higher than when rates briefly fell below six percent. That's about thirty-six hundred dollars more every year, before taxes, insurance, or maintenance. And here's the catch: a lower rate doesn't automatically make a home affordable. The price, your down payment, credit score, and loan terms all matter. So before you shop by the listing price, calculate the monthly payment. That's the number your budget actually has to survive."

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice-original.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Original Voice B duration: {duration:.2f}s; final mix applies 0.9x speed.")
    if not 27.0 <= duration <= 40.0:
        raise SystemExit(f"Voice duration {duration:.2f}s outside target.")

if __name__ == "__main__":
    main()
