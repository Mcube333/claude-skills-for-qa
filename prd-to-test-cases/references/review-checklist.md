# PRD & design review checklist

Go through each area. Anything undefined, conflicting, or open to two readings becomes a finding.

## Scope and users
- Which platforms (iOS, Android, mobile web, desktop web)? Which app versions / force-update?
- Which users: new vs existing, logged-in vs guest, user tiers/memberships, regions/cities, B2B vs B2C?
- Is it behind a feature flag or A/B experiment? Variants, split, bucketing rule (user/device/session), stickiness, what control looks like, kill switch behaviour.
- What happens to existing data/users on rollout (migration, carts in progress, saved state)?

## Inputs and limits
- Every input: allowed characters, min/max length, format, required/optional, trimming, case sensitivity, paste behaviour, emoji.
- Every number: min, max, step, decimals, currency, rounding rule (where and when), negative/zero.
- Quantities and counts: max items, max attempts, rate limits, cooldowns.
- Dates/times: timezone, cut-off times, date boundaries, expiry.

## States
For each screen/component: **loading, empty, partial, error, success, disabled**, and long-content/overflow. Is each designed? PRDs often describe success only.

- Network failure / timeout / retry. Offline (mobile).
- Session expiry mid-flow; login required mid-flow; return to the same place after login?
- Back/forward navigation, refresh, deep link into a middle step, app kill and relaunch.
- Double-tap / double-submit; concurrent edits from two devices/tabs.

## Business rules
- Combinations: does rule A apply together with rule B (coupon + offer + membership)? Precedence order?
- Eligibility conditions and what the ineligible user sees.
- Recalculations: what updates when an upstream value changes (quantity → price → tax → total → EMI)?
- Reversibility: undo, cancel, refund, edit after submit.

## Copy and messaging
- Exact error/success messages specified? Same message in PRD and design?
- Truncation, pluralization ("1 items"), currency and number formatting, localization.

## Design vs PRD
- Every PRD behaviour has a screen/state in the design, and vice versa (designs often contain behaviour the PRD never mentions).
- Labels, values, order of elements, CTA text, which CTA is primary, default selections.
- Components shown on one platform's design but not another's.
- Responsive breakpoints for web; small-screen and large-font behaviour on mobile.

## Analytics / tracking
- Events listed with name, trigger moment, attributes, attribute types.
- Fires once per action (not on re-render), deduped on back navigation?
- No PII in attributes (name, phone, email, address) unless explicitly approved.
- Naming consistent with existing events (casing, tense).

## Integrations and dependencies
- APIs: new vs changed endpoints, backward compatibility with older app versions.
- Third parties (payments, maps, SMS/OTP, KYC): failure, timeout, and sandbox behaviour.
- Notifications (push, SMS, email, WhatsApp): triggers, content, deep links, opt-out.

## Non-functional
- Performance expectations (load time, pagination size).
- Accessibility of new components (labels, focus, touch target size, contrast).
- Security: authorization (can user A see/modify user B's data via IDs?), data exposure in responses.

## Common contradiction patterns
- A limit stated twice with different values (e.g. "max 5" in one section, "up to 10" in another).
- A rule in the overview contradicted by an edge-case table later.
- PRD says a field is optional; design marks it required (or shows no skip option).
- PRD defines a message; design shows different copy.
- PRD flow order differs from the design prototype order.
- Acceptance criteria that conflict with the analytics spec (event fires on "tap" vs "success").
- Experiment variants described differently in PRD and in the experiment config/tracking spec.
