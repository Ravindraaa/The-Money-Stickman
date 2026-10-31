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
html = re.sub(r'data-duration="[^"]+"', f'data-duration="{total:.3f}"', html)
html = re.sub(r'\.scene\{position:absolute;inset:0;opacity:0;animation:show 38s linear both\}', f'.scene{{position:absolute;inset:0;opacity:0}}', html)

# Build each scene's own timing from the measured duration of its matching spoken chunk.
starts = []
cursor = 0.0
for d in durations:
    starts.append(cursor)
    cursor += d

for i, (start, dur) in enumerate(zip(starts, durations), 1):
    end = start + dur
    # A short crossfade keeps the screen changing with the spoken section.
    fade = min(0.22, dur * 0.12)
    anim = f'.s{i}{{animation:scene{i} {total:.3f}s linear both}}'
    html = re.sub(rf'\.s{i}\{{animation:scene{i}[^}}]*\}}', anim, html)
    kf = (f'@keyframes scene{i}{{'
          f'0%,{start/total*100:.4f}%{{opacity:0}}'
          f'{(start+fade)/total*100:.4f}%,{max(start+fade,end-fade)/total*100:.4f}%{{opacity:1}}'
          f'{end/total*100:.4f}%,100%{{opacity:0}}'
          f'}}')
    html = re.sub(rf'@keyframes scene{i}\{{[^}}]*\}}', kf, html)

# Keep the final scene visible through the final spoken question and a short tail.
html_path.write_text(html)
print("VOICE_DURATIONS=" + ",".join(f"{x:.2f}" for x in durations))
print(f"COMPOSITION_DURATION={total:.2f}")
