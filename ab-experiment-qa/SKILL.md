---
name: ab-experiment-qa
description: Plan and run QA for A/B tests, feature-flag experiments and multivariate rollouts - build the variant x platform x user-state test matrix, verify bucketing and stickiness, control/variant isolation, exposure and conversion analytics per variant, fallbacks when the experiment service fails, and how to pin variants for automation; then check results for sample ratio mismatch and tracking gaps. Use this whenever the user mentions an experiment, A/B test, variant A/B/C, control vs treatment, feature flag rollout, split test, bucketing, exposure event, or shares an experiment PRD/config and asks what to test - even if they don't say "experiment QA".
---

# A/B Experiment QA

An experiment can fail in two ways: the feature is broken in one variant, or the experiment itself is
broken (wrong users bucketed, variants leaking into each other, exposure not tracked). The second kind
silently ruins weeks of data and the decision made from it, so it gets as much testing as the UI.

## Inputs
Experiment PRD or brief, variant definitions, targeting rules, allocation %, platforms, the flag/experiment
tool (LaunchDarkly, Optimizely, GrowthBook, Firebase, in-house), analytics spec (exposure and goal events).

## Workflow

1. **Summarise the experiment** in a table: variants and what differs, allocation, targeting (who is
   eligible), platforms, start/stop conditions, primary and guardrail metrics, exposure event.
2. **Build the test matrix.** Rows = variant x platform x user state. User states usually include:
   new vs returning, logged-in vs guest, eligible vs not eligible (targeting), and any state the
   feature depends on (empty cart, existing subscription, region). Prune combinations that cannot
   differ, and say what you pruned.
3. **Add experiment-mechanics tests** from `references/experiment-checks.md`: bucketing, stickiness
   across sessions/devices/login, isolation, exposure timing, fallback/default, kill switch, cache.
4. **Add analytics tests:** exposure fires once per user per experiment at the moment the user actually
   sees the variant (not on app start), carries the variant name, and goal events carry or can be joined
   to the variant. No PII in experiment payloads.
5. **Automation plan:** how to force each variant (query param, header, cookie, flag override, test
   user allow-list), and keep automated tests deterministic by pinning variants. Never let automation
   traffic count in experiment results (exclude test users or use a test environment).
6. **Post-launch checks (if the user shares data):** sample ratio mismatch (observed split vs planned,
   chi-square), exposure count vs eligible users, variants with zero goal events, platform skew.

## Output

```
## Experiment QA plan: <name>

Experiment summary: (table)
Test matrix: | # | Variant | Platform | User state | What to verify | Priority |
Experiment mechanics: | # | Check | How | Expected |
Analytics: | Event | When it should fire | Required attributes | Check |
Automation: <how to pin each variant; how test traffic is excluded>
Risks and open questions: ...
```

Offer the matrix as CSV for a test management tool. For a sample ratio check, show the calculation.
