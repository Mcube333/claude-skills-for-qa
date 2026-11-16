---
name: production-issue-rca
description: Structured root-cause analysis for production or staging issues raised as support tickets, bug reports or incidents - payments not reflecting, wrong order or subscription state, missing data, failed jobs, wrong amounts, errors for some users only. Builds a timeline, forms ranked hypotheses, says exactly which data, logs, API calls and queries to check (read-only, privacy-safe), interprets the evidence the user brings back, and ends with root cause, customer resolution, permanent fix and a regression test. Keeps a reusable casebook of solved patterns. Use this whenever the user pastes a ticket or incident, a transaction/order/user ID with "why is this wrong", "analyse this ticket", "RCA this", "what is the resolution", "customer says X but system shows Y", or shares logs, HAR files, admin screenshots or query results about a live issue - even if they don't say "RCA".
---

# Production Issue RCA

Support tickets describe symptoms. The goal is to get from symptom to a cause backed by evidence,
fix the customer's problem, and stop it happening again - without guessing, and without touching
production data.

## Ground rules

- **Read-only.** Suggest only SELECT queries, GET requests and log searches. Any data correction is
  written as a proposal for the owning team to review, never as something to run.
- **Privacy.** Work with internal IDs (order, transaction, user ID). Do not ask for or repeat customer
  names, phones, emails, addresses or card data; mask them if they appear in pasted evidence.
- **Evidence over intuition.** Every conclusion cites the record, log line, response or timestamp that
  supports it. If the evidence is not there yet, say what to fetch instead of concluding.
- **One change at a time.** When the user brings results back, update the hypotheses before asking for more.

## Workflow

1. **Restate the ticket** in one or two lines: who (ID only), what they expected, what the system shows,
   since when, how many users affected if known.
2. **Classify the issue** (pick one, it decides where to look first):
   money/payment, state/status mismatch, missing or duplicate data, wrong calculation, access/auth,
   integration/third party, async job/queue/webhook, performance/timeouts, client display only.
3. **Build the timeline.** List the events that should have happened in order (user action -> API call ->
   payment gateway -> webhook -> DB update -> job -> notification), and mark which ones are confirmed,
   missing or unknown. The first missing or wrong step is usually where the cause is.
4. **Hypotheses.** Write 2-5 ranked hypotheses. For each: what would be true if it were the cause,
   and the single fastest check that confirms or kills it. Use `references/hypothesis-library.md`
   for common patterns by issue class.
5. **Checks to run.** Give the user concrete, read-only checks in priority order: admin screens to
   open, API calls, log queries, SQL. Write SQL generically (placeholders for table and column names)
   unless the user has shared the schema; never guess real table names as fact.
6. **Interpret evidence** as it comes back. Update each hypothesis to confirmed / ruled out / still open
   and say why. Stop when one hypothesis is confirmed by evidence from two independent sources
   (e.g. gateway says captured + DB has no matching record).
7. **Conclude** with the output below.
8. **Casebook.** Offer a short casebook entry (pattern, signals, checks, fix) the user can save in
   `references/casebook.md` so the next similar ticket is faster.

## Output format

```
## RCA: <ticket ID or short title>

Summary: <one line: cause and fix>

Timeline:
| Time | Event | Source | Status (ok / missing / wrong) |

Hypotheses:
| # | Hypothesis | Check | Result | Status |

Root cause: <what went wrong, where, and why - with evidence>
Customer resolution: <what to do for this customer now, who does it, any refund/credit/state correction as a proposal>
Permanent fix: <code/config/process change, owner team>
Blast radius: <other users or records likely affected and the read-only query to find them>
Regression test: <the test case (and automation idea) that would catch this next time>
Confidence: <High / Medium / Low> - <why>
Open questions: <anything still unknown>
```

For a quick ticket where the cause is obvious from the evidence, shorten this to Summary, Root cause,
Resolution and Regression test.

## Writing for the ticket

Support and developers read the same RCA. Keep the Summary and Customer resolution in plain words a
support agent can act on; keep technical detail in Root cause and Permanent fix.
