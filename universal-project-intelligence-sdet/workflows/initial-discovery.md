# Workflow: initial project discovery

## Goal
Create a useful technical and SDET knowledge pack without changing the application.

## Procedure
1. Confirm workspace/repository root. If ambiguous, ask.
2. Read applicable agent instructions and project overview docs.
3. Inventory top-level structure and identify excluded/generated/vendor directories.
4. Identify manifests, lockfiles, entry points, modules, services, tests, configuration, CI/CD, infrastructure, schemas and migrations.
5. Create a staged analysis plan. For a monorepo, split by subsystem.
6. Analyse technology stack and architecture.
7. Trace critical interfaces, data flows and business workflows.
8. Assess security controls and operational/observability design at a static-evidence level.
9. Analyse testing architecture, testability and quality risks.
10. Cross-check and classify findings.
11. Check output path. If any target exists, do not overwrite; choose a new versioned directory or ask.
12. Generate documents using templates.
13. Validate internal links, file references, diagrams, secrets redaction and consistency.
14. Present summary, coverage, risks, unknowns and next steps.

## Default output
`docs/project-intelligence/`

Suggested files:
- `README.md`
- `PROJECT_OVERVIEW.md`
- `TECH_STACK.md`
- `REPOSITORY_MAP.md`
- `ARCHITECTURE.md`
- `COMPONENT_CATALOG.md`
- `API_AND_INTEGRATIONS.md`
- `DATA_ARCHITECTURE.md`
- `BUSINESS_FLOWS.md`
- `SECURITY_ASSESSMENT.md`
- `ENVIRONMENT_AND_CONFIGURATION.md`
- `CI_CD_AND_OBSERVABILITY.md`
- `QA_ASSESSMENT.md`
- `TEST_STRATEGY.md`
- `RISK_REGISTER.md`
- `COVERAGE_AND_GAPS.md`
- `OPEN_QUESTIONS.md`

## Completion response
State what was analysed, what was not analysed, output location, top risks, important unknowns, confidence limitations, and confirm that application files were not changed.
