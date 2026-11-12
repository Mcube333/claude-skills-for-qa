# Analysis method

## 1. Establish scope
Record repository root, workspace boundaries, branch/commit when available without running risky commands, requested scope, exclusions, and date. Do not assume the current directory is the repository root.

## 2. Inventory before deep reading
Prioritise:
- project/solution/workspace manifests and lockfiles;
- build and package manager files;
- application entry points;
- service/module descriptors;
- configuration examples (not secret values);
- routes/controllers/handlers;
- models/entities/schemas/migrations;
- tests and test configuration;
- CI/CD, containers, deployment and infrastructure definitions;
- architecture and product documentation.

Ignore or summarise generated, vendored, dependency-cache, binary, minified, build-output and coverage directories unless specifically relevant.

## 3. Analyse in layers
1. System context: purpose, actors, boundaries and external systems.
2. Containers/services: deployable units, runtime and ownership if discoverable.
3. Components: modules, packages, responsibilities and dependencies.
4. Code paths: representative critical workflows.
5. Contracts/data: APIs, schemas, persistence and events.
6. Quality: tests, observability, security controls and operational readiness.

## 4. Use targeted inspection
Search for entry points, route registration, dependency injection, configuration binding, persistence adapters, event publishers/consumers, authentication middleware, test fixtures and CI workflows. Read relevant bounded sections, not entire repositories by default.

## 5. Cross-check
For important conclusions seek at least two independent evidence points where practical (for example, route declaration + handler implementation; model + migration; test config + pipeline). If only one source exists, state that.

## 6. Report gaps
Use MISSING when not found in inspected scope; use UNVERIFIED when source evidence exists but runtime confirmation is required. Do not state "not present" if the relevant scope was not searched adequately.
