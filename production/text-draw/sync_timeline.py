#!/usr/bin/env python3
import json, re, subprocess
from pathlib import Path

root = Path(__file__).parent
chunks = [root / f"voice_{i}.mp3" for i in range(1, 7)]
durations = []
for p in chunks:
    raw = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(p)], text=True)
    d = float(json.loads(raw)["format"]["duration"])
    if d < 1.0:
        raise SystemExit(f"Voice chunk unexpectedly short: {p.name}={d:.2f}s")
    durations.append(d)

total = sum(durations) + 0.8
html_path = root / "index.html"
html = html_path.read_text()
html = re.sub(r'data-duration="[^"]+"', f'data-duration="{total:.3f}"', html, count=1)

# Replace the complete scene timing block in one operation. Avoid nested-brace
# regex replacements: CSS keyframes contain nested rule braces.
start_marker = ".scene{position:absolute;inset:0;opacity:0;animation:show 38s linear both}"
end_marker = ".kicker{"
a = html.index(start_marker)
b = html.index(end_marker, a)
cursor = 0.0
rules = [".scene{position:absolute;inset:0;opacity:0}"]
for i, dur in enumerate(durations, 1):
    begin = cursor
    end = cursor + dur
    fade = min(0.22, dur * 0.12)
    p0 = begin / total * 100
    p1 = (begin + fade) / total * 100
    p2 = max(begin + fade, end - fade) / total * 100
    p3 = end / total * 100
    rules.append(f".s{i}{{animation:scene{i} {total:.3f}s linear both}}")
    rules.append(
        f"@keyframes scene{i}{{0%,{p0:.4f}%{{opacity:0}}"
        f"{p1:.4f}%,{p2:.4f}%{{opacity:1}}"
        f"{p3:.4f}%,100%{{opacity:0}}}}"
    )
    cursor = end
html = html[:a] + "\n".join(rules) + "\n" + html[b:]

audio = f'<audio id="narration" src="narration.mp3" data-start="0" data-duration="{total:.3f}" data-track-index="0" data-volume="1"></audio>'
if '<audio id="narration"' in html:
    html = re.sub(r'<audio id="narration"[^>]*></audio>', audio, html)
else:
    html = html.replace('<div class="brand">', audio + '\n<div class="brand">', 1)

html_path.write_text(html)
print("VOICE_DURATIONS=" + ",".join(f"{x:.2f}" for x in durations))
print(f"COMPOSITION_DURATION={total:.2f}")
