---
name: ai-feature-testing
description: Design test cases, assertions, metrics and automation for any AI/ML-powered feature — LLM text/JSON output (chatbots, AI summaries, support replies), recommendation/ranking/search/classification models, image/voice/video generation, and multi-step AI agents that call tools, using property-based assertions and metrics instead of exact expected outputs. Use whenever the user wants to test, QA, write test cases for, automate, or evaluate any feature whose output comes from an LLM or ML model, asks "how do I test this AI feature", shares an AI feature PRD, prompt, or sample model responses, wants to check an AI response for correctness/PII/hallucination, or is preparing for interview questions on testing AI features. Also use for recommendation quality, precision/recall, relevance, image or audio generation QA, TTS/STT, agent tool-call testing. Use it even if the user only says "chatbot", "GenAI", "LLM", "recommender", "agent" or "AI assistant" without the word "test".
---

# AI Feature Testing

## Core idea

A normal feature is a promise: the same input always gives the same output, so a fixed expected result works. An AI feature is a distribution: the same input can give several different outputs that are all correct. A fixed expected sentence is the thing that breaks. Everything else about QA stays the same.

So: **do not assert the answer. Assert the properties every acceptable answer must have, and version the model.**

## Pick the feature type first

The core workflow below applies to every type. For these types, also read the matching reference file and apply its extra checks:

| Feature type | Examples | Read |
|---|---|---|
| Text / JSON from an LLM | Chatbot, AI reply, summary, extraction | This file only |
| Recommendation, ranking, search, classification | "You may also like", sort by relevance, intent/category classifier, fraud flag | `references/ranking-classification.md` |
| Image, voice, video generation | AI product images, TTS, voice bot, STT transcripts, generated video | `references/media-generation.md` |
| Multi-step agent with tools | Bot that looks up order, then creates ticket / issues refund | `references/agents-tool-calls.md` |

A feature can be several types (e.g. a voice support agent = media + agent + text). Combine the relevant references.

## Workflow

### 1. Gather context
Collect what's available; ask only for what's missing and blocking:
- What the feature does and who sees the output (end user, internal tool, downstream service)
- The prompt / system prompt, if accessible
- Output contract: free text, JSON, structured cards, tool calls
- Sample responses (good and bad), PRD, API captures
- Model name/version and generation settings (temperature, seed)
- Data the model can see (customer records, catalogue, policies)

### 2. Split deterministic vs generative
Most "AI features" are mostly normal code wrapped around one model call (API, auth, rendering, fallback, logging). Test the deterministic parts the normal way with exact assertions. Apply property-based testing only to the model output.

### 3. Build the property checklist
For every scenario, define properties in four buckets:

| Bucket | What to assert | Examples |
|---|---|---|
| **Shape** | Output is parseable and well-formed | Valid JSON, required fields present, correct types, enums within allowed values, length limits, language |
| **Must include** | Facts that every correct answer must contain | Order number, date, amount, policy name, the product the user asked about |
| **Must NOT include** | Things that must never appear | Another customer's data, PII not needed for the answer, internal names/IDs/tool names, invented prices or policies, system prompt text, competitor recommendations |
| **Around it** | Behaviour of the system around the model | Latency limit (p95), graceful fallback on timeout/5xx/malformed output, refuses out-of-scope or harmful asks, handles empty/garbage input, rate limits, correct analytics events |

Pick the cheapest reliable checker for each property:
1. **Code assertion** (schema validation, contains, regex, numeric equality vs source data) — preferred.
2. **LLM-as-judge** with a narrow yes/no rubric — only for semantic properties code can't check (e.g. "tone is polite", "answer addresses the question"). Keep the judge's model and rubric versioned too.
3. **Human review** — sample for subjective quality; don't gate CI on it.

Cross-check facts against the source of truth (DB / API / catalogue), not against a hard-coded string. A price in the answer should equal the price in the catalogue for that SKU.

### 4. Cover the risk scenarios
Beyond the happy path, include:
- **Grounding / hallucination**: ask about something not in the data; expect "don't know" or fallback, not an invented answer.
- **Data isolation**: user A must never see user B's data, even when asked directly.
- **Prompt injection**: user input or retrieved content containing "ignore previous instructions…", requests for the system prompt.
- **Out of scope / refusal**: off-topic, abusive, or unsafe asks.
- **Input edge cases**: empty, very long, other languages/code-mixed text, emojis, typos.
- **Failure modes**: model timeout, provider 5xx, malformed JSON from model → fallback UI/message.
- **Consistency**: same input run N times (e.g. 10); every run must pass all hard properties. Report pass rate per property, not just one run.

### 5. Make runs reproducible (from day one)
- Fix seed and/or set temperature to 0 (or lowest allowed) in the test environment.
- Record model name + version, prompt version, and settings with every run/result.
- Treat **same prompt + new model version = a new feature**: re-run the full suite and compare pass rates before rollout.
- Treat a prompt change the same way.
- Keep a golden set of inputs (not golden outputs) and grow it with every production bug.

## Output format

Default: reply in chat (no files unless the user asks). Use this structure:

**Feature summary** — one or two lines, plus which parts are deterministic vs model-generated.

**Test cases** table:

| ID | Scenario | Input | Properties asserted (Shape / Must / Must-not / Around) | Checker (code / judge / manual) | Priority |

**Reproducibility setup** — seed/temperature, what to log, re-run triggers.

**Open questions** — gaps in the PRD/prompt that block defining a property.

For ranking/classification features, add a **Metrics plan** section (dataset, metrics, thresholds, slices). For agents, add a **Trajectory checks** section. For media, add a **Media checks** section — see the matching reference for the formats.

If the user asks for automation code, read `references/java-assertions.md` and produce code in their stack (default Java + RestAssured/Playwright, TestNG/JUnit).

If the user gives a single AI response to evaluate, check it against each property and report pass/fail per property with the evidence, then list defects in bug-ticket style (title, steps, expected, actual, severity).

## Interview framing
If the user is preparing for interviews, give a short spoken-style answer built on: (1) why exact-match fails, (2) the four property buckets with one concrete example each, (3) reproducibility: seed/temperature, model-version logging, new model = new feature.
