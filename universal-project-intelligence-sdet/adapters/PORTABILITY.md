# Agent portability notes

This package uses a common Markdown skill convention with YAML frontmatter. Host support varies.

## Required host capabilities
- repository file read/search;
- ability to load the entry point and referenced Markdown;
- controlled writing to an approved docs directory;
- user confirmation for actions with side effects.

## Claude Code
Use project-level `.claude/skills/` or documented personal skill location. Keep relative references intact.

## Antigravity
If native skill discovery differs, register `SKILL.md` as the agent rule/skill entry point and ensure supporting Markdown files are accessible as resources. Follow the installed Antigravity version's current documentation.

## Other agents
Map the package into their skill, rule, prompt, or workspace-instruction mechanism. Preserve approval semantics. If dynamic loading is unavailable, include the relevant supporting instructions in the active context.

## Portability caveat
No single folder format guarantees identical behaviour across every coding agent. Validate discovery, resource loading, tool permissions and approval enforcement on each host.
