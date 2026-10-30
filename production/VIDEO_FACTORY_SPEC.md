# The Money Stickman — Reusable Video Factory

## Product goal
A topic-in, review-ready YouTube Short-out workflow. The creator should only need to choose a topic and approve the finished MP4. Publishing is always a separate, user-approved action.

## Locked channel defaults
- Audience: United States
- Language: natural conversational American English
- Runtime: target 35 seconds; acceptable 30–40 seconds
- Canvas: 1080 × 1920, vertical 9:16, 30 FPS
- Character: recurring original 2D Money Stickman; preserve face, proportions, line weight and visual identity
- Narration: approved Voice B; Chatterbox settings exaggeration=0.82, cfg_weight=0.28
- Animation: GSAP-first for character articulation, gestures, expressions and scene transitions
- Effects: optional local Lottie only when a properly licensed animation asset adds visible value; never a required dependency
- Audio: narration-led mix, restrained background music and synced SFX; do not claim SFX are present until they are actually rendered and inspected
- Captions: burned-in, high contrast, mobile-safe, synchronized to spoken words
- Delivery: review MP4 + narration WAV + script + render metadata

## Topic-only input contract
For each episode, the only required creator input is a topic (for example, "the 24-hour rule for impulse purchases"). The system must derive:
1. A specific US-audience angle and viewer promise.
2. A 0–2 second hook.
3. A relatable mini-story/problem.
4. One actionable, accurate money lesson.
5. A concise close and channel CTA.
6. Scene-by-scene visual beats and character actions.
7. On-screen captions and narration timing.
8. A final title, description and relevant hashtags.

If a topic needs a factual statistic, tax rule, product rate, legal claim or current figure, verify it from reliable current sources before including it. Prefer timeless examples when verification is unnecessary. Clearly label illustrative numbers.

## Editorial structure
- 0–2s: pattern-breaking hook; show the problem immediately.
- 2–8s: relatable situation and stakes.
- 8–22s: visual story with a clear progression; change the visual beat every 2–3 seconds.
- 22–30s: reveal and practical takeaway.
- 30–35s: memorable close and concise follow CTA.
The timings are a pacing guide, not permission to cut words unnaturally.

## Script quality gates
- Target roughly 75–95 spoken words for 35 seconds; adjust after measuring the actual generated voice.
- One main idea per Short. Avoid generic filler and unsupported financial promises.
- Narration must sound natural at normal speed. Do not force-fit a short script by extreme time-stretching.
- If generated narration is outside 30–40 seconds, revise the script or regenerate; do not silently speed it up or slow it down.
- Do not pass the voice gate until the WAV has been checked for duration, clipping, silence and intelligibility.

## Animation quality gates
- Every scene must have meaningful motion, not just static cards sliding in.
- Give the character purposeful actions: walk, point, react, hold/inspect an object, celebrate or show disappointment as appropriate.
- Use layered motion (body, head, arms, legs, props) with stable pivots and no transform conflicts.
- Change composition, scale, camera emphasis or prop state every 2–3 seconds.
- Captions must not cover the face or key action.
- Avoid excessive flashes, random motion and decorative animation that does not support the story.

## Render and QA gates
1. Validate composition and all local assets.
2. Render the visual timeline.
3. Generate narration with the approved voice settings.
4. Measure actual narration duration; reject out-of-range audio rather than applying extreme tempo changes.
5. Mix voice, music and SFX with controlled loudness and fades.
6. Render the final 1080×1920, 30 FPS MP4.
7. Verify with ffprobe: duration, resolution, frame rate, video/audio codecs and audio stream.
8. Inspect the actual MP4 visually and listen to the full audio. Automated checks alone do not establish quality.
9. Upload a review artifact. Do not publish without explicit approval.

## Reliability principles
- Keep the existing HyperFrames + GSAP + FFmpeg pipeline as the stable core.
- Pin dependencies and use local assets; avoid CDN `@latest` references.
- Cache model/dependency downloads where safe.
- Do not rerender the visual timeline when only narration changes, if the pipeline can reuse a validated visual artifact.
- Keep each episode's content and generated assets isolated in its own folder.
- Never mark an item "tested", "working" or "approved" until a real run or human inspection confirms it.

## Current status (2026-10-30)
- Short 02 visual timeline validation and render: passed in workflow run #4.
- Short 02 narration duration check: failed because generated narration was 17.12s against a 27–42s gate.
- Updated Short 02 narration script to a longer 116-word version; a new workflow was triggered. Await its result before calling it successful.
- The current Short 02 compositions are episode-specific, not yet a reusable topic-driven animation template.
- Lottie and D3 are not installed in the production path. GSAP remains the primary animation engine.
