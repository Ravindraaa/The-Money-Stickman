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
total = sum(durations)
html_path = root / "index.html"
html = html_path.read_text()
import re
html = re.sub(r'data-duration="[^"]+"', f'data-duration="{total:.3f}"', html, count=1)
html = re.sub(r'(<audio id="narration"[^>]*data-duration=")[^"]+(")', rf'\g<1>{total:.3f}\g<2>', html, count=1)
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
if "window.__timelines.main" not in html:
    registration = ('<script src="https://cdn.jsdelivr.net/npm/gsap@3/dist/gsap.min.js"></script>'
        + '<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});tl.to({}, {duration:' + f"{total:.3f}" + '});window.__timelines.main=tl;</script>')
    html = html.replace("</body>", registration + "</body>")

# Build narration-synced visual beats. Each beat covers roughly three seconds
# and is cut from the actual narration paragraph for its matching section.
import html as html_escape
script_text = (root / "EPISODE_SCRIPT.md").read_text()
sections = re.findall(r"\\*\\*Scene \\d+ — [^\\n]+\\*\\*\\s*\\n([^\\n]+)", script_text)
if len(sections) != 8:
    raise SystemExit(f"Expected 8 narration sections, found {len(sections)}")
beat_cards = []
beat_css = []
elapsed = 0.0
beat_no = 0
for section_no, (paragraph, section_duration) in enumerate(zip(sections, durations), 1):
    words = re.findall(r"[A-Za-z0-9$]+(?:['’][A-Za-z]+)?", paragraph)
    count = max(1, round(section_duration / 3.0))
    per_beat = max(5, (len(words) + count - 1) // count)
    chunks = [" ".join(words[i:i+per_beat]) for i in range(0, len(words), per_beat)]
    # Rebalance to the section's measured voice duration; target ~3s per beat.
    beat_duration = section_duration / len(chunks)
    for phrase in chunks:
        beat_no += 1
        start, end = elapsed, elapsed + beat_duration
        p0, p1 = start/total*100, min(start+0.22,end)/total*100
        p2, p3 = max(start+0.22,end-0.22)/total*100, end/total*100
        safe = html_escape.escape(phrase)
        words_upper = html_escape.escape(" ".join(words[:0]))  # deterministic empty prefix
        kind = " ".join(phrase.lower().split())
        if any(k in kind for k in ["rent","bill","insurance","groceries","gas","paycheck","paid"]):
            label, fill = "MONEY IN / MONEY OUT", "82%"
        elif any(k in kind for k in ["coffee","delivery","subscription","rideshare","spending","charges","purchase"]):
            label, fill = "SMALL SPENDS ADD UP", "64%"
        elif any(k in kind for k in ["repair","tire","medical","surprise","emergency","breaks"]):
            label, fill = "THE UNEXPECTED HAPPENS", "38%"
        elif any(k in kind for k in ["save","saving","transfer","payday","twenty","twenty-five","fifty"]):
            label, fill = "BUILD THE SAVING HABIT", "56%"
        elif any(k in kind for k in ["hundred","thousand","milestone","progress","five"]):
            label, fill = "MILESTONE PROGRESS", "76%"
        else:
            label, fill = f"THE FIRST $1,000  /  BEAT {beat_no:02d}", "70%"
        beat_cards.append(f'<div class="microbeat" style="animation:microbeat{beat_no} {total:.3f}s linear both"><div class="beat-index">{label}</div><div class="beat-title">{safe}</div><div class="beat-sub">THE FIRST $1,000 — ONE STEP AT A TIME</div><div class="beat-graphic" style="--fill:{fill}"></div></div>')
        beat_css.append(f"@keyframes microbeat{beat_no}{{0%,{p0:.4f}%{{opacity:0;transform:translateY(24px) scale(.98)}}{p1:.4f}%,{p2:.4f}%{{opacity:1;transform:translateY(0) scale(1)}}{p3:.4f}%,100%{{opacity:0;transform:translateY(-16px) scale(1.01)}}}}")
        elapsed = end
stage_markup = '<div id="beat-stage" data-layout-ignore>' + "".join(beat_cards) + '</div>'
html = re.sub(r'<div id="beat-stage"[^>]*>.*?</div>\\s*<audio', stage_markup + '\\n<audio', html, flags=re.S)
html = html.replace('</style>', '\\n.scene .visual{opacity:0}\\n' + '\\n'.join(beat_css) + '\\n</style>')
print(f"VISUAL_BEATS={beat_no} TARGET_SECONDS_PER_BEAT={total/beat_no:.2f}")

html_path.write_text(html)
print("VOICE_DURATIONS=" + ",".join(f"{x:.2f}" for x in durations))
print(f"COMPOSITION_DURATION={total:.2f}")
if total < 210 or total > 255:
    raise SystemExit(f"Episode duration {total:.2f}s outside 3:30–4:15 target")
