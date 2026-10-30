from __future__ import annotations
import shutil
import sys

def main() -> int:
    missing = []
    for binary in ("ffmpeg", "ffprobe"):
        if shutil.which(binary) is None:
            missing.append(binary)
    if missing:
        print("Missing required tools: " + ", ".join(missing))
        print("Install FFmpeg and add its bin directory to PATH.")
        return 1
    try:
        import PIL  # noqa: F401
        import numpy  # noqa: F401
        import soundfile  # noqa: F401
        import kokoro  # noqa: F401
    except Exception as exc:
        print(f"Python dependencies are not ready: {exc}")
        print("Run: pip install -r requirements.txt")
        return 1
    print("Preflight passed. Generate voice, then run render_short.py.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
