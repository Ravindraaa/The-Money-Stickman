#!/usr/bin/env python3
"""Local, deterministic script-to-scene compiler. No paid API or network calls."""
from __future__ import annotations
import argparse, html, json, re
from pathlib import Path

RULES = [
    ("debt", ("debt", "credit", "loan", "interest", "minimum", "payment", "owe")),
    ("bills", ("rent", "bill", "utility", "subscription", "food", "transport", "expense", "spend")),
    ("savings", ("save", "saving", "emergency fund", "invest", "budget", "payday", "automatically")),
    ("warning", ("trap", "risk", "danger", "mistake", "expensive", "late", "avoid", "problem")),
    ("money", ("money", "cash", "dollar", "paycheck", "income", "salary", "bank", "price")),
    ("growth", ("grow", "increase", "build", "future", "compound", "goal", "progress")),
]
VISUALS = {
    "debt":   {"icon":"💳", "label":"THE DEBT TRAP", "accent":"#fb7185", "action":"react"},
    "bills":  {"icon":"🧾", "label":"WHERE IT GOES", "accent":"#fbbf24", "action":"point"},
    "savings":{"icon":"🏦", "label":"PAY YOURSELF FIRST", "accent":"#4ade80", "action":"celebrate"},
    "warning":{"icon":"⚠️", "label":"WATCH OUT", "accent":"#fb923c", "action":"shock"},
    "money":  {"icon":"💵", "label":"FOLLOW THE MONEY", "accent":"#67e8f9", "action":"grab"},
    "growth": {"icon":"📈", "label":"BUILD MOMENTUM", "accent":"#a78bfa", "action":"celebrate"},
    "general":{"icon":"⚡", "label":"THE MONEY STICKMAN", "accent":"#67e8f9", "action":"talk"},
}

def classify(text: str) -> str:
    low = text.lower()
    scores = [(sum(1 for term in terms if term in low), name) for name, terms in RULES]
    best = max(scores, default=(0, "general"))
    return best[1] if best[0] else "general"

def split_script(text: str, max_words: int = 7) -> list[str]:
    # Keep punctuation attached to its spoken word. Sentence boundaries are preferred.
    sentences = re.findall(r'[^.!?;]+[.!?;]?', text.strip())
    chunks = []
    for sentence in sentences:
        words = sentence.strip().split()
        while words:
            take = min(max_words, len(words))
            # Prefer a clause break close to the target, without creating tiny fragments.
            if len(words) > max_words:
                candidates = [i for i, w in enumerate(words[:max_words], 1)
                              if re.search(r'[,;:]$', w) and i >= 4]
                if candidates:
                    take = candidates[-1]
            chunk = " ".join(words[:take]).strip()
            words = words[take:]
            if chunk:
                chunks.append(chunk)
    return chunks

def compile_beats(script: str, max_words: int = 7) -> list[dict]:
    beats = []
    for idx, line in enumerate(split_script(script, max_words), 1):
        kind = classify(line)
        visual = VISUALS[kind]
        beats.append({
            "id": f"beat-{idx:03d}", "text": line, "caption": line,
            "kind": kind, "icon": visual["icon"], "label": visual["label"],
            "accent": visual["accent"], "action": visual["action"],
            "duration": None, "audio": f"audio/beat-{idx:03d}.wav"
        })
    return beats

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--script-file", required=True, type=Path)
    p.add_argument("--output", type=Path, default=Path("build/storyboard.json"))
    p.add_argument("--max-words", type=int, default=7)
    a = p.parse_args()
    if not a.script_file.is_file(): raise SystemExit(f"Missing script: {a.script_file}")
    script = re.sub(r"\s+", " ", a.script_file.read_text(encoding="utf-8")).strip()
    if not script: raise SystemExit("Script is empty.")
    if not 4 <= a.max_words <= 10: raise SystemExit("--max-words must be between 4 and 10.")
    beats = compile_beats(script, a.max_words)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps({"version":2,"source":"local-rule-based","beats":beats},indent=2)+"\n",encoding="utf-8")
    print(f"Compiled {len(beats)} narration beats into {a.output}")
    for b in beats: print(f"{b['id']} [{b['kind']}] {b['text']}")
if __name__ == "__main__": main()
