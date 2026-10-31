#!/usr/bin/env python3
import json, subprocess
from pathlib import Path

root = Path(__file__).parent
chunks = [root / f"voice_{i}.mp3" for i in range(1, 9)]
durations = []
for p in chunks:
    raw = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(p)], text=True)
    d = float(json.loads(raw)["format"]["duration"])
    if d < 8.0:
        raise SystemExit(f"Voice chunk unexpectedly short: {p.name}={d:.2f}s")
    durations.append(d)
total = sum(durations) + 1.0
html_path = root / "index.html"
html = html_path.read_text()
import re
html = re.sub(r'data-duration="[^"]+"', f'data-duration="{total:.3f}"', html, count=1)
start_marker = ".scene{position:absolute;inset:0;opacity:0}"
end_marker = ".kicker{"
a, b = html.index(start_marker), html.index(end_marker, html.index(start_marker))
rules = [".scene{position:absolute;inset:0;opacity:0}"]
cursor = 0.0
for i, dur in enumerate(durations, 1):
    begin, end = cursor, cursor + dur
    fade = min(0.30, dur * 0.025)
    p0, p1 = begin/total*100, (begin+fade)/total*100
    p2, p3 = max(begin+fade,end-fade)/total*100, end/total*100
    rules.append(f".s{i}{{--scene-start:{begin:.3f}s;animation:scene{i} {total:.3f}s linear both}}")
    rules.append(f"@keyframes scene{i}{{0%,{p0:.4f}%{{opacity:0}}{p1:.4f}%,{p2:.4f}%{{opacity:1}}{p3:.4f}%,100%{{opacity:0}}}}")
    cursor = end
html = html[:a] + "\n".join(rules) + "\n" + html[b:]
html_path.write_text(html)
print("VOICE_DURATIONS=" + ",".join(f"{x:.2f}" for x in durations))
print(f"COMPOSITION_DURATION={total:.2f}")
if total < 210 or total > 255:
    raise SystemExit(f"Episode duration {total:.2f}s outside 3:30–4:15 target")
