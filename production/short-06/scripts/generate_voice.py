import torch
import soundfile as sf
from chatterbox.tts import ChatterboxTTS

TEXT = (
    "Want to invest but feel lost? You do not need to become a stock-picking expert. "
    "Start with a broad, low-cost index fund that tracks a market index. "
    "One fund can give you exposure to hundreds of companies, including familiar names across different industries. "
    "If one company struggles, the others are still part of the basket. That spreads company-specific risk, but it does not remove market risk. "
    "Now check the expense ratio. It is the annual fund fee, and even small costs can add up over many years. "
    "Next, build a simple habit. Choose an amount you can afford and invest it regularly, like every payday or once a month. "
    "When prices rise, stick to your plan. When prices fall, stick to your plan too, if your goals and finances have not changed. "
    "Investing the same amount at regular intervals is called dollar-cost averaging. It can make the process more consistent, but it cannot guarantee a profit. "
    "Nobody can reliably predict every market move. Give a long-term plan time to work, and start with an amount that feels manageable. "
    "Compounding may help growth build on itself over time. You might use a workplace 401(k) or an IRA, but understand the account rules first. "
    "Investments can lose value, including the money you put in. Follow for one practical money lesson every day."
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
