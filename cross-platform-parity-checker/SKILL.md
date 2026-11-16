---
name: cross-platform-parity-checker
description: Compare the same screen, flow or component across platforms and against design - iOS vs Android vs mobile web vs desktop vs Figma vs PRD - and list every mismatch in text, numbers, formatting, rows, order, states, tooltips, colours, spacing and behaviour, with severity and a reference platform. Works from screenshots, screen recordings, Figma frames, PRD excerpts or written notes. Use this whenever the user shares screenshots of one screen from two or more platforms, says "compare iOS and Android", "check against Figma", "parity check", "why does web look different", "is this matching the design", or is doing UI QA on a revamped screen - even if they don't say "parity".
---

# Cross-Platform Parity Checker

Users switch devices, and support teams answer from one platform's screenshots. When the same screen
shows different numbers, labels or rows on different platforms, users lose trust and support gets
tickets. This skill finds those differences systematically so nothing is missed by eyeballing.

## Workflow

1. **Name the source of truth.** Ask (or infer from the user) which reference wins: Figma, PRD, or one
   platform (e.g. "Android is correct"). If none is given, use design > PRD > the platform the user calls
   correct, and say which you used. Without a reference, report differences as "differs" rather than "wrong".
2. **Read every input carefully.** For each screenshot, transcribe the visible content section by section,
   top to bottom: headings, labels, values, units, currency symbols, separators, badges, icons, buttons,
   empty/error states, and any text in status bars that shows OS or app version. Mark unreadable parts as
   unreadable instead of guessing.
3. **Align sections.** Match sections and rows across platforms by meaning, not position (a row may be
   in a different order on one platform). Note sections that exist on only one platform.
4. **Compare on every dimension** in `references/parity-checklist.md`: content, numbers and formatting,
   structure and order, states, interaction, visual design, accessibility.
5. **Classify each mismatch** with severity:
   - **Critical:** different amounts, totals or prices; missing legal or price-affecting row; different behaviour in money or data flows.
   - **Major:** missing or extra row/section, wrong label meaning, different state handling, broken interaction.
   - **Minor:** formatting (separators, decimals, case), copy wording, order of rows, tooltip text.
   - **Cosmetic:** colour, spacing, alignment, icon style, font weight.
6. **Group for filing.** Suggest how to group mismatches into tickets (per platform + section is usually right).

## Output format

```
## Parity check: <screen/flow> | Reference: <Figma frame / PRD section / platform>
Platforms compared: <iOS x.y build / Android x.y / Web / Figma>

Summary: <n mismatches: x critical, y major, z minor, w cosmetic. One line on the worst one.>

| # | Section | Element | Reference | iOS | Android | Web | Severity | Note |
(only rows with a difference; "=" where a platform matches the reference)

Present on one platform only:
- ...

Suggested tickets:
1. <platform> - <section>: items #..., severity ...

Could not verify (unreadable or not captured):
- ...
```

Keep it to differences. Do not list things that match, except in a final one-line count ("38 elements match").
If the user wants to file bugs, hand the grouped list to the bug-report-writer format when available.
