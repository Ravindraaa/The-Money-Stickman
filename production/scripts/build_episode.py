#!/usr/bin/env python3
"""Build a complete local episode: Chatterbox beat audio + GSAP scene compositions."""
from __future__ import annotations
import argparse, html, json, re, sys, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS
from compile_storyboard import compile_beats

W, H = 1080, 1920
VOICE_EXAGGERATION, VOICE_CFG = 0.82, 0.28
GAP_SECONDS = 0.08
VOICE_CHUNK_WORDS = 14

def svg_character() -> str:
    # Shared character geometry: keep proportions and face consistent in every scene.
    return """<svg class="stickman" viewBox="0 0 360 620" aria-label="The Money Stickman">
    <ellipse cx="180" cy="574" rx="92" ry="18" fill="#020817" opacity=".55"/>
    <g class="body" stroke="#f8fafc" stroke-width="20" stroke-linecap="round" fill="none">
      <path class="torso" d="M180 190V395"/>
      <path class="arm-left" d="M174 230L94 310L52 260"/>
      <path class="arm-right" d="M186 230L266 300L310 235"/>
      <path class="leg-left" d="M180 395L125 485L105 555"/>
      <path class="leg-right" d="M180 395L235 485L260 555"/>
    </g>
    <circle cx="180" cy="112" r="78" fill="#f8fafc"/>
    <ellipse cx="153" cy="112" rx="9" ry="14" fill="#0b1730"/>
    <ellipse cx="207" cy="112" rx="9" ry="14" fill="#0b1730"/>
    <path class="mouth" d="M151 151Q180 177 209 151" stroke="#0b1730" stroke-width="8" fill="none" stroke-linecap="round"/>
    </svg>"""

def scene_html(beat: dict, number: int) -> str:
    caption = html.escape(beat["caption"])
    label = html.escape(beat["label"])
    icon = html.escape(beat["icon"])
    accent = beat["accent"]
    action = beat["action"]
    return f'''<template>
<style>
#root{{position:absolute;inset:0;overflow:hidden;background:radial-gradient(ellipse at 50% 38%,#203d62 0%,#0a1629 58%,#050914 100%);font-family:Inter,Arial,sans-serif;color:#fff}}
.grid{{position:absolute;inset:0;opacity:.28;background-image:linear-gradient(#ffffff0b 1px,transparent 1px),linear-gradient(90deg,#ffffff0b 1px,transparent 1px);background-size:76px 76px}}
.glow{{position:absolute;width:760px;height:760px;left:160px;top:450px;border-radius:50%;background:{accent};opacity:.10;filter:blur(100px)}}
.brand{{position:absolute;top:160px;width:100%;text-align:center;font-size:25px;font-weight:900;letter-spacing:7px;color:#9fb5d5}}
.eyebrow{{position:absolute;top:275px;width:100%;text-align:center;font-size:25px;font-weight:900;letter-spacing:5px;color:{accent}}}
.headline{{position:absolute;top:355px;left:70px;right:70px;text-align:center;font-size:66px;line-height:1.08;font-weight:950;overflow-wrap:anywhere}}
.stage{{position:absolute;top:650px;left:0;right:0;height:820px}}
.stickman{{position:absolute;left:50%;top:130px;width:350px;height:610px;margin-left:-175px;filter:drop-shadow(0 22px 30px #0008)}}
.prop{{position:absolute;left:690px;top:230px;width:190px;height:190px;border-radius:42px;display:grid;place-items:center;font-size:105px;background:#ffffff12;border:2px solid #ffffff24;box-shadow:0 25px 70px #0005}}
.floor{{position:absolute;bottom:30px;left:130px;right:130px;height:10px;border-radius:50%;background:{accent};filter:blur(13px);opacity:.7}}
.caption{{position:absolute;bottom:205px;left:58px;right:58px;min-height:130px;display:flex;align-items:center;justify-content:center;text-align:center;padding:24px 28px;box-sizing:border-box;border-radius:26px;background:#071326ed;border:1px solid #ffffff26;font-size:37px;line-height:1.18;font-weight:850;box-shadow:0 20px 55px #0006}}
.number{{position:absolute;bottom:115px;right:72px;color:#8ca3c4;font-size:22px;font-weight:800;letter-spacing:3px}}
@keyframes drift{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(-18px)}}}}
@keyframes pulse{{0%,100%{{transform:scale(1)}}50%{{transform:scale(1.08)}}}}
</style>
<div id="root" data-composition-id="beat-{number:03d}" data-width="{W}" data-height="{H}">
<div class="grid"></div><div class="glow"></div>
<div class="brand">THE MONEY STICKMAN</div>
<div class="eyebrow">BEAT {number:02d} • {label}</div>
<div class="headline">{label}</div>
<div class="stage"><div class="floor"></div>{svg_character()}<div class="prop">{icon}</div></div>
<div class="caption">{caption}</div><div class="number">BEAT {number:02d}</div>
</div>
<script>
const tl=gsap.timeline({{paused:true}});
tl.fromTo(".eyebrow",{{y:-35,opacity:0}},{{y:0,opacity:1,duration:.28,ease:"back.out(1.7)"}})
.fromTo(".headline",{{y:75,scale:.84,opacity:0,filter:"blur(12px)"}},{{y:0,scale:1,opacity:1,filter:"blur(0px)",duration:.42,ease:"back.out(1.5)"}},.08)
.fromTo(".stickman",{{y:125,scale:.72,opacity:0}},{{y:0,scale:1,opacity:1,duration:.48,ease:"back.out(1.7)"}},.18)
.fromTo(".prop",{{x:150,y:60,rotation:-24,scale:.45,opacity:0}},{{x:0,y:0,rotation:0,scale:1,opacity:1,duration:.42,ease:"back.out(2)"}},.32)
.fromTo(".caption",{{y:65,opacity:0}},{{y:0,opacity:1,duration:.34,ease:"power2.out"}},.38);
if("{action}"==="shock"){{tl.to(".stickman",{{x:-24,rotation:-7,duration:.16,yoyo:true,repeat:3}},.85).to(".prop",{{rotation:12,scale:1.12,duration:.18,yoyo:true,repeat:1}},.88);}}
else if("{action}"==="celebrate"){{tl.to(".stickman",{{y:-25,rotation:4,duration:.24,yoyo:true,repeat:2,ease:"sine.inOut"}},.85).to(".prop",{{y:-28,rotation:12,duration:.3,yoyo:true,repeat:1}},.9);}}
else if("{action}"==="grab"){{tl.to(".arm-right",{{rotation:-34,transformOrigin:"10% 10%",duration:.22,yoyo:true,repeat:1}},.82).to(".prop",{{x:-90,y:-45,scale:1.12,duration:.35,ease:"power2.out"}},.9);}}
else if("{action}"==="point"){{tl.to(".arm-left",{{rotation:28,transformOrigin:"100% 10%",duration:.2,yoyo:true,repeat:1}},.82).to(".prop",{{x:22,duration:.2,yoyo:true,repeat:3}},.9);}}
else if("{action}"==="react"){{tl.to(".stickman",{{rotation:5,x:18,duration:.2,yoyo:true,repeat:2}},.84).to(".mouth",{{attr:{{d:"M151 158Q180 130 209 158"}},duration:.18}},.9);}}
else{{tl.to(".stickman",{{y:-15,duration:.28,yoyo:true,repeat:2}},.9).to(".prop",{{rotation:8,duration:.28,yoyo:true,repeat:1}},1);}}
tl.to(".glow",{{opacity:.18,duration:.45,yoyo:true,repeat:1}},.9);
window.__timelines=window.__timelines||{{}};window.__timelines["beat-{number:03d}"]=tl;
</script></template>'''

def build_hyperframes(beats: list[dict], out_dir: Path):
    comp_dir = out_dir / "compositions"
    comp_dir.mkdir(parents=True, exist_ok=True)
    start = 0.0
    sections = []
    for i, beat in enumerate(beats, 1):
        duration = float(beat["duration"])
        if duration <= 0: raise ValueError(f"Invalid beat duration for {beat['id']}")
        (comp_dir / f"beat-{i:03d}.html").write_text(scene_html(beat, i), encoding="utf-8")
        sections.append(
            f'<div id="beat-{i:03d}" data-composition-id="beat-{i:03d}" '
            f'data-composition-src="compositions/beat-{i:03d}.html" '
            f'data-start="{start:.4f}" data-duration="{duration:.4f}" '
            f'data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>'
        )
        start += duration
    root = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
            f'<title>The Money Stickman — Generated Episode</title></head><body>'
            f'<div id="root" data-composition-id="main" data-start="0" data-duration="{start:.4f}" '
            f'data-width="{W}" data-height="{H}">{"".join(sections)}</div>'
            f'<script src="vendor/gsap.min.js"></script>'
            f'<script>window.__timelines=window.__timelines||{{}};window.__timelines.main=gsap.timeline({{paused:true}});</script>'
            f'</body></html>')
    (out_dir / "index.html").write_text(root, encoding="utf-8")
    return start

def main():
    p=argparse.ArgumentParser(description="Build a local script-to-Short episode.")
    p.add_argument("--script-file",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,default=Path("episode"))
    p.add_argument("--max-words",type=int,default=7)
    p.add_argument("--device",choices=("auto","cpu","cuda"),default="auto")
    a=p.parse_args()
    try:
        script=re.sub(r"\s+"," ",a.script_file.read_text(encoding="utf-8")).strip()
        if not script: raise ValueError("Script is empty.")
        beats=compile_beats(script,a.max_words)
        if not beats: raise ValueError("No narration beats were produced.")
        if a.device=="auto":
            # A 4 GB laptop GPU is too tight for reliable Chatterbox inference.
            has_room = torch.cuda.is_available() and torch.cuda.get_device_properties(0).total_memory >= 6 * 1024**3
            device = "cuda" if has_room else "cpu"
        else:
            device = a.device
        if device=="cuda" and not torch.cuda.is_available(): raise RuntimeError("CUDA is unavailable.")
        a.output_dir.mkdir(parents=True,exist_ok=True)
        audio_dir=a.output_dir/"audio"; audio_dir.mkdir(exist_ok=True)
        vendor_dir=a.output_dir/"vendor"; vendor_dir.mkdir(exist_ok=True)
        project_gsap=Path(__file__).resolve().parents[1]/"vendor"/"gsap.min.js"
        if not project_gsap.is_file(): raise FileNotFoundError(f"Missing GSAP bundle: {project_gsap}")
        shutil.copy2(project_gsap,vendor_dir/"gsap.min.js")
        print(f"Loading local Chatterbox model on {device} for {len(beats)} beats...")
        model=ChatterboxTTS.from_pretrained(device=device)
        full_audio=[]
        sr=int(model.sr)
        # Generate two visual beats together to retain more natural phrase-level prosody.
        voice_groups=[]
        pending=[]
        pending_words=0
        for beat in beats:
            pending.append(beat)
            pending_words += len(beat["text"].split())
            if pending_words >= VOICE_CHUNK_WORDS:
                voice_groups.append(pending)
                pending=[]
                pending_words=0
        if pending:
            voice_groups.append(pending)

        for group_index, group in enumerate(voice_groups,1):
            spoken_text=" ".join(item["text"] for item in group)
            print(f"[voice {group_index}/{len(voice_groups)}] Voice B: {spoken_text}")
            wav=model.generate(spoken_text,exaggeration=VOICE_EXAGGERATION,cfg_weight=VOICE_CFG)
            samples=wav.detach().float().cpu().squeeze().numpy().astype(np.float32).reshape(-1)
            if not samples.size or not np.isfinite(samples).all():
                raise ValueError(f"Bad audio in voice chunk {group_index}")
            gap=np.zeros(int(sr*GAP_SECONDS),dtype=np.float32)
            segment=np.concatenate([samples,gap])
            total_words=sum(len(item["text"].split()) for item in group)
            elapsed=0.0
            for local_index, beat in enumerate(group):
                share=len(beat["text"].split())/total_words
                duration=len(segment)/sr*share
                if local_index==len(group)-1:
                    duration=len(segment)/sr-elapsed
                beat["duration"]=round(duration,6)
                beat["audio"]=f"audio/voice-{group_index:03d}.wav"
                beat["voice_chunk"]=group_index
                elapsed += duration
            sf.write(a.output_dir/f"audio/voice-{group_index:03d}.wav",segment,sr,subtype="PCM_16")
            full_audio.append(segment)
        joined=np.concatenate(full_audio)
        sf.write(a.output_dir/"narration.wav",joined,sr,subtype="PCM_16")
        total=build_hyperframes(beats,a.output_dir)
        (a.output_dir/"storyboard.json").write_text(json.dumps({
            "version":2,"source":"local-rule-based","voice":"Chatterbox Voice B profile",
            "sample_rate":sr,"duration_seconds":round(total,3),"beats":beats
        },indent=2)+"\n",encoding="utf-8")
        print(f"\nBUILD COMPLETE: {a.output_dir}")
        print(f"Beats: {len(beats)} | Duration: {total:.2f}s | Voice: local Chatterbox")
        print("Next: run HyperFrames check/render in this episode directory, then mux narration.wav.")
        return 0
    except Exception as exc:
        print(f"BUILD FAILED: {exc}",file=sys.stderr)
        return 1
if __name__=="__main__": raise SystemExit(main())
