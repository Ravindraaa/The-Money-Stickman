#!/usr/bin/env python3
"""Mux locally generated beat-aligned narration into the HyperFrames render."""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

def probe(path: Path) -> dict:
    raw=subprocess.check_output([
        "ffprobe","-v","error","-show_entries",
        "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate",
        "-of","json",str(path)],text=True)
    return json.loads(raw)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--episode-dir",type=Path,required=True)
    a=p.parse_args()
    try:
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise RuntimeError("FFmpeg and ffprobe must be installed and on PATH.")
        videos=sorted((a.episode_dir/"renders").glob("*.mp4"))
        if not videos: raise FileNotFoundError("No HyperFrames MP4 found in renders/.")
        video=videos[0]; audio=a.episode_dir/"narration.wav"
        if not audio.is_file(): raise FileNotFoundError("narration.wav is missing.")
        vp=probe(video); ap=probe(audio)
        vdur=float(vp["format"]["duration"]); adur=float(ap["format"]["duration"])
        vstream=next(s for s in vp["streams"] if s["codec_type"]=="video")
        if int(vstream.get("width",0))!=1080 or int(vstream.get("height",0))!=1920:
            raise ValueError(f"Expected 1080x1920 render, got {vstream.get('width')}x{vstream.get('height')}.")
        if abs(vdur-adur)>0.20:
            raise ValueError(f"Video/audio duration mismatch: video={vdur:.3f}s audio={adur:.3f}s. Refusing to time-stretch.")
        out=a.episode_dir/"final"; out.mkdir(exist_ok=True)
        target=out/"the-money-stickman-short.mp4"
        final_duration=min(vdur,adur)
        fade_start=max(0.0,final_duration-0.18)
        audio_filter=f"[1:a]loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d=0.10,afade=t=out:st={fade_start:.4f}:d=0.18[voice]"
        subprocess.run([
            "ffmpeg","-y","-i",str(video),"-i",str(audio),
            "-filter_complex",audio_filter,
            "-map","0:v:0","-map","[voice]","-c:v","copy","-c:a","aac","-b:a","192k",
            "-t",f"{min(vdur,adur):.4f}","-movflags","+faststart",str(target)
        ],check=True)
        result=probe(target)
        print(json.dumps({"output":str(target),"duration":result["format"]["duration"],
            "streams":result["streams"],"human_review_required":True},indent=2))
        print(f"FINAL MP4: {target}")
        return 0
    except Exception as exc:
        print(f"FINALIZE FAILED: {exc}")
        return 1
if __name__=="__main__": raise SystemExit(main())
