import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS
TEXT = "America's credit card balance just hit one point two nine trillion dollars. That's a record, up twenty two billion in just three months. But here's the twist: more debt doesn't mean everyone is missing payments. The New York Fed says serious-delinquency transitions on cards actually edged down from a year ago. Still, the pressure is real. Reuters recently profiled a twenty seven year old who built nearly thirty thousand dollars in card debt after losing her job. Her cards charged up to twenty six percent interest. A nonprofit debt plan helped negotiate those rates down. The lesson? A card can bridge a rough month, but high interest can turn a short-term gap into years of payments. Know your rate, make a payoff plan, and ask about help early."
def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Voice duration: {duration:.2f}s")
    if not 28.0 <= duration <= 45.0: raise SystemExit(f"Voice duration {duration:.2f}s outside 28–45s target.")
if __name__ == "__main__": main()
