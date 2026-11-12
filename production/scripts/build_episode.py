#!/usr/bin/env python3
"""Build a complete local episode: Chatterbox beat audio + GSAP scene compositions."""
from __future__ import annotations
import argparse, json, re, sys, shutil
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
from chatterbox.tts import ChatterboxTTS
from compile_storyboard import compile_beats
from scene_renderer import build_hyperframes

VOICE_EXAGGERATION, VOICE_CFG = 0.82, 0.28
GAP_SECONDS = 0.08
VOICE_CHUNK_WORDS = 14

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
