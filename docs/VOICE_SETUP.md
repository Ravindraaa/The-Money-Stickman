# Free local voice setup

This project uses Kokoro for local text-to-speech. It does not call ElevenLabs, Runway, or another paid voice API.

## Install
The Python package is listed in requirements.txt. Kokoro also needs its model weights and voice pack. Follow the current installation instructions from the upstream Kokoro project: https://github.com/hexgrad/kokoro

The starter voice preset is `af_heart` (American female). Change `assets/short_001.json` voice to an installed US male preset offered by your downloaded voice pack to audition a male narration. Voice IDs vary by Kokoro release; do not guess a preset name if your installed release doesn't list it.

## Troubleshooting
- If model download fails, check internet access and retry the first run.
- If audio sounds clipped, reduce the voice speed slightly.
- If you have limited RAM/VRAM, close other applications. TTS can run on CPU but will take longer.
- Always listen to the exported voice before posting. Do not post the preview without review.

## Why the initial preset is female
The starter configuration uses a known common American preset rather than claiming a male voice has been tested here. Select and audition the male voice available in your installed voice pack before publishing.
