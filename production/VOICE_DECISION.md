# Voice selection — approved for production pilot

## Decision
The user listened to both Chatterbox auditions and approved **Voice B** (higher-energy delivery) for The Money Stickman.

## Selected generation settings
- Engine: Chatterbox TTS
- Delivery: brighter, more expressive American-English male narration
- Exaggeration: 0.82
- CFG weight: 0.28
- Audition text: "Your paycheck just hit. Nice! But wait... where did ALL that money go? Let's break it down."

## Production notes
- Use Voice B as the default narrator for Short #1 and subsequent pilot drafts.
- Keep the approved audition as the reference for energy and pacing; tune per-script pauses and emphasis without changing the voice identity.
- Before public monetized release, verify the current Chatterbox model-weight and voice-output terms for the exact deployed version. The audition approval is a creative decision, not a legal clearance.
- Keep generated audio artifacts out of source control; store them as workflow artifacts.
