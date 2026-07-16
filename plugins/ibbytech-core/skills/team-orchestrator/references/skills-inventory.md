# Skills Inventory — ibbytech-core Plugin + Project-Local Skills

## Shared Skills (this plugin — `ibbytech-core`)

| # | Skill | Path | Scope Boundary |
|---|-------|------|----------------|
| 1 | team-orchestrator | `skills/team-orchestrator/` | Task decomposition, agent coordination, skill routing, parallel execution management |
| 2 | git-discipline | `skills/git-discipline/` | Commit convention, two-commit discipline, branch promotion, changelog, release tagging, stale branch cleanup, PR quality |
| 3 | documentation | `skills/documentation/` | README rules, PR descriptions, changelog format, API docs, ADRs, evidence-to-docs flow |
| 4 | secret-hygiene | `skills/secret-hygiene/` | Secrets management, security scans, credential SOPs, pre-commit checks |

## Project-Local Skills (repo-specific — add rows here per project as they're built)

| # | Skill | Path | Scope Boundary |
|---|-------|------|----------------|
| — | *(repo-specific skills live in that repo's own `.claude/skills/`)* | | |

Examples of what typically belongs in this tier rather than the shared
plugin: a specific external API's field masks and pricing, a specific
project's UI/design system, a specific schema's migration and grant
patterns, a specific gateway's endpoint map. If a skill applies to every
repo regardless of domain, it belongs in the shared plugin, not here.

---

## Routing Quick Reference

| Task involves... | Primary skill |
|------------------|--------------|
| Git branch management, promotion, releases | git-discipline |
| Documentation updates, PR descriptions, changelogs | documentation |
| Security / credentials | secret-hygiene |
| Multi-agent coordination | team-orchestrator (routes to others) |
| Anything repo/domain-specific | check that repo's local skills inventory first |

---

## Scope Boundary Rules

1. **No overlap:** Each skill owns a distinct domain. If two skills seem
   to apply, pick the more specific one; use it as primary and the other
   as secondary context.
2. **Primary skill decides:** When skills disagree, the primary skill for
   that task takes precedence.
3. **Escalate ambiguity:** If a task doesn't clearly map to any skill,
   ask the human before proceeding. Don't guess.
4. **Skill ≠ Permission:** Having a skill loaded doesn't grant access to
   infrastructure. Rules and safety constraints still apply.
5. **New skills:** If a capability gap is identified that no skill covers,
   flag it. Don't improvise — propose a new skill rather than stretching
   an existing one to cover unrelated ground.
