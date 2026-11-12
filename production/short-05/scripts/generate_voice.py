import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "Many Americans can’t cover a thousand-dollar emergency. Here’s how to fix that. "
    "Step one. Save a thousand-dollar starter fund in a separate savings account. "
    "Step two. If your job offers a 401k match, get all of it. That’s free money. "
    "Step three. Pay off high-interest debt, like credit cards. "
    "Step four. Build three to six months of expenses in a high-yield savings account. "
    "Step five. Automate it. Move money on payday, so saving comes before spending. "
    "Then invest regularly in low-cost index funds, and let time do the work. "
    "Save this, and follow for one money lesson every day."
)

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    print(f"Loading Chatterbox Voice B on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.82, cfg_weight=0.28)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("short-05-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Saved narration: {duration:.2f}s")
    if not 40 <= duration <= 47:
        raise SystemExit(f"Narration duration {duration:.2f}s outside safe 40–47s range; refusing aggressive time-stretch.")

if __name__ == "__main__":
    main()
