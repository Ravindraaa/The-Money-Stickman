#!/usr/bin/env python3
import json, subprocess, re
from pathlib import Path
root = Path(__file__).parent
chunks = [root / "voice_1.mp3", root / "voice_2.mp3"]
durations = []
for p in chunks:
    raw = subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","json",str(p)], text=True)
    durations.append(float(json.loads(raw)["format"]["duration"]))
total = sum(durations)
html_path = root / "index.html"
html = html_path.read_text()
html = re.sub(r'data-duration="[^"]+"', f'data-duration="{total:.3f}"', html, count=1)
html = re.sub(r'<audio id="narration" src="narration.mp3" data-start="0" data-duration="[^"]+"', f'<audio id="narration" src="narration.mp3" data-start="0" data-duration="{total:.3f}"', html, count=1)
html = re.sub(r'animation:progress 240s linear both', f'animation:progress {total:.3f}s linear both', html)
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
if "__timelines.main" not in html:
    html = html.replace("</body>", '<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script><script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});tl.to({}, {duration:'+f'{total:.3f}'+'});window.__timelines.main=tl;</script></body>')
html_path.write_text(html)
print("PREVIEW_VOICE_DURATIONS=" + ",".join(f"{x:.2f}" for x in durations))
print(f"PREVIEW_DURATION={total:.2f}s")
if not 45 <= total <= 75:
    raise SystemExit(f"Preview duration {total:.2f}s outside 45–75s")
