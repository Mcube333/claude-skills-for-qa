# Evidence and confidence standard

## Labels
- **VERIFIED**: directly established by repository evidence or an explicitly observed tool result.
- **INFERRED**: a reasonable conclusion from evidence, but not explicitly declared or runtime-confirmed.
- **UNVERIFIED**: plausible or documented claim requiring runtime, environment, owner or external confirmation.
- **MISSING**: not found in the inspected scope, or required information is unavailable. State search scope.

## Evidence citation
Use repository-relative file paths, symbol names, and line ranges when available. Prefer precise references such as `src/orders/OrderService.java:42-81`. Do not fabricate line numbers. If the host cannot provide line numbers, cite path + symbol/section.

## Finding format
| Finding | Confidence | Evidence | QA/engineering impact | Follow-up validation |
|---|---|---|---|---|

## Rules
- Distinguish implementation from documentation and intended behaviour.
- Distinguish configured from active, declared from installed, and tested from testable.
- A test file is not proof a test passes.
- A mock is not proof a live integration works.
- A route declaration is not proof of production availability.
- A static security review is not a penetration test.
- A source configuration is not proof of deployed configuration.
- If sources conflict, report the conflict rather than silently choosing one.
