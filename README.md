# The Money Stickman — Short #001

A vertical 9:16 animated finance explainer with original stick-figure animation, timed captions, sound design and locally generated American-English narration.

## Short concept
**Why Your First $1,000 Is So Hard to Save**

The story follows one recurring stickman character: paycheck arrives, bills chase him, a surprise expense knocks him back, then he starts a tiny automatic savings habit. This is educational storytelling, not a promise of investment returns.

## Render locally (free software)
Tested target: Python 3.11+, FFmpeg, Kokoro TTS.

1. Install FFmpeg and make sure `ffmpeg` and `ffprobe` are on PATH.
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   # Windows: .venv\\Scripts\\activate
   # macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Install Kokoro's voice assets as described in `docs/VOICE_SETUP.md`.
4. Generate narration and render:
   ```bash
   python render_short.py
   ```
5. Find the finished file at `output/first_1000_short.mp4`.

The renderer makes a portrait 1080x1920 H.264/AAC MP4. First run downloads model/voice assets when configured; this is local inference, not a paid API. Voice availability and quality depend on the chosen installed Kokoro voice.

## Files
- `render_short.py`: timed scene animation, captions, voice/audio mix and export.
- `scripts/generate_voice.py`: Kokoro local TTS adapter.
- `assets/short_001.json`: narration, timing and scene plan.
- `docs/VOICE_SETUP.md`: voice setup and troubleshooting.
- `docs/UPLOAD_PACK.md`: title, description, hashtags and pinned comment.

## Transparency
This repository contains the production project. A file is not a published YouTube Short until it has been rendered, reviewed and uploaded in YouTube Studio. Never claim a render or upload completed unless it has.
