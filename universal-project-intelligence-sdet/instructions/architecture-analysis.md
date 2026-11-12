# Architecture analysis

Build a grounded architecture view:
- system context and trust boundaries;
- deployable applications, services, workers, jobs and libraries;
- runtime entry points and lifecycle;
- layers and responsibilities;
- dependency direction and coupling;
- synchronous and asynchronous communication;
- event/message flows;
- resilience patterns, retries, timeouts and circuit breakers where evidenced;
- state ownership and transaction boundaries;
- external systems and integration boundaries.

Prefer diagrams that can be traced to evidence. Mermaid diagrams are recommended. Label inferred edges as inferred. Do not create a generic layered diagram and present it as discovered architecture.

For each subsystem document: purpose, entry point, key components, dependencies, data owned, interfaces, tests, deployment unit, and known risks.
