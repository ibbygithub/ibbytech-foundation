# IbbyTech Agent Framework — Master Operating Plan
**Version:** 1.1 · **Ratified by owner:** 2026-07-19 · **Status:** ACTIVE
All agents and sessions treat this document as law. Changes travel through
git PRs, never through improvisation.

## 1. Purpose and principle
The owner converses and decides; agents plan, build, test, and document; git
and the vault remember. The owner's hands touch only genuinely-human surfaces:
payments, account settings, physical hardware, final judgment calls. Any task
landing on the owner outside those four is a framework defect — log it in
docs/DEBT.md.

## 2. Capability grants (ruled 2026-07-19)
**Grant A — Scoped sudo, devops-agent, all three nodes.** Sudoers drop-in
/etc/sudoers.d/devops-agent enumerating only: systemctl
start/stop/restart/status for named platform services; install/cp into
platform-owned config dirs (/etc/alloy/, /etc/loki/, service compose dirs);
journalctl; package queries. NOPASSWD; sudo journal logging stays on. Anything
outside the list fails; agents needing more propose a sudoers amendment as a
PR. Capability changes travel through git.
**Grant B — Machine account + organization.** GitHub org: try "ibbytech",
fall back "ibbytech-labs" (owner ruling). Members: ibbygithub (owner role),
machine account ibbytech-agent (member, repo-creation permission, per-repo
Write on the six framework repos). Org-level ruleset: PRs required to main on
all repos, applied at creation. New projects are created in the org by the
machine account, PRIVATE by default. The six existing repos stay in the
ibbygithub namespace for now; migration is an M-7-class decision. Node
deploy keys retire once the machine account's SSH key is verified. Kill
switch: suspend ibbytech-agent.
**Grant C — Forgejo admin API token,** stored node-side only (root-owned,
mode 600, outside any git tree). Agents manage mirrors and visibility via
API. First use: flip the seven existing mirrors private.
**Grant D — Merge policy.** After CI: auto-merge on green for low-risk repos
(ibbytech-foundation docs/handoffs/evidence, mirror config, vault). Owner
click required for: platform and shogun infra changes; anything touching
sudoers, credentials, or personas; any PR flagged as a deviation. The gate is
encoded in CI config, not memory.

## 3. Roles
- Planner (chat): converses with owner, emits plans and mission files; output
  is always a git artifact.
- Orchestrator (Claude Code, brainnode-01, tmux + Remote Control): reads
  missions from git, decomposes, dispatches subagents, assembles PRs.
- Subagents (reconciled in M-4): implementer, security-reviewer,
  QA/validator (suites must be green before any PR opens), docs/librarian
  (evidence to outputs/validation/, knowledge to the vault).
- Laptop Claude Code: Windows-only duties (checkout sync, mkcert, desktop
  tasks).
- Owner: decisions, merges per Grant D, human-only surfaces.

## 4. Model tiering
Declared per-subagent via frontmatter model field. Opus-class: planning,
security review, irreversible actions. Sonnet-class: implementation, service
builds, test writing (default workhorse). Haiku-class: log triage,
formatting, evidence assembly, catalog reconciles, commit hygiene. Local
models (Hermes node): invoked as tools, not sessions — bulk summarization,
RSS classification, vault enrichment. Rule: the reviewing model is >= the
authoring model. Tiering is the Pro-vs-Max pressure valve; revisit the
subscription decision with one week of real Plane 2 usage data.

## 5. Mission pipeline (every mission, no exceptions)
Plan in chat -> mission file committed to
ibbytech-foundation:docs/missions/ with an EXECUTE ON header -> launch ->
pre-flight gate -> build -> QA gate (validator, suites green) -> two commits
-> PR with customer debrief (What changed / Why your life is better / What to
check or decide) -> merge per Grant D -> librarian writes vault entry +
evidence -> post-mission housekeeping (checkout syncs, branch deletion)
executed by agents within the mission, never left as owner homework.
Failure anywhere: stop, verbatim report, 4-step diagnostic path, wait.

## 6. Build queue (each item is one mission)
- M-2 "Keys to the kingdom": sudoers drop-ins on three nodes; owner creates
  org + ibbytech-agent (one browser sitting); node SSH key registered to the
  machine account; deploy keys retired; Forgejo admin token minted and
  stored; seven mirrors flipped private via API; Loki activation one-liner
  run under new sudo. Closes PR #18 items 1, 2, 6.
- M-3 CI: GitHub Actions on all six repos — JSON/YAML validation, hook
  selftests, governance greps, validate suites where present; required
  checks; auto-merge rules per Grant D. Check Actions minute quotas on
  private repos during design.
- M-3.5 Project genesis template: reusable mission in
  docs/missions/templates/ — gh repo create in the org (private), scaffold
  (README, .gitignore, CLAUDE.md from foundation template, plugin reference,
  docs/, outputs/validation/, CI workflow stamped in), clone to
  /opt/git/work/<name>, Forgejo mirror added PRIVATE via API, vault entry,
  row in docs/PROJECTS.md. Owner involvement: the concept chat only.
- M-4 Subagent layer: reconcile plugin + vault agent sets; add QA/validator
  and librarian; per-agent runbooks under docs/; model tiers in frontmatter;
  PostToolUse evidence hook; tool allowlists including Google-connector
  fencing (chat discussion first).
- M-5 Plane 2 pilot: one cron mission end-to-end (nightly catalog reconcile
  + repo health report) proving headless operation.
- M-6 Vault integration (own planning chat first): hooks writing decisions
  and evidence to the vault automatically; QMD recall as standard
  pre-flight; RSS research pipeline.
- M-7 Housekeeping sweep: laptop ~/.ssh hygiene; Fable5-haness-review
  mining; gitleaks full-history scan (owner answered "unsure" on
  secrets-in-history); svcnode root disk (85%); stale branches; certs-dir
  file perms; MOTD probe patch; org migration decision for the six repos.

## 7. Standing registers (agent-maintained, read at session start)
docs/DECISIONS.md · docs/OUT-OF-SERVICE.md · docs/DEBT.md ·
docs/PROJECTS.md. Nothing lives only in chat.

## 8. Workspace trust
brainnode-01: /opt/git/work/ parent-path trust configured in M-2; new
project folders inherit; the node never prompts. Laptop keeps its per-folder
trust prompt by design — the human machine retains its gate.
