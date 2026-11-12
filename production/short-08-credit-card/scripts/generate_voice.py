import torch, soundfile as sf
from chatterbox.tts import ChatterboxTTS
TEXT = "Paying only the minimum on your credit card feels like a win. You avoid a late payment, and you keep more cash in your pocket today. But here's the catch: the unpaid balance keeps collecting interest. Imagine you owe one thousand dollars, and your card charges twenty-four percent annual interest. That's roughly two percent a month, before fees and other details. If you pay just the minimum, a big part of that payment may go toward interest, not reducing what you borrowed. So your balance can shrink painfully slowly, and you may pay much more than the original purchase price over time. Here's a smarter move: pay the full statement balance by the due date whenever you can. If you can't, pay more than the minimum and stop adding new charges if possible. Check your statement for the interest rate, minimum payment, and payoff estimate. And remember, a credit card's minimum payment is designed to keep the account current, not to help you get out of debt quickly. A few extra dollars toward the principal can make a difference. Before you borrow, understand the rate, the fees, and how long repayment could take."
def main():
    device = "cuda" if torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3 else "cpu"
    model = ChatterboxTTS.from_pretrained(device=device)
    wav = model.generate(TEXT, exaggeration=0.92, cfg_weight=0.24)
    audio = wav.detach().float().cpu().squeeze().numpy()
    sf.write("voice.wav", audio, model.sr, subtype="PCM_16")
    duration = len(audio) / model.sr
    print(f"Voice duration: {duration:.2f}s")
    if not 28.0 <= duration <= 45.0: raise SystemExit(f"Voice duration {duration:.2f}s outside 28–45s target.")
if __name__ == "__main__": main()
