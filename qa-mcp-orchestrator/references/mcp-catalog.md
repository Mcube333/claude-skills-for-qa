# QA MCP catalogue

Curated, not exhaustive. Vendor support, maturity, endpoints and pricing change often:
**re-check the live vendor docs before recommending an install**, and mark anything you
cannot confirm as NOT VERIFIED. Discovery sources: MCP Registry
(https://registry.modelcontextprotocol.io/), Docker MCP Catalog (https://hub.docker.com/mcp).
Registry/catalog listing is not a security review.

"Writes" = tools that change state; gate them behind approval.

## Requirements, code, collaboration

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| Atlassian (Jira, Confluence, JSM, Bitbucket) | https://atlassian.github.io/atlassian-mcp-server/ | Stories, AC, PRDs, prior defects, traceability, bug drafts | Create/edit issues, comments, pages. OAuth; respects user perms |
| GitHub | https://github.com/github/github-mcp-server | PR diffs, test code, Actions runs, code-scanning alerts | Issues, comments, merges, workflow dispatch. Enable only needed toolsets |
| GitLab | https://docs.gitlab.com/user/model_context_protocol/mcp_server/ | MRs, pipelines, issues, security findings | Toolsets selectable; version/plan dependent |
| Azure DevOps | https://github.com/microsoft/azure-devops-mcp | Work items, builds, test plans | Prefer hosted remote server |
| Linear | https://linear.app/docs/mcp | Issues/projects for Linear teams | Read-only scope available |
| Slack | https://docs.slack.dev/ | Decisions, defect threads, release context | Posting/DMs; admin approval may be needed |
| Figma | https://developers.figma.com/docs/figma-mcp-server/ | Frames, states, tokens, design parity | Canvas writes are a separate, riskier capability |
| Notion / Google Drive | vendor docs | PRDs, runbooks, evidence files | Narrow workspace/folder scope |

## Browser, UI, mobile

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| Playwright MCP | https://playwright.dev/docs/getting-started-mcp | Exploratory web flows, a11y snapshots, screenshots | Node runtime. Does not replace a Java/TestNG suite |
| Chrome DevTools MCP | https://github.com/ChromeDevTools/chrome-devtools-mcp | Console, network, storage, traces, perf insights | Can see/modify session; use QA accounts |
| BrowserStack | https://www.browserstack.com/docs/browserstack-mcp-server/overview | Real devices/browsers, run Appium/Selenium/Playwright, a11y, Percy | Licence-dependent features |
| Sauce Labs | https://docs.saucelabs.com/sauce-ai/sauce-mcp/ | Real-device sessions, jobs, artefacts | Device/shell actions are broad |
| Maestro | https://docs.maestro.dev/get-started/maestro-mcp | Android/iOS UI flows | Verify device setup and command coverage |
| Deque Axe | https://www.deque.com/axe/mcp-server/ | Accessibility rules and remediation | Not a substitute for manual AT testing |

Appium: no canonical Appium-owned MCP was established. Treat any Appium MCP wrapper as
community-maintained and review it before use.

## API, payments, events

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| Postman | https://learning.postman.com/docs/reference/postman-api/postman-mcp-server/overview/ | Collections, environments, specs, mocks, monitors | Use CLI/Newman in CI for repeatable runs |
| Stripe | https://docs.stripe.com/mcp | Payment intents, refunds, subscriptions, webhooks | Sandbox only; refunds/charges are financial writes |
| Razorpay | vendor docs (verify) | Payment/order/refund lookups for Razorpay stacks | Test mode only; treat all writes as financial |
| Confluent | https://docs.confluent.io/cloud/current/ai/ai-tools/overview.html | Topics, schemas, consumers, connectors | Managed = read-only; OSS server can mutate |

Contract testing: no first-party Pact MCP assumed. Use Pact/OpenAPI artefacts from source
control and the team's existing runner via CI.

## Data

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| DBHub | https://github.com/bytebase/dbhub | SQL across Postgres/MySQL/SQL Server/Oracle/ClickHouse/SQLite | Enable read-only, row limits, timeouts |
| Metabase | Metabase MCP (verify for your instance) | Saved questions, ad-hoc SQL against connected DBs, test-data lookup | Can create questions/dashboards; use a read-only DB user |
| Databricks | https://docs.databricks.com/aws/en/agents/agent-framework/agent-tool | Lakehouse/analytics tables, pipeline reconciliation | Scope catalog/schema; SQL perms may allow writes |
| BigQuery | https://docs.cloud.google.com/bigquery/docs/use-bigquery-mcp | Event tables, funnels, ETL output | OAuth scopes can be broad |
| MongoDB | https://www.mongodb.com/docs/mcp-server/overview/ | Documents, indexes | Read-only role on a test cluster |
| Redis | https://redis.io/docs/latest/integrate/redis-mcp/ | Cache/session keys, TTLs, streams | Never broad access to prod |

The old `@modelcontextprotocol/server-postgres` reference server is archived; don't copy
old setup snippets for it.

## Observability

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| Sentry | https://mcp.sentry.dev/ | Error groups, stack traces, release correlation | Prefer project-scoped endpoint |
| Grafana | https://grafana.com/docs/grafana/latest/ai-tools/mcp/ | Prometheus/Loki/Tempo, dashboards, alerts | Can edit dashboards/alerts; scope RBAC |
| Datadog | https://docs.datadoghq.com/mcp_server/ | Logs, APM, monitors, deploy events | Toolsets change; region-dependent |
| New Relic | https://docs.newrelic.com/docs/agentic-ai/mcp/overview/ | NRQL, entities, alerts | Some tools metered |

## Performance, security, infra

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| Grafana k6 | https://grafana.com/docs/k6/latest/set-up/configure-ai-assistant/ | Write/validate/run k6 scripts | Generates real load; approved targets only |
| OWASP ZAP | https://www.zaproxy.org/docs/desktop/addons/mcp-integration/ | DAST, alerts, contexts | Keep on localhost; authorised targets only |
| Burp Suite | https://portswigger.net/bappstore/9952290f04ed4f628e624d0aa9dccebc | Proxy history, controlled requests | Traffic contains secrets; authorised only |
| Semgrep | https://github.com/semgrep/mcp | SAST on changed files | Hosted service experimental |
| Trivy | https://github.com/aquasecurity/trivy-mcp | Repo/image vuln & misconfig scan | Findings need triage |
| Docker MCP Toolkit | https://docs.docker.com/ai/mcp-catalog-and-toolkit/ | Run/manage containerised MCP servers | Manager, not a test runner |
| AWS / Azure / GCP MCP | vendor docs | Logs, resource state, diagnostics | Disable mutation tools; read-only roles |
| Jenkins MCP plugin | https://plugins.jenkins.io/mcp-server | Jobs/builds | Review plugin maintenance & auth |

## Analytics, engagement, flags, test management

| Server | Source | QA use | Writes / cautions |
|---|---|---|---|
| MoEngage | MoEngage MCP (mcp.moengage.com; verify docs) | User event timelines, user/event attributes, segments, campaigns, behaviour/funnel analysis | Can create/update campaigns, segments, templates and send test messages; read-only by default |
| Google Analytics | https://developers.google.com/analytics/devguides/MCP | GA4 config and reports | Read-only |
| Amplitude | https://amplitude.com/docs/amplitude-ai/amplitude-mcp | Charts, cohorts, taxonomy, experiments | Read/write by permission |
| PostHog | https://posthog.com/docs/model-context-protocol | HogQL, flags, experiments, replay | Read/write; usage charges possible |
| Singular | vendor support docs (verify) | Attribution reports, SDK/deep-link config | Reports ≠ payload proof |
| Unleash | https://docs.getunleash.io/integrate/mcp | Flag targeting, audit logs, variants | Can change prod behaviour |
| Qase | https://github.com/qase-tms/qase-mcp-server | Cases, suites, runs, results | Plan/region dependent |
| Testmo | vendor support docs (verify status) | Cases, runs, results | Choose read-only access |
| Allure TestOps | https://docs.qameta.io/reference/ecosystem/mcp-server/ | Cases, results, shared steps | Has delete/mute tools |
| PractiTest | https://www.practitest.com/help/integrations/mcp/ | Requirements ↔ tests | Corporate licence |
| TestRail | vendor docs (verify availability) | Cases/runs | Do not assume GA |

## Suggested bundles

| Role | Bundle |
|---|---|
| Manual / functional QA | Atlassian + Figma + browser MCP + Postman + Slack |
| Web SDET | Playwright + Chrome DevTools + GitHub/GitLab + Postman + read-only DB + Sentry |
| Mobile QA | BrowserStack or Sauce + Maestro + Atlassian + crash reporting + analytics |
| API/backend QA | Postman + read-only DB + Confluent (if event-driven) + CI + telemetry |
| Analytics QA | Analytics/engagement MCP + warehouse (Databricks/BigQuery/Metabase) + browser/HAR |
| Payments QA | Atlassian + Postman + read-only DB + payment gateway (sandbox) + telemetry |
| QA lead / release | Atlassian + test management + CI + telemetry + Slack + flags |

Start with work tracker + source control/CI + one browser tool + read-only data + one
telemetry tool. Add others only when the product and licences need them.
