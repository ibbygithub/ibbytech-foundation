# Mission: Phase 2A — Governance Hardening
Repo: ibbytech-foundation | Branch: feature/governance-hardening-v2
Input: docs/audits/AGENT_READINESS_AUDIT.md on branch feature/20260715-agent-readiness-audit (audit of main @ 4449986)

## RULING CONTEXT (approved by repo owner; supersedes any conflicting existing rule in this repo)
- Git Doctrine v2 (Task 1) replaces the current 04-git-discipline.md in full.
- The develop branch requirement is DELETED, not fulfilled. Do not create a develop branch.
- GitHub remains the canonical remote. Branch protection on main is the enforcement mechanism.
- Two-commit discipline (canonical definition): each task lands on main via PR as exactly two logical commits — (1) implementation, (2) evidence artifact. Working commits on feature branches are unrestricted; squash/rebase into the two logical commits before the PR is finalized.

## TASK 1 — Rewrite .claude/rules/04-git-discipline.md as "Git Doctrine v2" containing exactly these rules
1. Trunk-based development (GitHub Flow): branch from main, PR back to main. No develop branch exists or is referenced.
2. main is protected mechanically at GitHub (PR required, force-push and deletion blocked). GIT_MAIN_DIRECT_WRITE remains as a local courtesy rule; enforcement is server-side.
3. Two-commit discipline as defined in RULING CONTEXT.
4. Branch naming: feature/<name> or fix/<name>. Dates permitted but optional. No hard blocks on naming.
5. Worktrees optional for parallel agent work; if used, created under .claude/worktrees/<branch-name>/ and removed when the PR merges.
6. Transport rule unchanged: code moves between machines via git push/pull only; SCP/SFTP/rsync forbidden (TRANSPORT_BYPASS hard block).

Then search every file in .claude/ and templates/ for references to a develop branch or to the old naming/worktree hard blocks and update them for consistency with Doctrine v2.

## TASK 2 — GitHub branch protection on main
Use the gh CLI only if `gh auth status` shows an authenticated session:
- Require a pull request before merging (0 required approvals is acceptable — solo operator).
- Block force pushes and branch deletion.
If gh is not authenticated, do NOT attempt workarounds or interactive logins; record the exact manual steps (GitHub -> repo Settings -> Branches -> add rule for main) in the evidence artifact and mark this item DEFERRED-MANUAL.

## TASK 3 — Tighten templates/settings-baseline.json per the six audit Domain 1.6 flags, then write the corrected version to .claude/settings.json
(The template file gets the same fixes so future instantiations inherit them.)
- Flag 1: remove blanket auto-allow of git push*/git merge* in the platform-repo scope. Under Doctrine v2: allow push and merge to non-main branches in all repo scopes; deny any push to main or master and any force push (--force, -f) in all repo scopes.
- Flag 2: extend secret-read denies beyond cat to cover head, tail, grep, less, more, awk, sed, strings, and find with -exec, applied to secret paths: ~/.ssh/*, *.env*, *secret*, *credential*, *auth.json*, *token*. Keep the existing cat denies.
- Flag 3: remove the blanket Bash(echo *) allow (shell redirection makes it a write primitive). Add narrower allows only where a concrete need exists in the rules.
- Flag 4: remove auto-allow of chained python*/pip* commands in the platform-repo scope; package installs remain Yellow Zone (human confirm).
- Flag 5: duplicate every SQL write deny in lowercase (drop, insert, update, delete, truncate, alter, grant) for the dba-agent psql grant, and add a comment that database writes flow through migrations only.
- Flag 6: no permission-layer change; record in the evidence artifact as accepted residual risk mitigated by server-side branch protection (Task 2).
Validate that the final .claude/settings.json parses as valid JSON and that claude loads it without configuration errors.

## TASK 4 — Hygiene
- Create root CLAUDE.md as a 2-3 line pointer stub directing readers and tooling to .claude/CLAUDE.md and .claude/rules/. Do not duplicate rule content.
- Delete the stray, unregistered .worktrees/hermes-rules/ directory at repo root.
- Correct the skills list in .claude/CLAUDE.md to match the actual contents of skills/ (ciso-security, dbnode-01 only).

## TASK 5 — Land it under the new doctrine
- Squash working commits into two logical commits: (1) "feat(governance): git doctrine v2, hardened settings.json, hygiene fixes" and (2) "docs(evidence): phase 2A governance hardening report".
- This mission file (docs/missions/) is included in the evidence commit.
- Evidence artifact at outputs/validation/2026-07-15_governance-hardening_report.md using templates/evidence-report-template.md, Persona(s): none (laptop-local). It must map every addressed gap ID (P2-1, P2-3, P2-4, P3-1, P3-3, P3-5, and all six 1.6 flags) to what changed, with verification output for each.
- Open a PR: feature/governance-hardening-v2 -> main.
- Open a second PR for the stranded audit branch: feature/20260715-agent-readiness-audit -> main, content unchanged.
- If gh cannot create PRs, push both branches and record the manual PR steps in the evidence artifact.

## CONSTRAINTS
Modify only this repository; no SSH to any node; do not merge either PR — the owner reviews and merges.

## COMPLETION CONDITION
Both branches pushed; both PRs opened (or DEFERRED-MANUAL documented); .claude/settings.json exists, is valid JSON, and contains all six flag fixes; 04-git-discipline.md contains Doctrine v2 with zero develop references remaining repo-wide; evidence artifact and this mission file present in the second logical commit.
