# Payload formats

`audit_events.py` finds events by walking any JSON structure: an object with an event-name key (`event`, `event_type`, `eventName`, `event_name`, `e`, `en`, `action`, or `name` when an attributes object sits next to it) is an event; its attributes come from the first of `properties`, `event_properties`, `params`, `attributes`, `attrs`, `eventAttributes`, `event_attributes`, `a`, `data` that is an object (else the remaining keys). User id, timestamp and platform come from common keys on the event, its attributes, or the enclosing batch envelope. Envelope scalar fields (app id, api key, project, workspace) and URL query/headers are kept as **context** for `--expect` checks.

| Source | Shape | Notes |
|---|---|---|
| Segment / RudderStack | `{batch:[{event, properties, userId, timestamp}]}` or single object | `traits` read as user properties for PII scan |
| Amplitude HTTP v2 | `{api_key, events:[{event_type, event_properties, user_properties, user_id, time}]}` | `api_key` available to `--expect` |
| Mixpanel | form body `data=<base64 JSON>` or JSON `[{event, properties:{distinct_id, time, ...}}]` | base64 decoded automatically |
| GA4 (gtag/Measurement Protocol) | `/g/collect?en=...&ep.key=...&epn.key=...`; batched lines in body | `ep.` → string attrs, `epn.` → numeric attrs, `tid` in context |
| MoEngage / CleverTap / WebEngage / others | Vendor-specific JSON batches | Usually picked up by the generic walk; if not, inspect one request body and pass `--name-key` / `--attr-key` |
| Tool CSV export | One row per event: name column + attribute columns, or a JSON `properties` column | Column names matched case-insensitively |
| NDJSON | One event JSON per line | |

HAR filtering: only requests whose URL contains a known analytics host are read (moengage, amplitude, mixpanel, segment, google-analytics, clevertap, webengage, firebase, braze, appsflyer, branch, rudderstack, posthog, heap, mparticle, netcore…). Add first-party collectors with `--hosts "events.mycompany.com"`.

Mobile apps: capture SDK traffic via a proxy (Charles/Proxyman/mitmproxy) and export as HAR, or use the vendor's debug/live view export. Some SDKs encrypt or compress payloads; if bodies aren't readable, use the tool's user-activity export instead.

Override flags:
- `--name-key evt` / `--attr-key payload`: custom field names (tried before the defaults).
- `--platform android`: keep only events whose platform field matches (events without a platform field are kept).
