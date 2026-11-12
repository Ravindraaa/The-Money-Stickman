import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "Want to invest but feel lost? Don't pick stocks. Do this instead. "
    "Buy an index fund. One fund, hundreds of companies. Big names you know, all in one. "
    "One bad company won't sink the fund. Low fees keep more money yours. "
    "Fees quietly eat returns for decades. Pick a low-cost one. Check the expense ratio. "
    "Now the secret: consistency. Invest the same amount every month. "
    "Market up? Keep going. Market down? Keep going. That's called dollar-cost averaging. "
    "It removes the stress of timing. Even experts can't time the market. "
    "Time in the market beats timing it. Start early, even small. "
    "Compounding does the heavy lifting. Start in your 401(k) or a Roth IRA. "
    "Not a guarantee. Investments can lose value. Follow for one money lesson a day."
)

def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    print(f"Loading approved Voice B on {device}")
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.92, cfg_weight=0.24)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("short-06-voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Raw narration duration: {duration:.2f}s")
    if not 30 <= duration <= 48:
        raise SystemExit(f"Voice duration {duration:.2f}s outside 30–48s acceptance range.")
if __name__ == "__main__":
    main()
