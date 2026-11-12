# Workflow: change impact and regression analysis

1. Identify changed files, symbols, configuration and public contracts from the supplied diff or approved repository comparison.
2. Map direct dependencies and downstream callers/consumers.
3. Map affected business workflows, APIs, data models, events and integrations.
4. Assess backward compatibility, data migration, feature flags and environment differences.
5. Identify test suites and scenarios to run, grouped by risk and test level.
6. Highlight likely automation updates and test data needs.
7. Report impact matrix: changed element, dependent component, business impact, risk, recommended validation, confidence.
8. Do not run tests, modify files or query external systems without approval.
