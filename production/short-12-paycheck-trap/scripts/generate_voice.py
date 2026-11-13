import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = """You bring home five thousand dollars a month. On paper, that sounds like plenty. But before you can enjoy it, rent takes nineteen hundred. Your car payment takes another six hundred and fifty. Then insurance, utilities, groceries, gas, and subscriptions all want their share. And don't forget the credit card bill sitting in your inbox. Suddenly, your paycheck is already working overtime before the month is halfway done. Now imagine your car breaks down and the repair costs four hundred dollars. If there's no emergency savings, that one surprise can push you straight onto a credit card. You're not necessarily terrible with money. Your paycheck may simply have too many jobs. Start by tracking where every dollar goes, then give your savings a job too. How much of your paycheck actually belongs to you?"""

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.72, cfg_weight=0.30)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice-original.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Voice B duration: {duration:.2f}s; final mix applies 0.9x speed.")
    if not 30.0 <= duration <= 39.0:
        raise SystemExit(f"Voice duration {duration:.2f}s outside target.")

if __name__ == "__main__":
    main()
