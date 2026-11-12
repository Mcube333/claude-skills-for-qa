# Universal Project Intelligence & SDET Engineering

A portable, evidence-driven skill for understanding unfamiliar software projects and supporting day-to-day SDET work.

## What it does
- Discovers project structure, languages, frameworks, services, dependencies and entry points.
- Documents architecture, APIs, data, workflows, integrations, security posture, environments, CI/CD and observability.
- Assesses existing testing architecture and testability.
- Generates a modular Markdown knowledge pack.
- Supports test design, defect investigation, regression/change-impact analysis and code review.
- Scales to monorepos and large repositories using staged analysis.

## Safety defaults
- Initial analysis is read-only.
- Generated Markdown goes only under `docs/project-intelligence/` by default.
- Existing files are never silently overwritten.
- No dependency installation, network call, test execution with side effects, code/config changes, migration or deployment without explicit approval.
- Secrets and sensitive data are redacted.

## Package layout
- `SKILL.md`: entry point and orchestration rules.
- `instructions/`: reusable analysis standards.
- `workflows/`: task-specific procedures.
- `templates/`: report templates.
- `adapters/`: compatibility guidance for agent platforms.
- `validation/`: acceptance checklist and test scenarios.

## Quick start
1. Place this folder in the supported skills directory for your agent (see `INSTALLATION.md`).
2. Open the target repository/workspace in the agent.
3. Invoke `universal-project-intelligence` or ask the agent to use this skill.
4. Request: "Run initial discovery in read-only mode. Generate the project intelligence documentation pack."
5. Review the scope, evidence, unknowns and generated documents.

## Important limitations
A skill is an instruction package, not a privileged repository scanner. Actual capabilities depend on the host agent's file access, context window, terminal permissions, MCP/tools and configured approval policies. Static source inspection cannot prove production behaviour, runtime configuration, live API responses, actual test coverage, or security absence. Use explicit validation steps where required.
