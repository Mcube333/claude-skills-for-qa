# Installation and portability

## Claude Code
Claude Code supports project-level and personal skills. For a project-local installation, copy this folder into:
`.claude/skills/universal-project-intelligence/`
Keep the folder name aligned with the skill name. Invoke it with `/universal-project-intelligence` where supported, or ask Claude Code to use the skill. Check current Claude Code documentation for any platform-specific frontmatter or discovery changes.

## Antigravity
Use the agent's supported skills/workflows/rules directory and preserve the package structure. If Antigravity does not auto-discover Claude-style `SKILL.md` frontmatter, add the content of `SKILL.md` as the agent's skill/rule entry point and retain the supporting folders as referenced resources. Verify skill discovery with the validation prompt below.

## Other compatible agents
1. Identify the host's documented skill/agent-instruction mechanism.
2. Install this directory as a skill/resource bundle.
3. Ensure the host can read referenced Markdown files.
4. Map its approval controls to the safety contract in `SKILL.md`.
5. If it supports only one instruction file, concatenate `SKILL.md` with the relevant modules or configure the entry point to load them on demand.
6. Do not assume all agents implement slash commands, frontmatter, or dynamic file loading identically.

## Recommended installation locations
- Project-scoped: `<repo>/.claude/skills/universal-project-intelligence/` for Claude Code, or the host's equivalent.
- Personal/global: the agent's documented user-level skills directory.
- Shared team use: commit the skill package into a dedicated internal tooling repository, then pin a reviewed version in each project.

## First-run prompt
"Use the Universal Project Intelligence skill. Run initial discovery for this repository in read-only mode. Do not execute project scripts, install dependencies, access external services, or modify application files. Generate the Markdown knowledge pack under docs/project-intelligence/. If that directory or any target file already exists, do not overwrite it; report the conflict and propose a safe versioned output path. Start with an inventory and staged analysis plan, then report evidence, confidence, exclusions and unknowns."

## Permission mapping
Configure the host agent to:
- allow repository file reading and bounded search;
- allow writing only to the approved documentation output path, if supported;
- require confirmation for shell/terminal commands where execution could have side effects;
- deny destructive commands and secret access where possible;
- require confirmation for network access, dependency installation, test execution, code edits, commits, pushes and deployments.

The skill text cannot override host-level permissions. Configure both.
