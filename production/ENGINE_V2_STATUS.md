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

## Implemented in this branch

### Offline script compiler

`production/scripts/compile_storyboard.py`:
- Splits a supplied script into short narration beats.
- Uses deterministic local keyword rules to choose a scene category, prop, accent and character action.
- Preserves all script words and punctuation; it does not invent financial claims.
- No paid API, cloud LLM, or network request is used.

### Local voice + animation builder

`production/scripts/build_episode.py`:
- Loads Chatterbox locally and generates each narration beat separately with the approved Voice B settings (exaggeration 0.82, CFG 0.28).
- Measures every generated audio segment and uses its measured duration as that scene's duration. There is no arbitrary fixed 35-second timeline and no speech time-stretching.
- Creates one reusable GSAP composition per narration beat, with the recurring SVG character, keyword-selected props, kinetic text, camera-like movement, and scene-specific character actions.
- Writes `narration.wav`, individual beat WAVs, `storyboard.json`, a HyperFrames `index.html`, and the generated compositions.
- Copies the project's local GSAP bundle into the episode folder.
- Auto-selects CPU for GPUs with less than 6 GB VRAM to avoid unreliable low-memory inference.

### Local render and finalization

`production/scripts/run_local.py` is the cross-platform one-command entry point. It builds the episode, runs HyperFrames validation and rendering, then muxes the measured narration into the MP4.

`production/scripts/finalize_episode.py`:
- Refuses to mux if video and audio durations differ by more than 0.20 seconds.
- Verifies 1080x1920 video dimensions.
- Applies loudness normalization and short audio fades without changing speech speed.
- Produces `final/the-money-stickman-short.mp4`.

### Run it locally

Install FFmpeg and Node.js first, then:

```bash
npm install --global hyperframes
python -m pip install -r production/requirements-local.txt
```

Create a UTF-8 text file containing the narration, for example `my-script.txt`, then run from the repository root:

```bash
python production/scripts/run_local.py my-script.txt --output my-episode
```

Optional device selection:

```bash
python production/scripts/run_local.py my-script.txt --output my-episode --device cpu
python production/scripts/run_local.py my-script.txt --output my-episode --device cuda
```

The generated MP4 is at `my-episode/final/the-money-stickman-short.mp4`.

### Automated tests

`tests/test_storyboard_compiler.py` checks chunk limits, finance-topic classification, script text preservation, and scene metadata. GitHub Actions runs Python syntax compilation and these offline tests. No Chatterbox model download is needed for the compiler tests.

## Current limitations and quality gates

- The storyboard compiler is deterministic and keyword-based, not a semantic AI director. It works fully offline but can choose a generic or imperfect visual for ambiguous language.
- Audio is generated one beat at a time so scene boundaries match the generated speech segments exactly. Listen for prosody changes between beats; improve chunking or add a reference voice only if needed.
- Chatterbox Voice B settings reproduce the approved delivery style, but without a supplied reference voice sample they do not guarantee identical speaker identity on every generation.
- This environment has not executed the full local Chatterbox + HyperFrames render. The code and CI compiler tests must pass before claiming a successful MP4.
- Human review of the full MP4 and full narration remains mandatory before publishing. The runner does not upload or publish anything.

## Branch safety

Work is being developed on `engine-v2-foundation`; the default `main` branch is not modified by this change.
