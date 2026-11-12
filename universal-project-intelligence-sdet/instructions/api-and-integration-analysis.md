# API and integration analysis

Detect REST, GraphQL, SOAP, gRPC, WebSocket, RPC, messaging and event contracts as applicable.

For each discovered interface capture:
- name/route/operation/topic;
- method/protocol and version;
- source declaration and handler/resolver/consumer;
- authentication and authorization evidence;
- request inputs, validation and schema;
- response/output and error model;
- downstream dependencies;
- idempotency, pagination, rate limits, retries and timeouts if evidenced;
- relevant tests and test gaps.

Do not invent payloads, status codes or runtime behaviour. Mark undocumented contract details UNVERIFIED. For external integrations, record purpose, direction, protocol, configuration key names (not values), failure handling, mocks/stubs and sandbox/testability.
