import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = "Social Security checks are getting a raise in 2027. The official number is three point six percent. The Social Security Administration says that means the average retirement benefit rises by about seventy five dollars a month, starting in January. Nearly seventy two million Social Security beneficiaries will see the increase. But here's what the headline leaves out: this is a cost of living adjustment, calculated using a specific inflation measure called the CPI-W. And seventy five dollars is an average, not your personal increase. Your exact amount can differ because your benefit and deductions are different. So don't budget from the headline. Check your personal Social Security notice when it arrives."

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Voice duration: {duration:.2f}s")
    if not 28.0 <= duration <= 45.0:
        raise SystemExit(f"Voice duration {duration:.2f}s outside 28–45s target.")

if __name__ == "__main__":
    main()
