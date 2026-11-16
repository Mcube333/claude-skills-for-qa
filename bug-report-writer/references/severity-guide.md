# Severity and priority guide

Adapt names to the team's tracker, but keep the meaning.

## Severity (technical impact)

| Severity | Meaning | Typical examples |
|---|---|---|
| Critical | Core flow blocked, data loss or corruption, security or privacy breach, money charged wrongly, crash on launch | Payment captured but order not created; PII sent to a third party; checkout button does nothing |
| Major | A main feature works incorrectly or a key path fails for a segment of users; workaround is hard | Coupon removed silently at checkout; wrong price shown for one tenure; API 500 on one platform |
| Minor | Feature works but with incorrect detail; easy workaround; cosmetic issue in an important area | Wrong rounding in a breakdown row; tooltip copy mismatch with spec; misaligned label |
| Trivial | Cosmetic, no functional impact, low visibility | Extra space, icon off by a few pixels on a rarely used screen |

## Priority (business urgency)

| Priority | Meaning |
|---|---|
| P1 | Fix before release / hotfix now. Blocks launch, affects revenue, compliance or many users |
| P2 | Fix in this release or sprint |
| P3 | Fix soon; schedule in a later sprint |
| P4 | Nice to fix; backlog |

## Things that raise priority

- Affects payment, pricing, checkout, login or sign-up
- Visible on the first screen users see, or in marketing / app store screenshots
- Legal, privacy or accessibility exposure
- Part of a running A/B experiment (corrupts results)
- Regression of something that used to work
