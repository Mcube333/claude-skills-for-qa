# Design rounds (L2-L4)

Run like a system design interview: the user drives, you play the interviewer. Ask clarifying questions back
when they ask you; add a constraint halfway through ("now it must run in 15 minutes", "now 3 platforms").

## How to structure an answer (share with the user if they struggle)
1. Clarify scope, users, platforms, release cadence, risks, constraints.
2. State the goals and how success is measured.
3. Propose the approach (layers, tools, environments, data, CI), with a simple diagram in words.
4. Discuss trade-offs and alternatives.
5. Cover failure modes: flakiness, data, environments, cost, ownership.
6. Rollout plan and metrics.

## Prompts by level

### L2
- Design an automation framework for a web app with UI and API tests, three environments, and CI on every PR.
- Test strategy for a new checkout page with coupons, multiple payment methods and an A/B experiment.
- Regression takes 3 days and blocks weekly releases. Fix it.

### L3
- Design test coverage for a microservices order system with async payments and webhooks.
- Our suite has 15% flaky tests and developers ignore failures. Plan to fix trust in 2 months.
- Add performance testing to CI for a public API with SLOs; what runs when?
- Mobile app on iOS and Android with weekly releases: device strategy, automation, release gates.

### L4
- Build a shared test platform for 12 product teams (grid/device farm, test data service, reporting, cost control).
- Define the quality strategy and team structure for a company moving from 1 to 6 squads.
- Leadership asks why we have QA at all if developers write tests. Make the case with metrics.
- Escaped defects doubled last quarter. Diagnose and present a plan to the CTO.

## What strong answers include
- Clear assumptions and scope; risk-based priorities; specific tools with reasons; data and environment strategy;
  ownership (who fixes what); metrics (flakiness rate, run time, escaped defects, cost); phased rollout.
