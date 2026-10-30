# Free local voice setup

This project uses Kokoro for local text-to-speech. It does not call ElevenLabs, Runway, or another paid voice API.

## Current voice
The storyboard is configured for `am_michael`, a US English male Kokoro voice preset. It is selected in `assets/short_001.json`. The first render should be listened to before publishing to confirm that the voice is a good fit.

## Install
The Python package is listed in requirements.txt. Kokoro downloads its model and voice assets on first run. See the upstream project for current details: https://github.com/hexgrad/kokoro

## Troubleshooting
- If model download fails, check internet access and retry.
- If a line exceeds its scene timing, shorten the narration or extend that scene in the JSON storyboard. The generator deliberately fails rather than silently cutting off a sentence.
- If you have limited RAM/VRAM, close other applications. TTS can run on CPU but will take longer.
- Always listen to the exported voice before posting.
