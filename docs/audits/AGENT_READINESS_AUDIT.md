# Agent Readiness Audit — ibbytech-foundation & brainnode-01

**Date:** 2026-07-15
**Auditor:** Claude Code agent session on ibbytech-laptop (control plane)
**Repo state audited:** `main` @ `4449986` — `feat(foundation): initial IbbyTech engineering foundation` (working tree clean at audit start)
**Remote:** `https://github.com/ibbygithub/ibbytech-foundation.git`
**Node audited:** brainnode-01 (192.168.71.222, Debian GNU/Linux 13 LXC, kernel 6.17.13-2-pve)
**Persona used for node access:** `devops-agent` via `~/.ssh/devops-agent_ed25519_clean` (identity verified: `hostname` → `brainnode-01`, `whoami` → `devops-agent`). No other credential used; no escalation.

---

## Scope and Method

- **Read-only audit.** No file in the repo was modified, created, or deleted except this deliverable. No remediation performed.
- Repo evidence gathered with directory listings, `git ls-files`, `git branch -a`, `git worktree list`, file reads, and case-insensitive content search.
- Node evidence gathered over SSH as `devops-agent` using Green Zone read-only diagnostics plus four vendor status commands the audit brief mandates: `claude --version`, `claude doctor`, `claude mcp list`, `codex login status`, and one authentication probe (`claude -p`, which returned a login error without executing any work).
- Secret material was never read or logged: credential files were checked for **existence only**; MCP config was inspected for **server names only**.

### Scoring legend

| Score | Meaning |
|:--|:--|
| **PASS** | Requirement fully satisfied, with verifiable evidence |
| **GAP** | Partially satisfied — mechanism exists but is incomplete, unenforced, or degraded |
| **FAIL** | Absent or non-functional |

---

## Domain 1 — Governance

| # | Item | Score | Evidence |
|:--|:-----|:------|:---------|
| 1.1 | `CLAUDE.md` exists at repo root | **FAIL** | Repo root contains only `.claude/`, `.git/`, `.gitignore`, `.worktrees/`, `outputs/`, `skills/`, `templates/` — no root `CLAUDE.md`. Project instructions live at `.claude/CLAUDE.md` (which Claude Code does load), so governance content is reachable by the agent, but the rubric location is empty and non-Claude tooling/humans browsing the repo root see no governance entry point. |
| 1.2 | Persona separation encoded | **PASS** | `.claude/rules/01-infrastructure.md` — "Persona Assignment Rules" and "SSH Identity Constraints": `devops-agent` → `devops-agent_ed25519_clean`, `dba-agent` → `dba-agent_ed25519`, per-node persona table, and `CREDENTIAL_ESCALATION` hard block for any other key. Reinforced per-node in the node role sections and in `05-database.md`. |
| 1.3 | Two-commit discipline encoded | **FAIL** | Case-insensitive search for `two[- ]commit` across the entire repo returns **zero matches**. The stated governance convention is not written down anywhere in the source-of-truth repo. Closest existing policy is `04-git-discipline.md` "Commit early and often within a feature branch" — a different (and arguably contradictory) rule. Unwritten conventions cannot be followed or audited. |
| 1.4 | Transport rules encoded | **PASS** | `.claude/rules/01-infrastructure.md` — "Transport Rules": "Code moves from laptop to nodes via **Git push/pull only**"; SCP/SFTP/rsync forbidden with `TRANSPORT_BYPASS` hard block. Duplicated in `02-safety.md` hard block types. |
| 1.5 | `.claude/settings.json` exists | **FAIL** | `.claude/` contains only `CLAUDE.md` and `rules/01–05` (glob of `.claude/**/*`; also confirmed by `git ls-files`). No `settings.json`, no `settings.local.json`. A baseline exists at `templates/settings-baseline.json` but has never been instantiated — **no declarative permission policy (and no hooks) is active in this repo**. Zone enforcement currently depends entirely on model compliance with prose rules. |
| 1.6 | Permission grants least-privilege | **GAP** (assessed on `templates/settings-baseline.json`, the only permission artifact present) | The baseline is broadly well-structured (per-persona, per-node, read-only SSH allowlists; Red Zone git/rm/docker deny rules; secret-file `cat` denies). Broader-than-needed grants are flagged below. All are **latent** until the template is instantiated. |

### 1.6 flags — grants broader than needed in `templates/settings-baseline.json`

1. **Platform-repo Yellow Zone auto-allow:** `Bash(cd C:/git/work/platform && git push*)` and `... git merge*` (lines 106–108) auto-approve operations that `04-git-discipline.md` classifies as Yellow Zone (human-confirm). Only `*git push * main*` / `* master*` are denied — pushes and merges to `develop` or any feature branch would proceed without the mandated confirmation.
2. **Secret-read deny covers only `cat`:** deny list blocks `cat ~/.ssh/*`, `cat .env*`, `cat *secret*`, etc. (lines 182–187), but the allow list also grants `head *`, `tail *`, `grep *`, `find *` — so `head .env`, `tail ~/.ssh/devops-agent_ed25519`, or `grep . .env` pass the permission layer. Blacklist-by-command-name does not close the read path.
3. **`Bash(echo *)` permits file writes:** the pattern matches `echo x > anyfile` (shell redirection is part of the matched command string). Redirect denies exist only for `ssh * > *`, not local commands.
4. **Arbitrary code execution auto-allowed in platform repo:** `... && python*` and `... && pip*` (lines 111–112) — `03-platform-standards.md` classifies package installs as Yellow Zone.
5. **DBA grant is superuser-wide with fragile guards:** `Bash(ssh ... dba-agent@192.168.71.221 sudo -u postgres psql *)` (line 49) grants superuser SQL, while the write-SQL denies (`* DROP *`, `* INSERT *`, …) are literal uppercase globs — lowercase `insert`/`drop` SQL bypasses them. `05-database.md` restricts the `postgres` superuser to infrastructure tasks only.
6. **Direct-to-main commit not blocked at permission layer:** `git checkout *` + `git commit *` are allowed unconditionally; only *pushes* to main/master are denied. `GIT_MAIN_DIRECT_WRITE` protection relies on model compliance alone.

---

## Domain 2 — Subagents

| # | Item | Score | Evidence |
|:--|:-----|:------|:---------|
| 2.1 | `.claude/agents/` enumeration; frontmatter (name, description, tools, model) valid | **FAIL** | The directory **does not exist**. Glob `.claude/agents/**` → no files; `.claude/**/*` shows only `CLAUDE.md` + `rules/`. There are zero subagent definitions to validate — frontmatter, tool grants, and escalation boundaries are all unverifiable by absence. |
| 2.2 | Tool grants least-privilege per subagent | **FAIL** | Not assessable — no subagents exist (see 2.1). |
| 2.3 | Explicit escalation boundary documented per subagent | **FAIL** | Not assessable — no subagents exist. (Escalation boundaries *do* exist at the rules level — hard blocks in `01-infrastructure.md`/`02-safety.md` — but nothing binds them to a subagent definition.) |
| 2.4 | Expected subagent: `coding` | **FAIL** | Missing — no `.claude/agents/coding.md` (directory absent). |
| 2.5 | Expected subagent: `github` | **FAIL** | Missing. |
| 2.6 | Expected subagent: `security-review` | **FAIL** | Missing. |
| 2.7 | Expected subagent: `logging` | **FAIL** | Missing. |

**Note:** `skills/ciso-security.md` and `skills/dbnode-01-skill.md` exist, but these are skills (instruction packs), not subagent definitions with scoped tool grants — they do not substitute for any of the four expected subagents. All 4 of 4 expected subagents are missing; the framework currently has **no execution layer**.

---

## Domain 3 — Toolchain on brainnode-01

All commands run as `devops-agent` (never escalated). Raw outputs in the Appendix.

| # | Item | Score | Evidence |
|:--|:-----|:------|:---------|
| 3.1 | SSH access as `devops-agent` | **PASS** | Key auth succeeded with `devops-agent_ed25519_clean`; `hostname` → `brainnode-01`, `whoami` → `devops-agent`, `uname -sr` → `Linux 6.17.13-2-pve`. |
| 3.2 | `claude --version` | **PASS** | `2.1.207 (Claude Code)` at `/usr/local/bin/claude` (npm-global install). |
| 3.3 | `claude doctor` | **GAP** | Doctor runs clean (exit 0; Search OK; install `npm-global (2.1.207)`, commit `bc512d563325`) but reports **1 warning**: "Can't auto-update: npm global folder isn't writable" — the install is root-owned, so the `devops-agent` runtime user cannot self-update. Remote Control section: "Not signed in to claude.ai". |
| 3.4 | Claude Code authentication state | **FAIL** | Not authenticated for `devops-agent`: `~/.claude/.credentials.json` **absent**, `~/.claude.json` **absent**, `ANTHROPIC_API_KEY` **not set**, doctor reports not signed in, and the functional probe `claude -p "Reply with exactly: AUTH_OK"` returned `Not logged in · Please run /login`. **Any agent run on this node fails at the first model call.** |
| 3.5 | `codex --version` | **PASS** | `codex-cli 0.125.0` at `/usr/local/bin/codex`. |
| 3.6 | Codex authentication state | **PASS** | `codex login status` → `Logged in using ChatGPT`; `~/.codex/auth.json` present (existence checked only, contents not read). |
| 3.7 | `node --version` | **PASS** | `v22.22.2` at `/usr/local/bin/node`. |
| 3.8 | `npm --version` | **PASS** | `10.9.7`. |
| 3.9 | Registered MCP servers (`claude mcp list`); note failures to start | **FAIL** | **User scope** (from `~`): `No MCP servers configured.` **Project scope**: the only checkout on the node (`/opt/git/work/agent-vault-system/`) defines exactly one server, `qmd` (`node .claude/scripts/qmd-mcp.mjs`), and `claude mcp list` from that directory reports `⏸ Pending approval (run \`claude\` to approve)`. No server failed to start because none is approved to start — **zero MCP servers are operational** for this persona, on the node whose documented role (`01-infrastructure.md`) includes "MCP servers". |

---

## Domain 4 — Documentation & audit trail

| # | Item | Score | Evidence |
|:--|:-----|:------|:---------|
| 4.1 | Runbook in `docs/` per existing subagent (scope, allowed tools, failure modes, log location) | **FAIL** | The repo has **no `docs/` directory at all** (root listing; `git ls-files` shows 14 tracked files, none under `docs/`). There are also zero existing subagents (Domain 2), so no runbook exists for any of them, and none of the four expected subagents (`coding`, `github`, `security-review`, `logging`) has documentation covering scope, tools, failure modes, or log location. Both layers of this requirement are absent. |
| 4.2 | Where agent actions are logged; persona attribution | **GAP** | **Designed but not operating.** Design: `02-safety.md` mandates a persistent evidence artifact for every infrastructure action at `outputs/validation/YYYY-MM-DD_<task>_report.md` ("Silent actions are forbidden"), and `templates/evidence-report-template.md` includes an explicit `**Persona(s):** [devops-agent / dba-agent / none]` field — persona attribution is designed in. Reality: **zero evidence records are committed anywhere in this repo** (`git ls-files` shows no `outputs/` entries; on disk `outputs/` contains only an empty `work-log/` directory). Attribution is manual self-report by the agent filling a template — with no `.claude/settings.json` there are no hooks, so nothing enforces or automates it. Service-level Loki logging (`03-platform-standards.md`) attributes by `service=` label, not persona, and covers services, not agent actions. |

---

## Prioritized Gap List

### P1 — blocks agent execution

| # | Gap | Evidence anchor |
|:--|:----|:----------------|
| P1-1 | **Claude Code is unauthenticated on brainnode-01 for `devops-agent`** — no claude.ai login, no `ANTHROPIC_API_KEY`, no credentials file. Every agent invocation dies at the first model call (`claude -p` → `Not logged in · Please run /login`). | Domain 3.4 |
| P1-2 | **No subagents exist.** `.claude/agents/` is absent; all four expected subagents (`coding`, `github`, `security-review`, `logging`) are missing. The multi-repo agent framework has no execution layer to be ready. | Domain 2 |
| P1-3 | **Zero operational MCP servers** for the persona on the designated MCP host: user scope empty; the single project-scoped server (`qmd`) is blocked at "Pending approval" and requires an interactive `claude` session — which itself is blocked by P1-1. | Domain 3.9 |

### P2 — blocks auditability

| # | Gap | Evidence anchor |
|:--|:----|:----------------|
| P2-1 | **`.claude/settings.json` missing** — no declarative permission boundary or hooks active; the baseline exists only as an uninstantiated template. SSH/git/PowerShell zone rules are enforced by nothing except model compliance, leaving no machine-checkable permission record. | Domain 1.5 |
| P2-2 | **Audit trail is empty and unenforced** — zero evidence records committed despite `02-safety.md` requiring one per infrastructure action; persona attribution exists only as a manual template field with no hook or automation writing/verifying it. | Domain 4.2 |
| P2-3 | **"Two-commit discipline" is not encoded anywhere** in the source-of-truth repo — a stated core governance convention that cannot be followed, verified, or audited as written. | Domain 1.3 |
| P2-4 | **No `develop` branch exists** (locally or on origin) even though `04-git-discipline.md` makes it the sole merge target for all agent work. Completed agent tasks have no compliant landing path (Path A of the worktree lifecycle cannot execute), which borders on P1 for task completion. Branches present: `main`, `feature/20260705-foundation-skills`, `feature/ibbytech-core-plugin`, `codex/20260429-codex-agent-foundation`. | `git branch -a` |

### P3 — hygiene

| # | Gap | Evidence anchor |
|:--|:----|:----------------|
| P3-1 | Root `CLAUDE.md` absent — governance is only discoverable via `.claude/CLAUDE.md` (fine for Claude Code, invisible at repo root for humans/other tools). | Domain 1.1 |
| P3-2 | `claude` on brainnode-01 is a root-owned npm-global install; auto-update is broken for the runtime user (doctor warning). Version currency depends on manual root intervention. | Domain 3.3 |
| P3-3 | **Worktree rot:** stray `.worktrees/hermes-rules/` directory at repo root — wrong location per `04-git-discipline.md` (worktrees belong under `.claude/worktrees/<branch-name>/`), matches no existing branch, and is not registered (`git worktree list` shows only the main checkout). | Root listing; `git worktree list` |
| P3-4 | **Branch-naming violations on existing branches:** `feature/ibbytech-core-plugin` (no `YYYYMMDD` date — a pattern `04-git-discipline.md` itself labels a hard block) and `codex/20260429-codex-agent-foundation` (prefix outside the `feature/`/`hotfix/` scheme). | `git branch -a` |
| P3-5 | Doc drift: `.claude/CLAUDE.md` advertises `skills/` as containing "CISO security, dbnode-01, advanced-planner" but `skills/` holds only `ciso-security.md` and `dbnode-01-skill.md`. | `skills/` listing |
| P3-6 | Baseline permission template breadth (latent until instantiated): the six flags in Domain 1.6 should be tightened **before** the template is promoted to a live `.claude/settings.json`, or instantiation will codify broader-than-needed grants. | Domain 1.6 |

---

## Appendix — Raw Evidence (sanitized; escape codes stripped)

### A1. Repo root listing (ls -la)

```
.claude/  .git/  .gitignore  .worktrees/  outputs/  skills/  templates/
(no CLAUDE.md, no docs/ at root)
```

### A2. Tracked files (`git ls-files`, 14 files)

```
.claude/CLAUDE.md
.claude/rules/01-infrastructure.md
.claude/rules/02-safety.md
.claude/rules/03-platform-standards.md
.claude/rules/04-git-discipline.md
.claude/rules/05-database.md
.gitignore
skills/ciso-security.md
skills/dbnode-01-skill.md
templates/evidence-report-template.md
templates/openapi-template.yaml
templates/project-claude-md-template.md
templates/service-doc-template.md
templates/settings-baseline.json
```

### A3. "two-commit" search

```
Grep pattern: two[- ]commit   (case-insensitive, whole repo)
Result: No matches found
```

### A4. outputs/ and worktree state

```
outputs/            → contains only outputs/work-log/ (empty; nothing tracked)
.worktrees/         → contains only .worktrees/hermes-rules/ (empty; unregistered)
git worktree list   → C:/git/work/ibbytech-foundation  4449986 [main]   (sole entry)
```

### A5. brainnode-01 identity and versions (SSH as devops-agent)

```
hostname  → brainnode-01
whoami    → devops-agent
uname -sr → Linux 6.17.13-2-pve        (Debian GNU/Linux 13, LXC)

node:  v22.22.2      /usr/local/bin/node
npm:   10.9.7        /usr/local/bin/npm
claude: 2.1.207 (Claude Code)   /usr/local/bin/claude
codex: codex-cli 0.125.0        /usr/local/bin/codex
```

### A6. `claude doctor` (key lines, exit 0)

```
Running: npm-global (2.1.207)
Commit: bc512d563325
Platform: linux-x64
Path: /usr/local/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe
Search: OK (bundled)
Auto-updates: enabled

Remote Control
- Not signed in to claude.ai
- claude.ai subscription auth not active

1 warning found
- Can't auto-update: npm global folder isn't writable
```

### A7. Claude Code authentication signals

```
~/.claude/.credentials.json : absent
~/.claude.json              : absent
ANTHROPIC_API_KEY           : not set
~/.claude/                  : present (3 entries)

Probe: claude -p "Reply with exactly: AUTH_OK"
Output: Not logged in · Please run /login
```

### A8. MCP servers

```
From ~ (user scope):
  No MCP servers configured. Use `claude mcp add` to add a server.

Project checkouts on node: /opt/git/work/agent-vault-system  (only entry)
.mcp.json server keys: qmd

From /opt/git/work/agent-vault-system (project scope):
  qmd: node .claude/scripts/qmd-mcp.mjs - ⏸ Pending approval (run `claude` to approve)
```

### A9. Codex authentication

```
codex login status → Logged in using ChatGPT   (exit 0)
~/.codex/auth.json → present (existence only; not read)
```

---

## Deliverable Note

This audit is committed as a single commit on `feature/20260715-agent-readiness-audit` rather than on `main`, because `04-git-discipline.md` classifies any direct write to `main` as a Red Zone operation (`GIT_MAIN_DIRECT_WRITE`). No other file in the repository was modified. Per `02-safety.md`, this document serves as the evidence artifact for the audit task (the audit brief restricted output to this single file, superseding the default `outputs/validation/` location for this task only).

**Audit persona usage:** repo work — none (laptop-local); brainnode-01 — `devops-agent` only.
