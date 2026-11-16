# Hidden impact patterns

Use this list when tracing indirect impact. Each line: what changed -> what else to check.

## Shared UI and front end
- Design-system component (button, modal, price label, list item) -> every screen that uses it; check one per platform.
- Global CSS / theme / font -> layout of long text, RTL, dark mode, small screens.
- Navigation / routing -> deep links, back button, push-notification entry points, shared URLs.
- Form validation helper -> every form (sign-up, address, payment, contact).

## Money and orders
- Price, tax, discount, coupon, fee or rounding logic -> cart, checkout, order summary, invoice/email, refunds, admin views.
- Payment SDK or gateway config -> success, failure, cancellation, retry, refund and webhook callbacks.
- Order status or state machine -> order history, tracking, notifications, admin tools, analytics.

## Identity and session
- Auth, token or cookie change -> login, logout, session expiry, "remember me", OTP, social login, multi-device.
- User profile fields -> every screen and API that reads them; exports; analytics user attributes.

## Data
- Schema migration -> old records, null/default values, reports, admin search, rollback.
- Caching change -> stale data after updates, cache invalidation on price/stock changes.
- Search/index change -> filters, sorting, pagination, empty states.

## Platform and infrastructure
- Library / SDK / framework upgrade -> everything that library touches; also app startup and build size.
- Feature flag or remote config -> both flag states; users mid-session when it flips.
- A/B experiment setup -> every variant, bucketing, and analytics per variant.
- Environment config (URLs, keys, timeouts) -> integrations with third parties.

## Cross-cutting
- Analytics / tracking code -> event names, attributes, PII in payloads, duplicate fires.
- Notifications (email, SMS, push) -> content, links, timing, opt-out.
- Accessibility -> labels and focus order on changed screens.
- Localisation / copy -> truncation, plural forms, currency and date formats.
