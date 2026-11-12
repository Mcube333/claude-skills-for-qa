# Workflow: QA-oriented code review

Review the supplied diff or approved scope for:
- requirement and business-rule correctness;
- edge cases and validation;
- error handling and resilience;
- security and privacy;
- data integrity and transaction boundaries;
- API/contract compatibility;
- test adequacy and determinism;
- observability and diagnosability;
- performance and concurrency;
- maintainability and regression risk.

Report findings by severity with file/line evidence, impact, reproduction/validation idea and suggested direction. Avoid style-only noise unless it affects maintainability. Do not modify code during review.
