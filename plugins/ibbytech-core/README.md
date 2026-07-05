# ibbytech-core

Shared Claude Code framework for the five IbbyTech repos (biomesh, platform,
ibbytech-foundation, shogun, Trading-research). Distributed as a single
plugin from `ibbytech-marketplace` so all five consume the same baseline
instead of maintaining five drifting copies.

## Enforcement posture

Mixed, by design:

- **Hard-block (safety):** secret-guard, destructive-deny, persona-boundary,
  no-laptop-docker. These stop execution outright — no override, no
  workaround. Violations here are safety incidents, not process friction.
- **Soft-warn (process):** completion-condition-check, handoff-writer,
  verify-before-done, deploy-verify. These use `asyncRewake` to nudge and
  correct without halting the session. Violations here are hygiene issues.

Safety rules do not degrade to warnings under any circumstance. Process
rules do not escalate to hard blocks — they are advisory checks that keep
work legible across sessions and repos.

## Components (scaffolded — implemented in later build units)

| Component | Unit | Contents |
|---|---|---|
| Sub-agents | 3 | 4 agents: planner (Opus), implementer (Sonnet), reviewer-validator (Sonnet), docs (Haiku) |
| Hooks | 2 | 8 hooks total: 4 hard-block, 4 soft-warn (see `hooks/README.md`) |
| Commands | 4 | `/goal`, `/commit`, `/commit-push-pr`, `/handoff` |
| Skills | 4 | secret-hygiene, git-discipline, handoff-writer (folded from ibbytech-foundation) |
| MCP servers | 5 | `platform_retrieval.py`, `homelab_logs.py` (stdio, read-only where applicable) |

Only manifests and directory scaffolding exist as of this unit. No hook
logic, agent definitions, skill content, or MCP server code has been
written yet — each subdirectory's `README.md` states what belongs there.

## Consuming this plugin in a repo

1. Register the marketplace once per machine/repo:
   `/plugin marketplace add <path-or-url-to-ibbytech-foundation>`
2. Enable the plugin explicitly:
   `/plugin install ibbytech-core@ibbytech-marketplace`

Enabling is a reviewed, per-repo change — it is not auto-applied to a repo
just because the marketplace is registered. Each repo's maintainer decides
when to pick up `ibbytech-core`, and can pin or defer updates independently.

## Update propagation

All five repos consume `ibbytech-core` from this one source
(`C:\git\work\ibbytech-foundation\plugins\ibbytech-core`). A change made
here is the only place it needs to be made — no repo maintains a forked
copy of agents, hooks, commands, skills, or MCP config. This is the
mechanism that prevents the five repos from drifting apart on guardrails
and git discipline.
