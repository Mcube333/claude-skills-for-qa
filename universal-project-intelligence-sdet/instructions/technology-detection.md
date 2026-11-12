# Technology and dependency detection

Identify technologies from manifests, lockfiles, source imports, build configuration, CI definitions, container files and deployment manifests. Do not rely on a single filename.

Capture:
- language(s), versions and runtime/toolchain constraints;
- framework(s), versions and their role;
- package/build managers and lockfile presence;
- major libraries and dependency versions;
- database, cache, queue, storage and search technologies;
- API protocols and schema tooling;
- test frameworks, assertion, mocking and reporting libraries;
- automation, performance and security tools;
- CI/CD, container, orchestration and cloud hints.

For each item include evidence path, version source, purpose, scope (whole repo/subsystem), and confidence. Distinguish direct dependencies from transitive dependencies. Do not label a version "installed" merely because it appears in a manifest. Flag conflicting version declarations and missing lockfiles as observations, not automatic defects.

Never install packages or query package registries unless explicitly approved.
