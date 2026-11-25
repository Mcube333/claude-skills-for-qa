# qa-mcp-orchestrator

A Claude skill that routes QA tasks across connected MCP servers (Jira, GitHub, Figma,
browser tools, Postman, databases, telemetry, analytics, flags, test management), collects
evidence, and reports with honest statuses. Read-only by default; every write needs
approval.

## Structure
- `SKILL.md`: operating rules, intake, capability discovery, routing, workflows, evidence model
- `references/workflows.md`: 11 workflows + multi-tool examples
- `references/mcp-catalog.md`: curated QA MCP catalogue and role bundles
- `references/security-and-approvals.md`: approval matrix, redaction, injection, vetting
- `references/evidence-and-reporting.md`: statuses and templates
- `references/test-design-checklists.md`: domain checklists

## Example prompts
- "Analyse PROJ-123 and its Figma link. List missing AC and a risk-based test plan. Read-only."
- "Triage this staging checkout failure: correlate console/network, Sentry, and DB state."
- "Regression scope for this PR. Don't modify tests."
- "Check this test user's analytics events against the spec and flag any PII."
- "Prepare a release sign-off for build 4.12 with a go/no-go recommendation."
- "Which MCP servers should I connect for mobile QA? Don't install anything."

A skill does not install or authenticate MCP servers; it only tells Claude how to use the
ones you've connected.
