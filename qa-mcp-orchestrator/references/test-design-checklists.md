# Test-design checklists

Load only the sections the task needs. Always add positive, negative, boundary, state
transition, permission, retry/timeout, concurrency and recovery angles.

## Authentication
OTP/passwordless, wrong/expired OTP, resend limits, lockout, rate limits, session expiry and
refresh, logout everywhere, multi-device sessions, deep link while logged out, role-based
access, guest → logged-in transition (cart/identity carry-over).

## Commerce
Listing/search/filter/sort, PDP, out-of-stock, inventory race, cart add/update/remove,
quantity limits, address and serviceability, price/tax/discount/coupon stacking, deposits/
fees, checkout, order confirmation, cancellation, returns, order history consistency.

## Payments and subscriptions
Initiation, success, failure, pending, expiry, user abandon, retries, idempotency and
duplicate prevention, webhook delay/replay/out-of-order, reconciliation, refunds (full/
partial), autopay/mandate setup and failure, renewals, late fees/outstanding, invoices,
UI vs backend state consistency. Sandbox and test cards only.

## API / integrations
2xx/4xx/5xx, malformed/missing/extra fields, wrong types, auth failure/expired token,
timeouts, retries, idempotency keys, pagination, rate limits, partial outage of a
dependency, backward compatibility of versions.

## Web
Browser matrix, responsive breakpoints, mweb vs desktop, caching/stale assets, console
errors, failed requests, cookies/local/session storage, back/refresh/deep link mid-flow,
CORS/CSP where relevant.

## Mobile
Fresh install vs upgrade, OS versions, permissions granted/denied, background/foreground,
kill and relaunch, orientation, poor/offline network and handover, push and deep links
(cold/warm), notification permission, low storage, device-specific layout, app vs mweb
parity.

## Analytics and engagement
Event fires once, correct trigger point, names and attribute keys exact, types and enums,
no PII, identity before/after login, consent, UTM/click ids, deep-link/deferred deep-link
params, platform parity (web/Android/iOS), ingestion delay, duplicates, experiment/variant
attribute present.

## Feature flags / A/B
Control vs each variant, sticky assignment, targeting rules, excluded users, rollout %,
kill switch, flag service down → fallback, variant recorded in analytics, cleanup after
rollout.

## Data
Written once, correct state transitions, transaction rollback on failure, time zone and
currency precision, eventual consistency, stale cache, race conditions, audit trail.

## Accessibility
Focus order, keyboard traps, accessible names/labels, roles, contrast, zoom/text resize,
reduced motion, screen reader announcements for errors and dynamic content.

## Performance / reliability
Cold/warm start, p50/p95/p99 latency, throughput, concurrency, resource use, throttling,
queue backlog, graceful degradation, recovery after dependency outage.

## Security / privacy
Authorisation boundaries (IDOR), sensitive data masking in UI/logs/events, insecure
storage, session fixation/expiry, dependency and image vulnerabilities, safe test accounts.

## Release
Config/flag changes, DB migrations, backward compatibility with old app versions,
monitoring and alerts in place, rollback path, prod smoke evidence.
