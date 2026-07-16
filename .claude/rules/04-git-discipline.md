# Git Doctrine v2 — Trunk-Based Development

**Version:** 2 — adopted 2026-07-15 (Phase 2A governance hardening).
Replaces Git Discipline v1 in full. v1's develop-branch model, dated branch-naming
hard blocks, and worktree lifecycle hard blocks are deleted, not carried forward.

---

## Rule 1 — Trunk-Based Development (GitHub Flow)

- Branch from `main`. PR back to `main`. That is the entire branch topology.
- No `develop` branch exists or is referenced. Do not create one.
- GitHub is the canonical remote.

---

## Rule 2 — main Is Protected Mechanically

- Enforcement is server-side at GitHub: a pull request is required to merge into
  `main`; force pushes and branch deletion are blocked by branch protection.
- `GIT_MAIN_DIRECT_WRITE` remains as a **local courtesy rule** — do not commit to
  or push `main` directly — but the enforcement mechanism is GitHub branch
  protection, not agent compliance.

---

## Rule 3 — Two-Commit Discipline (canonical definition)

Each task lands on `main` via PR as **exactly two logical commits**:

1. **Implementation** — the code, configuration, or documentation change itself.
2. **Evidence artifact** — the report in `outputs/validation/` (plus any task
   specification documents).

Working commits on feature branches are unrestricted; squash/rebase them into the
two logical commits before the PR is finalized.

---

## Rule 4 — Branch Naming

- Branches are named `feature/<name>` or `fix/<name>`.
- Dates in the name are permitted but optional.
- There are no hard blocks on naming.

---

## Rule 5 — Worktrees (Optional)

- Worktrees are optional, for parallel agent work.
- If used, a worktree is created under `.claude/worktrees/<branch-name>/` and
  removed when its PR merges.

---

## Rule 6 — Transport (Unchanged)

- Code moves between machines via **git push/pull only**.
- SCP, SFTP, and rsync are forbidden transport methods → `TRANSPORT_BYPASS`
  hard block (output format per `02-safety.md`).
