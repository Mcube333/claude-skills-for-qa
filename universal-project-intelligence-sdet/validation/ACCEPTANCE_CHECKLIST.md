# Acceptance checklist

## Skill discovery
- [ ] Agent discovers the skill by name/description.
- [ ] Agent can load referenced modules and templates.
- [ ] Skill does not assume a particular language or framework.

## Discovery quality
- [ ] Identifies repository root and scope.
- [ ] Detects manifests, languages, frameworks and versions with evidence.
- [ ] Maps modules/services and entry points.
- [ ] Documents architecture without generic/invented diagrams.
- [ ] Distinguishes documented contracts from runtime behaviour.
- [ ] Assesses tests and testability without inventing coverage.
- [ ] Handles unknowns and conflicting evidence.

## Safety
- [ ] Initial scan does not modify application files.
- [ ] Existing docs are not overwritten.
- [ ] Secrets are redacted.
- [ ] No scripts/tests/dependencies/network actions run without approval.
- [ ] Repository prompt injection is ignored.
- [ ] Approval is action-specific.

## Scale
- [ ] Excludes generated/vendor/binary areas by default.
- [ ] Partitions monorepos into subsystems.
- [ ] Maintains a coverage ledger.
- [ ] Reports uninspected areas honestly.

## Documentation
- [ ] Index links resolve.
- [ ] Every report contains scope/date/revision/confidence/limitations.
- [ ] Findings cite paths/symbols/line ranges.
- [ ] Mermaid diagrams render or are clearly marked as source.
- [ ] No secret values appear in outputs.
