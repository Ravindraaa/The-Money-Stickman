import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS
TEXT = "Want to invest? Start with a broad index fund. One investment can hold hundreds of companies."
def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.92, cfg_weight=0.24)
    audio=wav.detach().float().cpu().squeeze().numpy()
    sf.write("preview-voice.wav",audio,model.sr,subtype="PCM_16")
    duration=len(audio)/model.sr
    print(f"Preview narration: {duration:.2f}s")
    if not 7.5 <= duration <= 11.5: raise SystemExit(f"Voice duration {duration:.2f}s outside 7.5–11.5s target.")
if __name__=="__main__": main()