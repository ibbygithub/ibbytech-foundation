# HANDOFF — IbbyTech Agent Framework (Session 2 → Session 3: Homelab Execution → Mission Delegation)

**Date:** 2026-07-18
**From:** Fable 5 chat session 2 (brainnode-01 bring-up, completed)
**To:** Fable 5 chat session 3 (mission-delegation phase)
**Owner:** Ibby (Todd) — retired 30-yr IT veteran, former CISO (CA EDD, CA DOJ), runs IbbyTech. Mid-level technical answers, not novice. Has ADHD — respect the communication contract strictly.

**⚠️ FIRST ACTION FOR SESSION 3:** This handoff must stop being chat-only context. Commit this file to `ibbytech-foundation` at `docs/handoffs/HANDOFF-2026-07-18-session2.md` (and ingest into the Second Brain vault's `02_Sources/`). Ibby explicitly flagged that decisions and supporting facts are being lost between chat sessions; the fix is his own infrastructure — handoffs, decisions, and rulings live in git, and chat sessions read them from there. Session 3 should also recommend he create a Claude Project for this workstream so documents persist across chats.

---

## 1. COMMUNICATION CONTRACT (non-negotiable — carried from session 1, reaffirmed and extended in session 2)

1. **Every user action as numbered steps:** WHERE (browser / PowerShell / SSH / Claude Code prompt) / DO (exact copy-pasteable command or click) / YOU SHOULD SEE (expected output). Never mix two surfaces in one step. **Session 2 violation and consequence:** browser actions (adding GitHub deploy keys) were buried inside a terminal step's YOU SHOULD SEE text; the keys never got added and all five clones failed with `Permission denied (publickey)`. Browser work gets its own numbered steps, always.
2. **Chat about concepts BEFORE producing code or missions.** Reasoning and tradeoffs first, then the artifact.
3. **Concrete next steps capped at ~4 items.**
4. **Every completed task ends with a customer debrief:** What changed / Why your life is better / What to check or decide.
5. **Whole, copy-pasteable code/commands only. No snippets.**
6. **When a task produces no output or fails, give a 4-step diagnostic path.**
7. **Show the map, not just the turns.** Session 2 escalation: Ibby rightly pushed back that he was being led step-by-step with no visible goal ("I don't believe you have a goal. Do you have a goal?"). Every session must keep the campaign roadmap explicit and place each task on it. Concept-before-action applies to the campaign, not just each command.
8. **Ibby is not the coding agent.** Ruling made at end of session 2: bootstrap/credential-trust work (which legitimately required his hands) is DONE. From now on: the chat assistant plans and writes mission files; node agents execute; Ibby only (a) launches missions (one paste, ideally via Remote Control from browser), (b) merges PRs in GitHub web UI (only until CI mission lands), (c) performs genuinely-human actions (account settings, payments, hardware).

### Terminal gotchas learned in session 2 (avoid re-triggering)
- The Proxmox community-scripts MOTD banner probes terminal background color on every fresh shell; typing immediately in a new tmux pane/shell lets the escape response land in the input buffer and garble the command (`11;rgb:0c0c/...`). Pause ~2 seconds after any fresh shell before typing. Cosmetic; permanent fix (patch `/etc/update-motd.d/`) offered, deferred.
- `exec $SHELL -l` swallows any command pasted after it on the same paste — the new shell discards the old shell's pending input. One command at a time around shell replacement.
- Long command output (e.g., a big `git pull` file listing) overruns Ibby's SSH scrollback. Keep verification commands' output short; use `--stat`, `| tail`, or redirect to a file when output could be large.

---

## 2. GOAL & TARGET ARCHITECTURE (unchanged end-state, expanded with Second Brain reconciliation)

**End state:** All agent coding/execution OFF the laptop, INTO the homelab. Laptop and browser are thin management layers. **Subscription auth only — NO Anthropic API keys anywhere (standing owner ruling).**

**Three execution planes:**
- **Plane 1 — Interactive:** Claude Code in tmux on brainnode-01, steered via Remote Control (claude.ai/code) or mobile app. ✅ **PROVEN WORKING in session 2** (see §4).
- **Plane 2 — Scheduled/autonomous:** `claude -p` missions via cron/systemd on brainnode-01. Not yet started. **Blocked on the Pro-vs-Max decision (§6 open items).**
- **Plane 3 — Event-driven (Phase 4, future):** svcnode-01 RSS/Telegram/Slack triggers. Evaluate "Claude Code Channels" before building custom.

**NEW — Three-layer data architecture ruling (session 2, reconciles the Second Brain / NFS share question):**
- **Layer 1 — Code:** GitHub canonical; local-disk working clones on every executing machine; git push/pull only transport. **Live git repos NEVER on the network share** (SMB/NFS locking semantics can corrupt the object DB/index). Reference copies of repos are served by: (a) the queued Forgejo pull-mirror, (b) one-way exports (`git bundle`/archive) into the share's existing `repos/mirrors` and `repos/bundles` folders, (c) QMD indexing of local clones.
- **Layer 2 — Knowledge:** The Second Brain vault (see §3) — the memory layer for ALL projects. Repo corpus is already ingested into the vault's `02_Sources/GitHub Repositories/` for semantic reference; that is the sanctioned "repo files available for reference" mechanism.
- **Layer 3 — Bulk:** The 12 TB NFS/SMB share ("X:") — datasets, audio, archives, per-node agent scratch (`agent-work/`), inbox/handoff pipeline (`shared/inbox`), exports. Already structured for this.

**Code residency:** GitHub canonical. brainnode-01 working clones at `/opt/git/work/` (**location re-confirmed by owner in session 2** after he questioned `/opt` as production-signaling; consistency won). Laptop is just-another-checkout at `C:\git\work\`.

---

## 3. THE SECOND BRAIN (major session-2 addition — session 1 didn't know about this)

- **Repo:** `github.com/ibbygithub/AI-second-Brain` — Ibby's adaptation of **Obsidian Mind** (breferrari/obsidian-mind): an Obsidian vault giving Claude Code persistent memory via lifecycle hooks (SessionStart/UserPromptSubmit/PostToolUse/PreCompact/Stop), `/om-*` commands, subagents, and **QMD semantic search** exposed as an MCP server. Not 100% in production; Ibby has been oscillating between foundation-repo work and Second Brain work — the three-layer ruling above is the reconciliation.
- **`/opt/git/work/agent-vault-system` on brainnode-01 IS the clone of AI-second-Brain** (verified via `git remote -v`). Session 2 found it parked on stale branch `codex/adopt-obsidian-mind` whose content was already merged to main; checked out main and fast-forwarded. Working tree clean.
- **Laptop clone:** `C:\git\work\second brain` — verified on main, clean, exactly in sync with origin (no ahead/behind). Sync triangle laptop ↔ GitHub ↔ node is closed; Obsidian-on-laptop is the human editing surface, git is the sync transport.
- **Vault already contains:** full ingested corpus of biomesh, platform, shogun, Trading-research, ibbytech-foundation + external repos, NIST 800-53r5 page-by-page ingest, `brain/Working With Ibby.md`, `_agent/` reports and policies (`canonical-authority.md`, `REPO_SYNC_CONTRACT.md`, `BRAINNODE_GITHUB_AUTH.md` under docs/operations — session 3 should READ these before making repo-sync decisions; some of this ground is already documented there).
- **qmd MCP server:** approved in session 2 (per-server approval "1", NOT "use all future servers" — deliberate trust-gate ruling), shows `✔ connected · 4 tools`. Audit P1-3 CLOSED.
- **Future integration mission (queued):** RSS/bot research pipeline (ML releases, BirdNET datasets for BioMesh, etc.) writes summaries into vault `01_Inbox` → hooks classify → QMD indexes → any session recalls by meaning. Design as its own mission; not yet specced.

---

## 4. VERIFIED CURRENT STATE (end of session 2)

**brainnode-01 (192.168.71.222, Debian 13 LXC):**
- Claude Code **native install 2.1.212** at `~/.local/bin/claude`, self-updating as devops-agent; leftover root npm install removed via Proxmox root console (`npm -g uninstall`); `claude doctor` = "No installation issues found." (The "Last update attempt: failed (no_permissions) — 2026-07-17" line is a stale historical log entry from the old npm binary; ignore, it rolls off.) Audit P1-1 fully closed.
- **Login is Claude Pro, NOT Max** — startup banner shows "Sonnet 5 · Claude Pro". See §6 open decision.
- qmd MCP approved & connected (above). Note: claude.ai **Gmail / Google Calendar / Google Drive connectors ride into node sessions** from the subscription account — flagged as a Phase 2D allowlist/fencing discussion item for headless missions.
- **Remote Control PROVEN:** command is `/remote-control` (or `/rc`) — NOT `/remote`, and NOT automatic; doctor showing "Remote Control available" only means the feature exists, each session must opt in. Known rough edge: session may not appear in the claude.ai/code list until the direct session URL is opened once. Full smoke test passed: browser steering, tmux (`tmux new -s agents`) detach survival, and full SSH-disconnect survival. **This is the Plane 1 mechanism, working.**
- **All six repos cloned at `/opt/git/work/`:** agent-vault-system, biomesh, ibbytech-foundation, platform, shogun, Trading-research.

**GitHub credentials (node):**
- Pattern: **one ED25519 deploy key per repo** (GitHub prohibits attaching one deploy key to multiple repos — a session-2 correction of an initially wrong plan). Keys: `~/.ssh/devops-agent-{biomesh,platform,shogun,Trading-research,ibbytech-foundation}_ed25519`, all **read-only**, registered under each repo's Settings → Deploy keys as `brainnode-01-devops-agent`.
- `~/.ssh/config` host aliases: `github-biomesh`, `github-platform`, `github-shogun`, `github-trading`, `github-foundation` (all → github.com with per-key IdentityFile + IdentitiesOnly). Pre-existing: `Host github.com` → `github_ai_second_brain_ed25519` (per-repo deploy key for AI-second-Brain, set up in May — verified clean, no account-wide key on the node). Also `hermes-node` / 192.168.71.111 entries exist.
- Clone URLs use the aliases: `git@github-<name>:ibbygithub/<repo>.git`.
- **Read-only by design.** When Plane 2 missions need to push branches, that is a deliberate future decision (write deploy keys vs. scoped machine account) — do not sneak it in.

**GitHub repos:**
- **Flipped PRIVATE in session 2** (owner action). Post-flip access verified: node `git fetch` OK (NODE_ACCESS_OK), laptop `git fetch` OK (LAPTOP_ACCESS_OK). Session 3 should spot-check visibility badges on all repos incl. AI-second-Brain and ibbytech-foundation to confirm none were missed.
- **Caveat delivered to owner:** anything ever public may have been crawled; going private stops future exposure only. If any repo history contains secrets, that's a rotation task — owner to flag.

**Foundation repo:** unchanged from session-1 handoff (main @ 8c317fd, Git Doctrine v2, branch protection with enforce_admins, 146/125 permission policy, plugin ibbytech-core v0.2.0, Mission Debrief Standard). Plugin still disabled on laptop; cross-repo rollout still queued.

**Laptop:** unchanged from session-1 handoff (workspace trust, defaultMode auto via settings.local.json, stray committed `acceptEdits` line still pending removal in some mission's diff).

---

## 5. PROCESS RULES (session-1 rules stand; session-2 additions)

1–5. (From session 1: freshness precondition; single-writer for governance files; `/goal` 4000-char limit → mission file + pointer; Doctrine v2 branch/two-commit/PR flow; plugin edits require marketplace-maintainer release procedure.) All still in force.
6. **One deploy key per GitHub repo.** Never plan a shared key across repos.
7. **Browser actions are always their own numbered steps** — never embedded in a terminal step's expected output.
8. **MCP servers get per-server approval** (option 1), never blanket "all future servers in this project."
9. **Chain independent commands with `;` not `&&`** when partial success is acceptable and diagnosable — `&&` masks which later items would have succeeded.
10. **`ssh -G <host> | grep -i identityfile`** and **`ssh -Tv ... | grep Offering`** are the canonical two-step diagnosis for key-selection problems; the config resolved correctly in session 2, and the failure was on the GitHub side (keys never registered).

---

## 6. OPEN ITEMS / DECISIONS PENDING

1. **Pro vs Max subscription (DECISION NEEDED before Plane 2 goes live).** Node authenticates as Claude Pro. Claude Code draws from the same rolling-window/weekly pool as chat; Max is 5x/20x that pool. Cron missions + interactive use + future subagents concurrently is exactly the load profile that thin Pro headroom struggles with (and the session-1 "17-agent parallel" incident is the cautionary tale). Options: stay Pro and accept pauses at the ceiling (usage-credit fallback exists), or upgrade before Plane 2. Owner's call; not urgent for Plane 1 interactive work. A `/status` reading of actual limits was requested but never captured — session 3 can grab it.
2. **Google connectors on node sessions:** decide whether headless missions should be fenced off from Gmail/Calendar/Drive tools (settings.json denies) — fold into the Phase 2D allowlist discussion (which per session-1 rules happens in chat BEFORE the mission is written).
3. **Secrets-in-history triage:** owner to state whether any formerly-public repo ever contained credentials; if yes, rotation mission.
4. **Housekeeping (when convenient):** stray `acceptEdits` in committed settings.json; delete merged branches; optional MOTD probe patch on brainnode-01.
5. **Whether AI-second-Brain becomes a sixth framework repo** for plugin rollout purposes (it already has its own `.claude/` ecosystem from Obsidian Mind — reconcile, don't stack, when cross-repo rollout happens).

---

## 7. ORDERED QUEUE (session 3 starts here)

**0. Persist this handoff** — commit to `ibbytech-foundation:docs/handoffs/` (see banner at top). First PR of session 3; can itself be the first delegated micro-mission.

**1. Forgejo pull-mirror mission (FIRST FULLY DELEGATED MISSION — the proof case for the new division of labor).**
   - Pending confirmation from owner (asked at end of session 2, not yet answered): service definition lands in the **platform repo** (svcnode-01 Docker/Traefik stack), foundation repo untouched except mission file. Confirm, then write the mission file.
   - Shape: Claude Code on brainnode-01 → SSH to svcnode-01 as devops-agent → add Forgejo service following existing service patterns → Traefik route `git.platform.ibbytech.com`, self-managed TLS per existing convention → configure pull-mirroring of the now-private GitHub repos (needs one read-scoped token from owner — the only human credential step) → verify → two commits → PR with customer debrief. Owner: launch, provide token, merge.
   - Forgejo explanation given to owner (he asked): self-hosted Gitea-fork GitHub-lookalike, read-only auto-syncing mirror, one write target (GitHub) preserved; LAN speed + escape hatch + browsable private code without GitHub login.

**2. CI mission (explicitly promised — removes owner's manual merge burden).** GitHub Actions: JSON validation, hook selftests, governance greps; required checks on main; auto-merge. Frame: "the robot reviewer we hired." Note: repos are now private — Actions minutes on private repos have quotas on free plans; check limits during design.

**3. Phase 2D — subagent layer.** Audit expected subagents (coding, github, security-review, logging) against plugin's existing agents (planner/implementer/reviewer-validator/docs) — reconcile, don't duplicate. Runbooks under `docs/` per agent. PostToolUse evidence-trail hook (audit P2-2). **Allowlist discussion in chat FIRST** (fold in open item #2, Google-connector fencing). Also reconcile against the vault's own subagent set from Obsidian Mind.

**4. Cross-repo plugin rollout** (≥0.2.0 into platform, biomesh, shogun, Trading-research; platform-repo doc alignment; decide AI-second-Brain's status per §6.5).

**5. Second Brain research-pipeline mission** (RSS → vault inbox → classification → QMD; design in chat first).

**Then:** Plane 2 cron missions (after Pro/Max decision), Phase 3/4 per original roadmap.

---

## 8. STATE OF MIND

Session 2 was productive but had a mid-session rupture worth remembering: after a string of successful hands-on steps, Ibby stopped and challenged the entire mode of operation — no visible goal, being led turn-by-turn, and (critically) *he* was doing all the typing while the "agent framework" watched. The recovery that worked: owning the failure plainly, stating the goal and full route explicitly, reconciling the Second Brain instead of deflecting it, and ending with the division-of-labor ruling (§1.8). He responded well to decisive rulings with reasoning attached (the "answer 1 or 2?" MCP moment; `/opt` confirmation), to honest ownership of mistakes (the deploy-key surface-mixing failure was named as the assistant's contract violation, and the diagnosis that followed was methodical), and to being shown the *why* behind each control. He is rightly wary of context evaporating between chat sessions — hence the banner at the top of this document. The wins are real: the node is a proven, remotely-steerable, fully-credentialed worker; the repos are private; the vault is reconciled and synced. Session 3's job is to make him a customer, not a typist: one mission at a time, debrief every time, and get these handoffs into git where they belong.
