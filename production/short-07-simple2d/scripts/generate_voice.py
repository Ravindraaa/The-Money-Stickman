import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS
TEXT = ("Ever notice your grocery bill keeps climbing? That's inflation. "
        "When prices rise, the same ten dollars buys less than it did before.")
def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.92, cfg_weight=0.24)
    audio=wav.detach().float().cpu().squeeze().numpy()
    sf.write("demo-voice.wav",audio,model.sr,subtype="PCM_16")
    duration=len(audio)/model.sr
    print(f"Demo narration: {duration:.2f}s")
    if not 7.0 <= duration <= 10.8: raise SystemExit(f"Voice duration {duration:.2f}s outside 7–10.8s target.")
if __name__=="__main__": main()