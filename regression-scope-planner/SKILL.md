---
name: regression-scope-planner
description: Decide what to regression-test for a release, hotfix or pull request, based on risk instead of "run everything". Takes a PR diff, list of changed files, commit log, release notes, Jira/Linear ticket list or a plain description of what changed, maps each change to impacted features and user flows (including indirect impact through shared components, APIs, data and config), ranks them by risk, and produces a prioritised regression plan - must-test, should-test, safe-to-skip with reasons - plus which automated suites to run and what needs manual or exploratory testing. Use this whenever the user asks "what should I test for this release/PR/hotfix", "regression scope", "impact analysis", "what areas are affected", "we have only X hours to test", shares a diff or release notes and wants a test plan, or needs to justify a reduced regression to a manager - even if they don't say "regression".
---

# Regression Scope Planner

Full regression is rarely affordable, and "test everything lightly" catches little. The goal is a plan
a QA lead can defend: test hardest where change and business risk meet, and say explicitly what is
skipped and why, so the risk is a decision, not an accident.

## Inputs (use whatever the user has)

- PR diff, changed-file list, commit messages
- Release notes, ticket list (titles, descriptions, labels)
- Architecture notes, module/ownership map, past incidents or flaky areas
- Time budget and team size; platforms in scope (web, iOS, Android, API)
- Existing test suites (names, tags, what they cover)

If the only input is a short description, still produce a plan, and list the assumptions you made.

## Workflow

1. **List the changes.** One row per change: what changed, where (file/module/service/screen), and type:
   new feature, behaviour change, bug fix, refactor, dependency/library upgrade, config/feature flag,
   data/schema migration, copy/UI-only.
2. **Trace the impact.** For each change, find:
   - *Direct* impact: the feature or screen that changed.
   - *Indirect* impact: anything that shares the changed code, component, API endpoint, database
     table, event, config or library. Shared things are where regressions hide. Read
     `references/impact-patterns.md` for common hidden dependencies (shared UI components, pricing and
     totals, auth/session, analytics, caching, feature flags, migrations, third-party SDKs).
   - Platforms affected (a backend change hits every client; a shared design-system change hits every screen).
3. **Score risk** for every impacted area with the model below. Keep the reasoning short and visible.
4. **Bucket the areas:**
   - **Must test** - high risk; blocks release if it fails.
   - **Should test** - medium risk; test if time allows, or cover with automation.
   - **Safe to skip** - low risk; state why (untouched, covered by green automation, UI-only text change, etc.).
5. **Map to execution.** For each must/should area say how it is covered: which automated suite or
   tag to run, what needs manual or exploratory testing, what needs specific test data, devices or
   accounts. Fit the plan into the user's time budget; if it doesn't fit, say what to drop first.
6. **Name the residual risk** in two or three lines a manager can read: what we are not testing and
   what could go wrong because of it.

## Risk model

Score each impacted area 1-3 on each factor, then multiply Likelihood x Impact (1-9).

- **Likelihood of breaking:** size and complexity of the change, shared code touched, no unit tests,
  history of bugs or flakiness, new library version, migration or config change. (1 low - 3 high)
- **Impact if broken:** money (payments, pricing, orders), access (login, sign-up), data integrity,
  legal/privacy, number of users, running experiments, hard-to-revert releases (mobile apps). (1 low - 3 high)

7-9 = Must test, 4-6 = Should test, 1-3 = Safe to skip (unless the user has a reason to include it).

Always put these in Must test when they are touched directly or indirectly: payment and checkout,
pricing and totals, login/session, data migrations, anything that writes or deletes user data,
privacy and analytics payloads.

## Output format

```
## Regression scope: <release / PR name>

Summary: <2-3 lines: what changed, total areas, how many must/should/skip, estimated effort>

### Changes
| # | Change | Where | Type |

### Regression plan
| Area / flow | Why impacted | Likelihood | Impact | Risk | Bucket | How to cover (suite / manual / data) | Platforms |
(sorted by risk, highest first)

### Safe to skip
- <area>: <reason>

### Execution order
1. <smoke / automation to run first>
2. <must-test manual or exploratory areas>
3. <should-test areas if time allows>

### Residual risk
<what is not covered and why that is acceptable, or what needs sign-off>

### Assumptions and open questions
- ...
```

Keep the plan as short as the release allows: a one-line copy fix gets a three-row table, not a report.
If the user wants it as a sheet, offer the regression plan table as CSV.
