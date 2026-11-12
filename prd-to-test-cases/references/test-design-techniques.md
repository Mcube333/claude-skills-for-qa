# Test design techniques & priority rubric

## Priority rubric

| Priority | Use when | Examples |
|---|---|---|
| P0 | Core happy path of the feature; money, orders, data loss, security/authorization; anything that blocks release if broken | Place order with coupon; payment success updates order; user can't see another user's cart |
| P1 | Main negatives and validations users will hit; key states (error/empty); main platform differences | Invalid coupon error; network failure on apply; empty cart |
| P2 | Boundaries, less common combinations, secondary UI states, analytics attributes | Coupon code at max length; coupon + membership combination; event attributes |
| P3 | Cosmetic, copy, rare edge cases | Long product name truncation; toast wording |

Smoke = all P0. Regression set = P0 + P1.

## Boundary value analysis (BVA)

For a range `min..max`, test `min-1`, `min`, `max`, `max+1` (add `min+1`/`max-1` only if the implementation is likely to have off-by-one logic). For lengths, test 0 (empty), 1, max, max+1. For money, include the exact threshold (`$9.99` vs `$10.00` min order).

Example: "Quantity 1–5" → 0 ✗, 1 ✓, 5 ✓, 6 ✗. One case with a data table, not four cases.

## Equivalence partitioning

Group inputs that the system should treat the same; test one representative per group plus boundaries.

Example coupon codes: valid active · valid expired · valid but not applicable to cart items · valid but below min cart value · already used (single-use) · non-existent · malformed (special chars) · empty · lowercase version of a valid code (is it case-insensitive? → finding if unspecified).

## State transition

List states and events; test every valid transition once and the important invalid ones.

| From \ Event | apply valid | apply invalid | remove | cart changes below min | checkout |
|---|---|---|---|---|---|
| No coupon | Applied | Error shown | — | — | Proceeds |
| Applied | Replaced? (finding) | Keeps current? (finding) | No coupon | Auto-removed + message? (finding) | Proceeds with discount |

Undefined cells are findings.

## Decision table

When several conditions combine to determine an outcome, enumerate combinations (or the meaningful subset) and the expected outcome. Missing outcomes are findings.

| Logged in | Member | Cart ≥ min | Coupon valid | Expected |
|---|---|---|---|---|
| N | — | — | — | Login prompt |
| Y | N | Y | Y | Discount applied |
| Y | Y | Y | Y | Member + coupon stack? (finding) |
| Y | — | N | Y | Min-value error |

## Pairwise

For many independent parameters (platform × payment method × user type × variant), cover every pair instead of every combination. Say in Notes which pairs a case covers. Use only when full combinations would explode and the parameters are believed independent.

## Error guessing (experience-based)

Add cases for typical defect spots: double submit, back after success, refresh mid-flow, rapid toggling, app background during API call, stale data after another device changes it, rounding of totals, leading/trailing spaces in inputs, very long text, RTL/emoji, timezone around midnight.

## Experiments / flags

- Case per variant where behaviour differs (prefix title with `[Variant A]`).
- Control unchanged (regression).
- Bucketing sticky across sessions/logins/devices (as specified).
- Flag off → old behaviour fully restored, no leftovers.
- Analytics carry the variant attribute.

## Analytics cases

One case per event (or group of related events): trigger action → event name, fires exactly once, attributes present with correct types/values, no PII, correct platform/workspace. Mark Automation = Yes when a network-interception approach is feasible.
