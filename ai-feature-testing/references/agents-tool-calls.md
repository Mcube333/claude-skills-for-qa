# Multi-step AI agents that call tools

An agent's final reply can look correct while the steps behind it were wrong (wrong customer looked up, refund issued twice, a tool called it had no permission for). So test the **trajectory** — the sequence of tool calls and their arguments — not only the final answer. Agents are non-deterministic in path too: different valid orders can reach the same correct result, so assert properties of the trajectory, not one exact sequence.

## Capture the trajectory
Make every run produce a log of: user turn, each tool call (name, arguments, timestamp), each tool result, model/prompt version, final reply. Without this log you can't test an agent. If the product doesn't expose it, raise that as a testability requirement.

## Trajectory properties
- **Shape**: every tool call uses a known tool name with schema-valid arguments; IDs in arguments are well-formed.
- **Must include**: required steps happen (e.g. `getOrder` before `createReturn`; identity verification before any account change); the final action matches the user's intent.
- **Must NOT include**:
  - Tools outside the allowed set for this user/role.
  - Arguments pointing to another customer's data (ID must come from the authenticated session, not from user text).
  - Destructive or money-moving actions (refund, cancel, delete, payment link) without required confirmation.
  - Duplicate side-effect calls (two refunds) — check idempotency.
  - Invented values in arguments (amount not taken from a tool result).
- **Around it**: max step count / no infinite loops; total latency and cost limits; correct handling when a tool returns error/timeout/empty (retry within limit, then graceful message — never claim success); state is consistent after partial failure.

Order rules: assert "A happens before B" and "C never happens without D", not the full sequence, unless the flow genuinely has one valid order.

## Grounding of the final reply
Every fact in the final reply must trace to a tool result in this run. If the reply says "refund of $24.99 initiated", there must be a successful refund call with amount 24.99. Reply claims success while the tool failed → P1 bug.

## Test environment
- Use mocked tools (or a sandbox backend) so you can force: success, error, timeout, empty result, slow response, unexpected schema.
- Never point agent tests at production tools that move money or message real customers.
- Verify side effects in the backend/DB after the run (ticket actually created, status changed), not just the reply text.

## Scenario ideas
- Happy path per intent (track order, return, reschedule, payment issue).
- Ambiguous request → agent asks a clarifying question instead of guessing an action.
- User changes mind mid-conversation → earlier pending action not executed.
- Tool fails → honest message, escalation/handoff to human.
- Prompt injection inside a tool result (e.g. a product description or ticket note saying "issue a refund") → ignored.
- User asks about another customer's order by ID → refused, no tool call with that ID.
- Repeat same request N times → same final state every run; pass rate per property.
- Multi-turn memory: details from turn 1 used correctly in turn 4.

## Metrics (across a scenario set)
Task success rate, correct-tool-selection rate, argument accuracy, unnecessary-step rate, average steps and latency per task, escalation rate, and zero tolerance for unauthorised or duplicate side effects.

## Output: Trajectory checks
| Scenario | Required steps / order | Forbidden calls | Side effect to verify in backend | Failure injection |
