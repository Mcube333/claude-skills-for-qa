# Large repository and monorepo strategy

## Goals
Maintain useful coverage without exhausting context, reading every generated file, or pretending a partial scan is complete.

## Phase 1: cheap inventory
- Determine repository size and top-level layout using safe listing/search capabilities.
- Identify manifests, workspaces, solutions, build files, service descriptors and ownership files.
- Detect generated/vendor/build/cache/binary directories and exclude by default.
- Find nested agent instructions and read only those governing the target scope.

## Phase 2: subsystem map
Partition by independently buildable/deployable application, service, package, library, infrastructure unit or bounded context. Record dependencies between partitions. Do not assume directory boundaries equal service boundaries.

## Phase 3: prioritisation
Prioritise:
1. user-requested subsystem;
2. critical business journeys;
3. public interfaces and data boundaries;
4. security-sensitive components;
5. high-change or high-dependency modules;
6. shared libraries and platform infrastructure;
7. remaining low-risk areas.

## Phase 4: representative inspection
For each subsystem inspect manifests, entry points, configuration, public interfaces, core business logic, persistence/integration edges, tests and deployment definitions. Use targeted search and bounded reads. Expand only where evidence or risk requires it.

## Phase 5: coverage ledger
Maintain a table with subsystem, estimated/known scope, inspected files/areas, sampled areas, excluded areas, reason, confidence and next action. Do not claim exhaustive analysis unless it was actually exhaustive.

## Token/context management
- Summarise findings incrementally in working notes or approved documentation.
- Avoid repeatedly rereading unchanged files.
- Prefer symbol-level and line-range evidence.
- Do not ingest lockfiles or generated bundles wholesale; extract targeted metadata.
- If context is constrained, complete the requested high-priority slice and report deferred areas.

## Monorepo-specific checks
- workspace/package relationships;
- shared libraries and versioning;
- service ownership and dependency graph;
- per-service build/test/deploy workflows;
- cross-service contracts and compatibility;
- shared CI templates and policy;
- environment and secret boundaries.

## Output
Include a scope statement and coverage ledger in the final report. Label uninspected areas MISSING/NOT ANALYSED, not "no issue found."
