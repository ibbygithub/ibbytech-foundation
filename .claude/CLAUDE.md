# IbbyTech Foundation — Shared Engineering Standards

This directory is the single source of truth for Claude Code engineering rules,
skills, and templates across all IbbyTech projects.

## Usage

Add to any IbbyTech project session:
```
claude --add-dir ../ibbytech-foundation
```

All projects live at `C:\git\work\<project-name>\`. The `../ibbytech-foundation`
relative path resolves correctly from any project at this depth. Do not place
projects at a different directory depth without updating this path.

## Contents

- `.claude/rules/` — Rules 01–05 (infrastructure, safety, standards, git, database)
- `skills/` — ciso-security, dbnode-01
- `templates/` — service-doc, evidence-report, openapi skeleton, project CLAUDE.md,
  settings baseline

## How Projects Reference This Foundation

In any project's `.claude/CLAUDE.md`, include:

```markdown
## Foundation Reference
Engineering standards: ../ibbytech-foundation
Launch command: claude --add-dir ../ibbytech-foundation
```

---

## Agent Permission Boundaries

SSH, git push, and worktree operations are governed by the project's
`.claude/settings.json`. The baseline is in `templates/settings-baseline.json`.

---

## Two-Stage Task Plan Approval

Every task follows a two-stage approval process before any code, file, or
configuration is created or modified.

### Lightweight Task Exemption

Stage 2 is NOT required when ALL of the following are true:

- Scope is limited to `tools/dashboard/`, `outputs/`, or service docs
- No SSH access to any remote node (svcnode-01, dbnode-01, brainnode-01)
- No changes to `docker-compose.yml`, `.env`, Traefik config, or any
  infrastructure file
- No changes to `.claude/CLAUDE.md` or any `.claude/rules/` file
- Fully reversible — file edits or additions only, no database operations

For lightweight tasks, the agent states intent in one line before acting:
> "Lightweight task — proceeding: [plain English description of what and why]"

Evidence write at completion is still required. All other rules still apply.

For all other tasks, the full two-stage process is mandatory. No exceptions.

---

### Stage 1 — Technology Vetting (conditional)

Stage 1 is required if and only if the task involves introducing any software,
tool, package, library, or service not already present in the platform stack.

**Canonical platform stack** (no vetting required):
- Runtime: Python 3.x, Node.js
- Containers: Docker, Docker Compose
- Reverse proxy: Traefik v3
- Database: PostgreSQL (on dbnode-01)
- Logging: Loki
- Observability: Grafana
- Network: platform_net (Docker bridge)
- OS: Ubuntu (Linux nodes), Windows 11 (laptop)
- Transport: Git / GitHub

**If the task requires anything outside this list**, produce the Technology
Vetting notice (see `02-safety.md` for format) and wait for explicit approval
before proceeding to Stage 2.

---

### Stage 2 — Execution Plan Approval

After technology choices are approved (or if Stage 1 was not required),
produce the full execution plan and wait for "proceed" (or equivalent:
"go", "go ahead", "do it", "start", "yes") before writing a single line
of code, configuration, or documentation.

---

## Stage 3 — Delivery Gate (Green Gate Checklist)

Before any service task is considered complete, verify all applicable items:

| # | Item | How to Verify |
|:--|:-----|:--------------|
| 1 | **All validate steps PASS** | Run `python services/{name}/validate_{name}.py` |
| 2 | **Loki Level 1 verified** | Validate script Step 7 — live log lines in last 15 min |
| 3 | **OpenAPI spec committed** | `services/{name}/openapi.yaml` exists and tracked |
| 4 | **Capability registry current** | `.claude/services/{name}.md` Capabilities table current |
| 5 | **`_index.md` updated** | `.claude/services/_index.md` entry added or revised |
| 6 | **Evidence report written** | `outputs/validation/YYYY-MM-DD_{task}_report.md` committed |
| 7 | **`.env.example` current** | All new env vars documented in `.env.example` |

### Checklist Exemptions

- **Non-service tasks**: Items 1–5 and 7 do not apply. Item 6 always required.
- **Existing service — no functional change**: Item 1 is SKIP unless changed code warrants it.
- **Loki gap (known)**: Item 2 is WARN (documented), not FAIL.

---

## Session Autonomy Mode

### Activating Autonomy

Active when the human says: "approve all actions", "approve all commands",
"full autonomy", "just do it", or "go ahead with everything".

Scope-qualified: "approve all commands to get X working" — autonomy covers
only that task's scope.

### What Changes Under Autonomy

- Stage 2 execution plan: agent shows plan, proceeds immediately
- Yellow Zone git/SSH/PowerShell ops: agent narrates, proceeds immediately

### What Does NOT Change

- Red Zone operations — still blocked
- Hard block triggers — still stop immediately
- Scope discipline — autonomy covers stated task only
- Stage 1 technology vetting — still required for new technologies
- Evidence write — still required

### Deactivating Autonomy

"check with me", "pause", "hold", "stop and ask", "ask first"
Also auto-deactivates on hard block or scope expansion detection.
Does NOT persist across sessions.

---

## Scope Discipline During Execution

Once execution begins, operate within the approved plan boundary.

- Do not expand scope beyond what was approved in Stage 2
- If a discovery requires plan changes — stop, report, request amendment
- "While I'm here I'll also..." is a scope violation

---

## Communication Standards

- State what you are doing and why before doing it
- Flag risks and tradeoffs proactively
- Be direct about uncertainty — "I don't know" is acceptable; guessing is not
- Do not pad responses with disclaimers or excessive caveats
- When presenting options, recommend one and explain why

---

## Hard Block Reference

Git-related: `04-git-discipline.md`
Infrastructure: `01-infrastructure.md`
Safety: `02-safety.md`

When any hard block is triggered:
1. Stop immediately
2. Produce the hard block output (format per `02-safety.md`)
3. Write evidence to `outputs/validation/`
4. Wait for human instruction

---

## Token and Context Efficiency

Once the session brief is produced, operate from that loaded context.

- Do not re-read rule files mid-session unless a specific rule needs verification
- Do not re-scan the repo structure if already mapped
- Do not ask the human for information derivable from git or the filesystem
- If session context may be degraded, say so and offer to re-run /start-session
