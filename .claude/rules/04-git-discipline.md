# Git Discipline — Branch Strategy, Worktree Policy, and Agent Lifecycle

## Core Principle

Git operations are infrastructure operations. They carry the same discipline
requirements as node access, service deployment, and credential use.
Correctness and traceability are not optional. Speed is never a justification
for skipping the lifecycle contract defined here.

---

## Branch Architecture

All IbbyTech projects use a trunk-based model: one default branch plus
short-lived task branches that land via pull request.

*(Model history: the previous three-tier `main`/`develop`/`feature` model was
retired 2026-07-11 — four months of practice showed every change landing via
feature → PR → default branch, with `develop` unused and stale. `develop` was
deleted after verifying zero unmerged value. Evidence:
`platform/outputs/validation/2026-07-11_develop-retirement_report.md`.)*

| Branch | Purpose | Who Writes | Who Merges |
|:---|:---|:---|:---|
| default (`master` or `main`, per repo) | Production-canonical state | Nobody directly — PR merges only | Human, or agent on explicit human instruction |
| `feature/<YYYYMMDD>-<task-slug>` | Active agent work | Agent | Via PR — human confirm |
| `hotfix/<YYYYMMDD>-<issue-slug>` | Urgent targeted fixes | Agent | Via PR — human confirm |

### Rules

- The default branch is never committed to directly. By anyone. Ever.
- Every change lands via a pull request from a `feature/` or `hotfix/` branch.
- PR merge requires explicit human instruction — the agent may open PRs
  freely but does not merge one without being asked.
- If a task does not clearly map to an existing branch, create a new
  `feature/` branch. Never work on the default branch directly.

---

## Branch Naming Convention

Branch names are constructed by the agent using this exact format:

```
feature/YYYYMMDD-<task-slug>
hotfix/YYYYMMDD-<issue-slug>
```

### Rules

- `YYYYMMDD` is the date the branch is created (today's date at creation time)
- `<task-slug>` is a short, lowercase, hyphen-separated description of the task
- Slugs must be meaningful and traceable to the task being performed
- Random words, session IDs, and auto-generated strings are forbidden
- Maximum slug length: 40 characters

### Valid examples

```
feature/20260305-firecrawl-postgres-validation
feature/20260305-reddit-gateway-service-doc
feature/20260305-llm-gate-loki-logging
hotfix/20260305-traefik-label-correction
```

### Invalid examples

```
witty-platypus          ← random words — HARD BLOCK
claude-session-3        ← session artifact — HARD BLOCK
fix                     ← no date, no context — HARD BLOCK
feature/my-changes      ← no date — HARD BLOCK
```

---

## Worktree Policy

Worktrees are permitted for parallel task isolation. They are governed by a
strict lifecycle contract. Unmanaged worktrees are platform rot.

### Creation Rules

- One worktree per feature branch. One feature branch per discrete task.
- The worktree directory name **must match the branch name exactly**
- Worktrees are created under `.claude/worktrees/<branch-name>/`
- Before creating a worktree, state the task it represents and the branch
  name it will use

### Lifecycle Contract

Every worktree follows one of two exit paths. There is no third option.

**Path A — Task Completed Successfully:**
1. Agent runs validation and captures evidence
2. Agent presents Merge Ready notice (see format below)
3. Human responds `proceed` or `hold`
4. On `proceed`: agent pushes the branch and opens a PR to the default
   branch; after the PR is merged (human, or agent on explicit instruction),
   agent deletes the worktree and the local feature branch
5. Agent writes evidence record to `outputs/validation/`

**Path B — Task Abandoned or Superseded:**
1. Agent states reason for abandonment
2. Agent explicitly deletes the worktree directory
3. Agent deletes the local feature branch
4. Agent writes abandonment record to `outputs/validation/`

### Hard Block Triggers

- Worktree directory name does not match branch name → HARD BLOCK
- Worktree exists after task completion without Path A or Path B executed → HARD BLOCK
- More than 3 active worktrees simultaneously without explicit human approval → HARD BLOCK

---

## Commit Standards

### Commit Message Format

```
<type>(<scope>): <short description>

<optional body — what and why, not how>
```

| Type | Use for |
|:---|:---|
| `feat` | New capability or service |
| `fix` | Bug or configuration correction |
| `docs` | Documentation only changes |
| `chore` | Maintenance, dependency updates, cleanup |
| `deploy` | Deployment configuration changes |
| `security` | Security-related changes |

### Rules

- Commit messages must be meaningful. "fix", "update", "changes" are forbidden.
- Commit early and often within a feature branch — do not accumulate large
  uncommitted diffs
- Never commit secrets, `.env` files, or credential material — if this is
  detected, stop immediately and report
- Every commit on a feature branch must leave the branch in a runnable state

### Valid examples

```
feat(firecrawl): add postgres persistence with pgvector support
fix(traefik): correct service label for llm-gateway routing
docs(reddit-gateway): add service doc and register in _index.md
security(ssh): rotate devops-agent key reference in compose config
```

---

## Operation Zone Classification

Git operations are classified into three zones. Zone determines agent autonomy.

### Green Zone — Agent Acts Autonomously

No confirmation required. These operations are local, reversible, and
carry no risk to shared state.

- `git status`, `git log`, `git diff`, `git show`
- `git branch` (create local feature branch)
- `git checkout`, `git switch`
- `git add`, `git commit`
- `git stash`, `git stash pop`
- `git worktree add` (with compliant naming)
- `git fetch` (read-only remote sync)
- `git push origin <feature-branch>` when all new commits since last push are
  type `docs` or `chore` AND touch only: `outputs/`, `services/*/README*`,
  `.claude/services/`, `.claude/databases/`, or `outputs/planning/`

### Yellow Zone — Agent Proposes, Human Confirms

Agent prepares the operation, presents the Merge Ready notice, and waits.
Human responds `proceed` or `hold`. No timeout — agent waits indefinitely.

- Merging a PR into the default branch (`gh pr merge` / web UI) — on
  explicit human instruction only
- `git push` (feature branch pushes not covered by the Green Zone docs exemption)
- `git worktree remove`
- `git branch -d` (delete local branch post-merge)
- `git tag`
- `git rebase` (only on unshared branches)
- `git push origin --delete <branch>` when ALL conditions are verified:
  1. `git log --oneline origin/<branch> ^origin/<default>` returns empty
     (fully merged into the default branch)
  2. Branch is NOT: `master`, `main`, or matching `svcnode/*`
  3. Human has confirmed cleanup intent in the current session

  Agent must state the merge verification result before executing.

### Red Zone — Human Only

Agent stops, explains what is needed and why, and hands off completely.
Agent does not execute these under any circumstances.

- `git push --force` or `git push --force-with-lease`
- `git reset --hard`
- `git clean -fd`
- `git branch -D` (force delete)
- Any direct commit or push to the default branch (`master`/`main`)
- `git remote set-url` or any remote configuration change
- `git push origin --delete master`
- `git push origin --delete main`
- Any remote branch delete where merge status cannot be verified
- Any remote branch delete not satisfying all Yellow Zone conditions above

---

## Merge Ready Notice — Required Format

When a task reaches Yellow Zone merge readiness, the agent must produce
this exact format before any merge or push operation:

```
╔══════════════════════════════════════════════════════════════════╗
║  ⏸  MERGE READY — Human Verification Required                  ║
╠══════════════════════════════════════════════════════════════════╣
║  Branch:     feature/YYYYMMDD-task-slug                        ║
║  Target:     default branch (via pull request)                  ║
║  Commits:    N commits since branch creation                    ║
║  Files:      N modified, N added, N deleted                     ║
║  Validated:  [brief description of what was tested/verified]   ║
║  Evidence:   outputs/validation/YYYY-MM-DD_<task>_report.md    ║
╚══════════════════════════════════════════════════════════════════╝

Changes summary:
- [plain English description of what changed and why]
- [any known risks or dependencies]

Respond "proceed" to push and open the PR, or "hold" to pause.
```

The agent does not proceed until receiving an explicit `proceed` response.
`ok`, `yes`, `do it`, `go ahead` are all accepted as equivalent to `proceed`.
Silence is not consent. Ambiguous responses prompt the agent to re-ask once.

---

## Parallel Task Rules

When two or more worktrees are active simultaneously:

- Each task must have a declared scope at creation time (which files/services
  it will touch)
- No two parallel tasks may modify the same file without a declared dependency
  logged in both task briefs
- If a conflict is detected during merge, stop both tasks, report the conflict,
  and wait for human resolution guidance
- Parallel tasks are merged to the default branch sequentially, not
  simultaneously
- The second PR must be updated from the default branch after the first
  merges, to incorporate the first task's changes before its own merge

---

## Hard Block — Git Violation Output Format

When a git-related HARD BLOCK is triggered, use the standard format from
`02-safety.md` with these git-specific violation types:

- `GIT_FORBIDDEN_OPERATION` — Red Zone operation attempted
- `GIT_NAMING_VIOLATION` — branch or worktree name does not comply
- `GIT_MAIN_DIRECT_WRITE` — any attempt to commit or push directly to the default branch (`master`/`main`)
- `GIT_WORKTREE_ROT` — worktree exists beyond task lifecycle without cleanup
- `GIT_PARALLEL_CONFLICT` — two active tasks declared overlapping file scope
- `GIT_UNAUTHORIZED_PUSH` — push attempted without Yellow Zone confirmation

Evidence file naming: `outputs/validation/YYYY-MM-DD_HARDBLOCK_GIT_<type>.md`
