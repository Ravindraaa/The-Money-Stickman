# Engine V2 — implementation status

This branch is the foundation upgrade for the reusable Money Stickman production engine.

## Non-negotiable production defaults

- 9:16, 1080x1920, 30 FPS.
- US audience; conversational American English.
- 30–40 second target, with the actual narration duration measured before visual timing is finalized.
- Recurring Money Stickman identity and consistent SVG proportions.
- Approved Voice B creative profile: Chatterbox, exaggeration 0.82, CFG weight 0.28.
- Visual beat changes every 2–3 seconds, driven by the narration/storyboard rather than arbitrary timers.
- No forced time-stretching to hide a script or timing problem.
- Human review of the actual MP4 and full audio remains mandatory before publishing.

## Implemented in this branch

### Reusable narration engine

`production/scripts/voice_engine.py` replaces the episode-specific hard-coded narration approach for new work.

Example:

```bash
python production/scripts/voice_engine.py \
  --script-file episode/narration.txt \
  --output episode/narration.wav
```

Or:

```bash
python production/scripts/voice_engine.py \
  --text "Paste the complete narration here." \
  --output episode/narration.wav
```

The engine:
- Uses the approved Chatterbox Voice B settings.
- Supports CPU or CUDA selection.
- Validates empty/non-finite audio, duration, peak, RMS and near-silence.
- Protects against clipping.
- Writes a JSON QA report beside the WAV.
- Rejects out-of-range narration instead of unnaturally time-stretching it.

The engine does not claim to prove that a voice sounds natural. A human must listen to the complete WAV.

## Next implementation stages

1. **Script compiler:** turn one supplied script into structured narration beats, caption chunks, scene descriptions, character actions, props, and transition cues. Preserve the exact approved script; never invent factual financial claims.
2. **Voice timing:** generate narration first, measure duration, and align beat boundaries to speech pauses/phrases. Use forced alignment where available; do not distribute words evenly across scenes.
3. **Reusable GSAP scene system:** render data-driven scene templates with layered stickman body parts, facial expressions, props, camera moves, and kinetic typography. A meaningful visual change must occur every 2–3 seconds.
4. **Audio post:** add ducked background music and scene-synced SFX, with fades and loudness checks.
5. **Render orchestrator:** one command accepts a script, creates an isolated episode folder, runs each stage, renders the vertical MP4, and emits title/description/hashtags plus QA metadata.
6. **Automated QA:** verify duration, dimensions, FPS, codecs, audio stream, caption safe areas, scene-change cadence, and no silent/truncated narration.
7. **Human approval:** inspect the MP4 and listen to the audio before upload. Uploading/publishing is always a separate explicit approval.

## Current limitations

- This branch currently implements the reusable narration stage only.
- It does not yet dynamically generate scene compositions from arbitrary scripts.
- The existing HyperFrames compositions remain episode-specific until the GSAP scene system is generalized.
- Chatterbox Voice B settings reproduce the approved delivery style, but without a supplied reference voice sample they do not guarantee identical speaker identity on every generation.
- No render or audio-quality pass is marked successful until executed in the target GitHub Actions environment and reviewed.

## Branch safety

Work is being developed on `engine-v2-foundation`; the default `main` branch is not modified by this change.
