#!/usr/bin/env python3
"""Cross-platform one-command local production runner."""
from __future__ import annotations
import argparse, shutil, subprocess, sys
from pathlib import Path

def run(command, cwd=None):
    print("\n$", " ".join(map(str, command)), flush=True)
    subprocess.run(list(map(str,command)),cwd=cwd,check=True)

def main():
    p=argparse.ArgumentParser(description="Script in, rendered Money Stickman Short out.")
    p.add_argument("script",type=Path,help="Plain-text UTF-8 narration script")
    p.add_argument("--output",type=Path,default=Path("episode-output"))
    p.add_argument("--device",choices=("auto","cpu","cuda"),default="auto")
    p.add_argument("--max-words",type=int,default=7)
    a=p.parse_args()
    try:
        root=Path(__file__).resolve().parents[1]
        script=a.script.resolve()
        output=a.output.resolve()
        if not script.is_file(): raise FileNotFoundError(f"Script not found: {script}")
        if shutil.which("hyperframes") is None:
            raise RuntimeError("HyperFrames CLI missing. Install it with: npm install --global hyperframes")
        run([sys.executable,root/"scripts"/"build_episode.py","--script-file",script,
             "--output-dir",output,"--device",a.device,"--max-words",a.max_words])
        run(["hyperframes","check","--json"],cwd=output)
        run(["hyperframes","render"],cwd=output)
        run([sys.executable,root/"scripts"/"finalize_episode.py","--episode-dir",output])
        print("\nSUCCESS: review the MP4 in",output/"final"/"the-money-stickman-short.mp4")
        print("Listen to the full narration and inspect the full video before publishing.")
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"PIPELINE FAILED at command exit code {exc.returncode}",file=sys.stderr)
        return exc.returncode or 1
    except Exception as exc:
        print(f"PIPELINE FAILED: {exc}",file=sys.stderr)
        return 1
if __name__=="__main__": raise SystemExit(main())
