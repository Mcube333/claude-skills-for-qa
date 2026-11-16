---
name: bug-report-writer
description: Turn rough QA notes, screenshots, screen recordings, defect-sheet rows, chat messages or test failures into clear, ready-to-file bug reports for Jira, Linear, Azure DevOps or GitHub Issues - with a precise title, environment, preconditions, numbered steps, expected vs actual, severity and priority with reasons, evidence and labels. Groups related UI/UX findings into one ticket, splits unrelated issues, and flags likely duplicates. Use this whenever the user pastes observations and says "file a bug", "log this", "raise a ticket", "write a defect", "make Jira tickets from this sheet", shares a screenshot of something broken, or lists QA findings after a test run - even if they don't say "bug report".
---

# Bug Report Writer

A bug report is a message to a developer who was not there when it happened. Its job is to let them
reproduce the problem on the first try and to let a lead decide its priority in ten seconds. Everything
in this skill serves those two goals.

## Workflow

1. **Collect what you were given.** Notes, screenshots, recordings, logs, a sheet row, a failing test.
   Look at every screenshot carefully: read the visible text, values, error messages, URL bars, device
   status bars (OS, time) and app version if shown. These are facts you can use; do not invent others.
2. **Separate the issues.** One ticket = one root problem a developer can fix and close.
   - Group findings that share a root cause or one component and will be fixed together
     (e.g. five formatting problems in the same price breakdown section → one ticket with a checklist).
   - Split findings that live in different components, need different owners, or have different severity.
   - Say which grouping you chose and why in one line, so the user can override it.
3. **Check for duplicates.** If the user shared existing tickets, a sheet of logged defects, or earlier
   reports in the conversation, compare titles and symptoms. Flag "possible duplicate of X" instead of
   writing a new ticket when the symptom and area match.
4. **Write each report** using the template below.
5. **List what is missing.** If something a developer needs is unknown (build number, account type,
   exact device, whether it reproduces every time), do not guess. Put it under "Open questions" at the
   end so the user can fill it in before filing.

## Report template

Use this structure for every ticket. Keep the field names; leave a field out only if it truly does not apply.

```
Title: [Area/Screen] <what is wrong> when <trigger/condition>

Environment: <env (staging/prod/UAT)> | <platform + OS version> | <device or browser + version> | <app build/version> | <account/user type>
Preconditions: <state needed before step 1: logged-in user type, cart contents, feature flag, experiment variant, test data>

Steps to reproduce:
1. ...
2. ...
3. ...

Expected result: <what should happen, citing the source of truth: PRD section, design, API contract, other platform>
Actual result: <what happens, with exact text, values, error codes>

Reproducibility: <Always | Intermittent (x of y tries) | Once>
Severity: <Critical | Major | Minor | Trivial> - <one-line reason>
Priority: <P1 | P2 | P3 | P4> - <one-line reason>
Evidence: <screenshot/recording/log names, request IDs, timestamps>
Labels/Components: <platform, feature area, regression?, experiment?>
Notes: <impact on users or revenue, workaround if any, related tickets>
```

### Writing rules (and why)

- **Title** names the place, the symptom and the trigger. A lead scanning a board should know what is
  broken without opening it. Bad: "Price issue". Good: "[Cart - Cost breakup] Deposit row missing when
  cart has mixed rental tenures".
- **Steps** start from a clean, named state and use exact UI labels in quotes. One action per step.
  If the bug needs specific data (a product ID, a coupon, a test account), put it in Preconditions or
  the step itself. Never write "do the usual flow".
- **Expected** must cite where the expectation comes from (PRD, Figma, API spec, the other platform's
  behaviour, previous release). This prevents "works as designed" ping-pong.
- **Actual** quotes exact on-screen text, values and error codes. Copy them from screenshots.
- **Severity vs priority.** Severity = how bad the impact is technically. Priority = how soon it must be
  fixed for the business. They can differ (a typo on the payment button: trivial severity, high priority).
  Use the scale in `references/severity-guide.md` and always give the reason.
- **Grouped tickets** list each sub-issue as a checklist item with its own expected/actual, so the
  developer can tick them off and the tester can verify each one.
- **No blame, no speculation as fact.** If you suspect a cause (e.g. a missing field in the API
  response), put it under Notes as "Possible cause: ..." with the evidence.
- **Privacy.** Never copy real customer names, phone numbers, emails, addresses, card numbers or
  tokens into a ticket. Replace them with placeholders like `<customer phone>` and keep the IDs a
  developer needs (order ID, request ID) only if they are internal identifiers.

## Output

1. One line on how many tickets and how you grouped them.
2. Each ticket in a fenced block in the template above, ready to paste.
3. "Open questions" list (only if anything is missing).
4. If the user asked for a sheet or a bulk import, also offer a CSV with columns:
   Summary, Description, Issue Type, Priority, Labels, Components, Environment.

For examples of good and bad reports, read `references/examples.md` when you are unsure how much detail to include.
