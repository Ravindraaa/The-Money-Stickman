# The Money Stickman — 2D production pilot

The new direction uses a recurring 2D SVG stickman with expressive face, independent limb gestures, cinematic finance backgrounds and fast kinetic type. The three scenes are an 18-second vertical visual pilot, not a finished narrated episode.

## License review
- HyperFrames: Apache-2.0. Official repository: https://github.com/heygen-com/hyperframes
- GSAP: current upstream says its full toolset is free for commercial use under the standard license: https://github.com/greensock/GSAP
- FFmpeg: license depends on build configuration; Ubuntu package is installed by CI. Review codec/build obligations before redistribution.
- Inter: bundled HyperFrames font; no separate font files added.
- SVG character and layouts are original project code.

## Voice
The existing Kokoro am_michael preset is not locked. User selected another voice approach. Do not publish until a natural US male voice has been selected, its model and voice-asset licenses checked, and the final audio listened to. Avoid unofficial hosted endpoints and non-commercial-only model weights.

## Render
Run the GitHub Actions workflow named Render 2D Production Pilot. It checks and renders the composition, then uploads an MP4 artifact. Inspect the rendered MP4 for animation, safe areas, legibility and sound before calling it publish-ready.