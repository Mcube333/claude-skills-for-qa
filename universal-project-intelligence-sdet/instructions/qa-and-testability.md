# QA architecture and testability

Inventory tests and tooling by level:
- unit, component, integration, contract, API, UI, mobile, end-to-end;
- performance, load, stress, soak, security, accessibility and compatibility where present.

Inspect test locations, naming, framework versions, fixtures, factories, mocks, stubs, assertions, reporting, coverage configuration, parallelism, retries, tagging, test selection, CI execution and environment dependencies.

Assess testability:
- separable business logic;
- stable and observable interfaces;
- dependency injection and replaceable external services;
- deterministic clocks/randomness;
- controllable state and test data;
- idempotent setup/cleanup;
- accessible UI semantics/stable locators;
- logs, correlation IDs and traceability;
- environment isolation;
- contract and failure simulation.

SDET recommendations must be risk-based and stack-aware. Consider positive, negative, boundary, equivalence, state-transition, concurrency, resilience, authorization, data-integrity, compatibility and recovery scenarios. Recommend automation only where repeatability, stability and value justify it.

Never infer coverage from number of test files. Report actual coverage only from a valid coverage artifact and state its scope/date. Never execute tests without approval if they may alter data, call external systems, incur cost or have other side effects.
