# Turning resume lines into interview questions

Interviewers probe every claim. For each resume bullet, generate questions from these angles:

| Angle | Question template |
|---|---|
| Ownership | "What exactly did you build yourself, and what did the team do?" |
| Design | "Walk me through the architecture. Why that choice over <alternative>?" |
| Numbers | "How did you measure <x>% / <n> tests? Baseline? Over what period?" |
| Problems | "What was the hardest problem in this, and how did you solve it?" |
| Trade-offs | "What would you do differently now?" |
| Depth | Pick one technology in the bullet and go two levels deep. |
| Impact | "What changed for the team or the users because of this?" |

Examples:
- "Built a Java + Playwright framework with 98 tests" -> How is it structured? How do tests run in parallel? How do you handle test data and A/B variants? How long does a run take? Flakiness rate?
- "Reduced regression time by 45%" -> From what to what? How measured? What did you automate first and why?
- "Found PII in analytics payloads" -> How did you find it? What was the impact? How did you make sure it does not come back?
- "Migrated a suite from Python to Java" -> Why migrate? How did you keep coverage during the move? How did you verify parity?

Also ask about public projects: open the README if available and question one design decision.
