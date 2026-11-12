# Image, voice and video generation

Same principle: assert properties, not pixels or waveforms. Never compare a generated file byte-for-byte or with an exact image diff; outputs differ every run.

## Image generation (e.g. AI product images, room mockups, banners)
- **Shape**: file opens, correct format (PNG/JPEG/WebP), dimensions and aspect ratio, file size limit, colour mode, not blank/single colour (check pixel variance).
- **Must include**: the requested product/object is present (vision model or object detector), brand colours if required, any required text is legible and correctly spelled (OCR), product matches the SKU (colour/material vs catalogue).
- **Must NOT include**: competitor logos, watermarks, distorted/extra limbs or broken geometry, NSFW/violent content (safety classifier), real people's faces if not allowed, wrong product variant, garbled text.
- **Around it**: generation time, fallback image when generation fails, CDN upload and caching, alt text present.
- Checkers: OCR for text; a vision-capable LLM-as-judge with one yes/no question per property (e.g. "Is there exactly one chair in the image?"); CLIP-style similarity score between prompt and image with a threshold; human review on a sample.

## Voice — text-to-speech (TTS)
- **Shape**: plays, correct codec/sample rate, duration within expected range for the text, no clipping or silence gaps beyond X ms, loudness within range.
- **Must include**: transcribe the audio back with STT and compare to input text using Word Error Rate (WER) threshold; numbers, amounts, order IDs and names spoken correctly; correct language/accent.
- **Must NOT include**: extra words, skipped sentences, robotic artefacts (human/MOS rating sample).
- **Around it**: time to first audio byte, streaming works, interruption/barge-in handling, fallback to text.

## Voice — speech-to-text (STT)
- Labelled audio set with reference transcripts; measure **WER** overall and per slice: accents, code-mixed languages, noisy background, low bandwidth, fast speech.
- Critical entities (phone numbers, order IDs, amounts) need exact-match accuracy, not just low WER.
- PII handling: are transcripts masked before storage/analytics?

## Voice bots (STT → LLM → TTS)
Test each stage separately, then end-to-end: a transcription error should be caught by the bot (confirmation for critical values), not silently acted on. Measure end-to-end latency per turn.

## Video generation
- **Shape**: plays, resolution, fps, duration, codec, audio track present and in sync.
- **Must include / not include**: sample frames (e.g. 1 per second) and run the image checks on them; check temporal consistency (product doesn't change colour/shape between frames); captions match audio (STT).
- **Around it**: render time, size, failure fallback, moderation before publishing.

## Reproducibility
Fix seed where the provider allows it; log model, version, seed, prompt and settings. For safety-critical properties (NSFW, logos, wrong product) require 100% pass on the run set; for quality properties use pass-rate thresholds plus human review.

## Output: Media checks
| Property | Bucket | Checker (code / OCR / STT+WER / vision judge / human) | Threshold |
