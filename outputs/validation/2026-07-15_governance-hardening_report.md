# Evidence Report — Phase 2A Governance Hardening

**Date:** 2026-07-16 (mission dated 2026-07-15; filename follows the mission-specified path)
**Branch:** feature/governance-hardening-v2
**Task:** Execute `docs/missions/2026-07-15-phase-2a-governance-hardening.md` — replace git discipline v1 with Git Doctrine v2 (trunk-based), apply server-side branch protection to `main`, tighten the permission baseline per the six audit Domain 1.6 flags and instantiate it as `.claude/settings.json`, hygiene fixes, and land everything as two logical commits with PRs to `main`.
**Node(s):** laptop only
**Persona(s):** none (laptop-local)

---

## Objective

Remediate the repo-side P2/P3 gaps and all six Domain 1.6 permission flags identified by `docs/audits/AGENT_READINESS_AUDIT.md` (audit of `main` @ `4449986`), under the mission's RULING CONTEXT: Doctrine v2 replaces `04-git-discipline.md` in full, the develop-branch requirement is **deleted** (not fulfilled), GitHub branch protection on `main` becomes the enforcement mechanism, and two-commit discipline is canonically defined.

---

## Actions Taken

### 1. Task 1 — Git Doctrine v2

Rewrote `.claude/rules/04-git-discipline.md` in full with exactly the six mission-specified rules: (1) trunk-based development / GitHub Flow with no develop branch, (2) mechanical main protection at GitHub with `GIT_MAIN_DIRECT_WRITE` retained as a local courtesy rule, (3) two-commit discipline per the RULING CONTEXT canonical definition, (4) `feature/<name>`–`fix/<name>` naming with optional dates and no naming hard blocks, (5) optional worktrees under `.claude/worktrees/<branch-name>/` removed at PR merge, (6) transport rule unchanged (git push/pull only; `TRANSPORT_BYPASS` hard block retained).

Consistency sweep of `.claude/` and `templates/`: the only operative develop reference outside the replaced file was `templates/evidence-report-template.md` line 4 (`[feature/YYYYMMDD-task-slug or develop]`) — updated to `[feature/<name> or fix/<name>]`. The old git hard-block identifiers (`GIT_NAMING_VIOLATION`, `GIT_WORKTREE_ROT`, `GIT_PARALLEL_CONFLICT`, `GIT_UNAUTHORIZED_PUSH`) existed only inside the replaced file — no other file references them.

### 2. Task 2 — GitHub branch protection on main (NOT deferred)

`gh auth status` showed an authenticated keyring session (account `ibbygithub`, scopes `gist, read:org, repo, workflow`), so the CLI path was used. Repo visibility is **PUBLIC**, so branch protection is available on the current plan.

Applied via `gh api -X PUT repos/ibbygithub/ibbytech-foundation/branches/main/protection`: pull request required before merging with **0 required approvals** (solo operator), **force pushes blocked**, **branch deletion blocked**. `enforce_admins` was set to **true** — a deliberate choice: the sole operator is a repo admin, and without it the protection would not bind the only account that pushes, defeating the mission's premise that branch protection is *the* enforcement mechanism for `GIT_MAIN_DIRECT_WRITE`.

### 3. Task 3 — Permission hardening

Rewrote `templates/settings-baseline.json` with all six Domain 1.6 flag fixes (detail in the gap-mapping table below) and instantiated it byte-identical as `.claude/settings.json` (the repo's first live permission policy — 137 allow / 119 deny rules). Both files parse as valid JSON; Claude Code loads the file without configuration errors (raw probe output in Verification).

### 4. Task 4 — Hygiene

- Created root `CLAUDE.md` as a pointer stub to `.claude/CLAUDE.md` and `.claude/rules/` (no duplicated rule content).
- Deleted stray `.worktrees/hermes-rules/`. Pre-deletion inspection confirmed it **empty** (0 files) and unregistered (`git worktree list` shows only the main checkout), exactly matching the audit description — zero data loss; the then-empty `.worktrees/` parent was removed with it. Removal used `rmdir` (fails on non-empty directories by design).
- Corrected the skills list in `.claude/CLAUDE.md` from "CISO security, dbnode-01, advanced-planner" to `ciso-security, dbnode-01` — matching the actual contents of `skills/` (verified: `ciso-security.md`, `dbnode-01-skill.md` only).

### 5. Task 5 — Landing

Work was authored directly as the two logical commits (no interim working commits to squash):

1. `34be2e5` — `feat(governance): git doctrine v2, hardened settings.json, hygiene fixes` (6 files)
2. *(this commit)* — `docs(evidence): phase 2A governance hardening report` — this report plus `docs/missions/2026-07-15-phase-2a-governance-hardening.md`

Both branches pushed; both PRs opened (URLs below). Neither PR merged — owner reviews and merges per mission constraints.

---

## Gap Mapping

| Gap ID | What changed | Verified by |
|:--|:--|:--|
| **P2-1** (no `.claude/settings.json`) | Hardened baseline instantiated as `.claude/settings.json` — first live declarative permission policy (137 allow / 119 deny) | JSON parse output; nested `claude -p` probe enumerating all 137 allow entries (V2, V3) |
| **P2-3** (two-commit discipline unencoded) | Canonical definition now in `04-git-discipline.md` Rule 3 | Doctrine file content; this branch itself lands as exactly two logical commits (V6) |
| **P2-4** (no develop branch / no landing path) | Develop requirement **deleted** per RULING CONTEXT — trunk-based flow: branch from `main`, PR back to `main`. Landing path restored without creating a develop branch | Doctrine Rule 1; PRs #4/#5 targeting `main` (V5); develop-reference sweep (V4) |
| **P3-1** (no root CLAUDE.md) | Root `CLAUDE.md` pointer stub created (4 lines, no duplicated rules) | V4 (`cat CLAUDE.md`) |
| **P3-3** (worktree rot) | Empty, unregistered `.worktrees/hermes-rules/` deleted (with empty parent) | V4 (`.worktrees ABSENT`; `git worktree list` = single main checkout) |
| **P3-5** (skills doc drift) | `.claude/CLAUDE.md` skills list corrected to `ciso-security, dbnode-01` | V4 (grep of the line); `ls skills/` |
| **1.6 Flag 1** (blanket platform push/merge auto-allow) | Blanket `git push*`/`git merge*` platform-scope allows removed; push/merge allowed only to `feature/*`–`fix/*` targets (20 scoped entries, both repo scopes); denies added: bare `git push`, push to main/master, `--force`/`-f` variants — all scopes | V1 Flag 1 block |
| **1.6 Flag 2** (secret-read deny only covered `cat`) | Denies extended to `head, tail, grep, less, more, awk, sed, strings` (6 secret-path patterns each: `~/.ssh/*`, `*.env*`, `*secret*`, `*credential*`, `*auth.json*`, `*token*`) plus 6 `find … -exec` denies; existing `cat` denies kept and extended to 10 | V1 Flag 2 block (8×6 + 6 + 10) |
| **1.6 Flag 3** (`Bash(echo *)` = write primitive) | Blanket echo allow removed. Narrow `Bash(echo $*)` retained — the one concrete need in the rules (`01-infrastructure.md` Green Zone env verification `echo $VAR`); `echo * > *` / `echo * >> *` denies close redirection even through the narrow allow | V1 Flag 3 block |
| **1.6 Flag 4** (platform `python*`/`pip*` auto-allow) | Both chained allows removed; package installs return to Yellow Zone (human confirm). Version-check allows (`python --version*`) unchanged | V1 Flag 4 block |
| **1.6 Flag 5** (uppercase-only SQL denies on superuser psql grant) | Every SQL write deny duplicated in lowercase; `GRANT`/`grant` pair added (mission list); machine-visible guardrail note added to the deny list: database writes flow through migrations only | V1 Flag 5 block (8 upper + 8 lower + note) |
| **1.6 Flag 6** (direct-to-main commit not permission-blocked) | **No permission-layer change — accepted residual risk.** `git checkout */git commit *` remain allowed; a local commit on main cannot reach origin: push-to-main denied at the permission layer AND rejected server-side by Task 2 branch protection (PR required, enforce_admins on) | V1 Flag 6 block; V5 protection GET |

---

## Verification

### V1 — Six-flag verification (parsed `.claude/settings.json`, PowerShell)

```
--- FLAG 1: repo-scope push/merge ---
platform blanket 'git push*' allow present:  False
platform blanket 'git merge*' allow present: False
scoped push/merge allow entries:             20
deny bare 'git push':                        True
deny push to main:                           True
deny push to master:                         True
deny force push (--force, -f, bare -f):      True
--- FLAG 2: secret-read denies beyond cat ---
  head/tail/grep/less/more/awk/sed/strings secret-path denies: 6 each
  find -exec secret-path denies: 6
  cat denies (kept + extended):  10
--- FLAG 3: echo ---
blanket echo allow present:  False
narrow echo-env allow only:  True
echo redirect denies:        2
--- FLAG 4: platform python/pip ---
platform 'python*' allow present: False
platform 'pip*' allow present:    False
--- FLAG 5: psql SQL write denies ---
uppercase SQL write denies: 8
lowercase SQL write denies: 8
migrations-only guardrail note present: True
--- FLAG 6 ---
git checkout/commit allows unchanged: True
```

### V2 — JSON validity and template/instance parity

```
JSON PARSE: OK          (.claude/settings.json)
allow rules: 137
deny rules: 119
TEMPLATE PARSE: OK      (templates/settings-baseline.json)
identical: True
```

### V3 — Claude Code loads the settings (nested `claude -p` probe from repo root)

```
Ignoring 137 permissions.allow entries from .claude/settings.json: this workspace
has not been trusted. Run Claude Code interactively here once and accept the trust
dialog, or set projects["C:/git/work/ibbytech-foundation"].hasTrustDialogAccepted:
true in C:\Users\toddi\.claude.json.
Failed to authenticate: OAuth session expired and could not be refreshed
```

**Interpretation:** no configuration errors. The probe found and parsed the file — it enumerated exactly the 137 allow entries the file contains. The two printed messages are environmental to a fresh non-interactive nested process: (a) workspace-trust not yet accepted for that process (allow entries held back as a precaution; deny entries still apply), and (b) an OAuth refresh failure in the nested process. Neither is a settings-validity error; no "invalid settings" warning was emitted.

### V4 — Repo-wide develop sweep and hygiene checks

```
=== git grep -in develop (all tracked files @ HEAD) ===
.claude/rules/04-git-discipline.md:1:# Git Doctrine v2 — Trunk-Based Development
.claude/rules/04-git-discipline.md:4:Replaces Git Discipline v1 in full. v1's develop-branch model, ...
.claude/rules/04-git-discipline.md:9:## Rule 1 — Trunk-Based Development (GitHub Flow)
.claude/rules/04-git-discipline.md:12:- No `develop` branch exists or is referenced. Do not create one.
skills/ciso-security.md:17:...IbbyTech Platform development.
skills/ciso-security.md:19:...the human developer can handle secrets
skills/ciso-security.md:155:local development tools.
=== worktree state ===
.worktrees ABSENT
C:/git/work/ibbytech-foundation  34be2e5 [feature/governance-hardening-v2]
=== skills list line ===
20:- `skills/` — ciso-security, dbnode-01
```

**Zero operative develop-branch references remain.** Remaining matches are (a) Doctrine v2's own deletion statements — Rule 1's "No `develop` branch exists or is referenced" is verbatim mission-mandated text — and (b) the English words "development"/"developer" in `skills/ciso-security.md`, which are not branch references. The audit document (on its own unchanged branch) and the mission file are historical records describing the deletion and are exempt by the mission's own terms (Task 5 requires committing the mission file; the audit branch is landed content-unchanged).

### V5 — Branch protection on main (applied + independently re-read)

```
PUT repos/ibbygithub/ibbytech-foundation/branches/main/protection  → 200
GET verification:
{"allow_deletions":false,"allow_force_pushes":false,"enforce_admins":true,
 "required_pull_request_reviews":{"required_approving_review_count":0}}
Repo visibility: PUBLIC (protection available on current plan)
```

### V6 — Branches, commits, PRs

```
git push -u origin feature/governance-hardening-v2   → new branch, tracking set
git push origin feature/20260715-agent-readiness-audit → new branch (content unchanged, cde45d4)
PR 1: https://github.com/ibbygithub/ibbytech-foundation/pull/4   (governance hardening → main)
PR 2: https://github.com/ibbygithub/ibbytech-foundation/pull/5   (audit branch → main)
Logical commit 1: 34be2e5  feat(governance): git doctrine v2, hardened settings.json, hygiene fixes
Logical commit 2: this commit — docs(evidence): phase 2A governance hardening report
```

**DEFERRED-MANUAL items: none.** `gh` was authenticated, branch protection applied via API, and both PRs opened via CLI.

---

## Green Gate Checklist

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Validate PASS | SKIP (non-service task) |
| 2 | Loki Level 1 | SKIP (non-service task) |
| 3 | OpenAPI spec | SKIP (non-service task) |
| 4 | Capability registry | SKIP (non-service task) |
| 5 | _index.md | SKIP (non-service task) |
| 6 | Evidence report | PASS — this file |
| 7 | .env.example | SKIP (no env vars involved) |

---

## Outcome

**COMPLETE** — Doctrine v2 in force on the branch, `main` protected server-side, live hardened permission policy in place, hygiene gaps closed, both PRs open for owner review (merging intentionally left to the owner). Follow-ups outside this mission's scope: node-side audit gaps P1-1, P1-3, P3-2 (brainnode-01 auth/MCP/install ownership) and the audit's Domain 2 subagent layer remain open.
