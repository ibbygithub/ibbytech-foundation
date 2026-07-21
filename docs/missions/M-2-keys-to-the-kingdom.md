# Mission M-2 — "Keys to the Kingdom"

**EXECUTE ON:** brainnode-01
**MODEL:** Sonnet (implementation tier per Master Operating Plan §4)
**STOP-ON-MISMATCH:** If the running host is not brainnode-01, or the login model
is not Sonnet-class, HALT and report. Do not execute any phase.
**Mission ID:** M-2 · **Authored:** 2026-07-21 (Opus 4.8, planner tier) ·
**Ceremony phases A–C executed live:** 2026-07-21 (owner hands, root console)
**Depends on:** Master Operating Plan v1.1 (canonical), PR #8 merged.
**Closes:** PR #18 items 1, 2, 6.
**Grants activated:** A (scoped sudo), B (machine account + org), C (Forgejo admin token).

---

## 0. Place on the map
Plan persistence (M-1.5) is done. This mission collapses every standing-root and
per-repo-credential surface in the estate down to **one enumerated identity per
node** and **one machine account for GitHub**, then retires the deploy-key era.
After M-2: the owner's terminal surface is closed; the remainder of the framework
(M-3 CI → M-7 housekeeping) executes on tiered subagents. Next mission after this
is M-3 (CI).

**Design note — why this file mixes "done" and "to-do":** Phases A–C are the
root-of-trust ceremony. They require the sovereign's own hands (root console,
account creation, credential issuance) and were executed live during authoring.
They are recorded here as **evidence, not instructions** — do NOT re-run them.
Phases D–G are the executable remainder and are the actual work of this launch.

---

## 1. Pre-flight gate (Sonnet runs this first)
Stop and report via 4-step diagnostic if any check fails.

1. Host is brainnode-01; `whoami` = devops-agent (or the orchestrator identity).
2. `/opt/git/work/` contains all six clones on clean `main`, no dirty trees:
   `for d in /opt/git/work/*/; do echo "== $d"; git -C "$d" status --porcelain | head; done`
3. Machine-account key present: `test -f ~/.ssh/ibbytech-agent_ed25519 && echo KEY_OK`.
4. Forgejo token reachable through the sudo path from svcnode (Phase E depends on it):
   `ssh devops-svcnode-01 'sudo -n cat /etc/ibbytech/forgejo-admin.token | wc -c'`
   → expect `40`.

**Known noise to NOT chase:** Tavily preflight failures (OUT-OF-SERVICE by ruling);
stale Claude Code update-log lines; MOTD escape-sequence garble on fresh node
shells (pause 2s before typing).

---

## 2. Phase A — Node sudoers reconciliation  ✅ DONE (evidence)
**Executed 2026-07-21 from the Proxmox host root console.** All three nodes were
found carrying undocumented standing root that predated the framework. The
reconciliation gate below is now a **mandatory M-class verification** for every
future node this framework touches.

### Reconciliation gate (permanent, re-runnable, read-only)
```
enumerate /etc/sudoers.d/  →  check sudo-group membership (getent group sudo)
→  identify every account with a grant  →  purge unsanctioned agents
(gpasswd -d sudo; rm drop-in; usermod -L; usermod -s /usr/sbin/nologin)
→  install the single enumerated devops-agent ceiling
→  assert only "devops-agent  README" remain and no "(ALL:ALL) ALL" line
```

### Findings and dispositions (per node)
| Node | CTID/VMID | Standing root found | Action | End state |
|---|---|---|---|---|
| brainnode-01 | LXC 106 | `devops-agent` in `sudo` group (inherited `%sudo ALL`); rogue `sysadmin-agent` + `ai-coding-agent` (own NOPASSWD:ALL drop-ins, both in `sudo`+`docker`) | de-sudoed, drop-ins removed, rogues locked+nologin, enumerated ceiling installed | one identity, ceiling only |
| dbnode-01 | LXC 100 | five drop-in files → three real accounts (`ai-coding-agent`, `sysadmin-agent`, `dba-agent`); `devops-agent` had **no** sudo (under-provisioned) | rogues locked+nologin, all drop-ins purged, enumerated ceiling installed | one identity, ceiling only |
| svcnode-01 | QEMU VM 101 | rogue `sysadmin-agent`+`ai-coding-agent`; **existing `devops-agent` drop-in = full `ALL=(ALL) NOPASSWD: ALL`**; all three in `docker` group; devops-agent also in `sysadmin-agent`'s primary group | full-root drop-in replaced with enumerated ceiling, rogues locked+nologin+de-dockered, stray group membership removed | one identity, ceiling only (+docker by ruling — see D-11) |

**Enumerated ceilings installed** (verbatim, per node) are reproduced in Appendix A.
**Live-fire proof:** on brainnode-01, `sudo -u devops-agent sudo -n systemctl status alloy`
returned alloy's status (active since 2026-07-08) with `exit=0` — the enumerated
grant authenticates; no password, no `(ALL:ALL)`.

---

## 3. Phase B — Sudo I/O session logging  ✅ DONE (evidence)
The pre-existing svcnode drop-in had one thing right — full sudo session capture —
which the first ceiling rewrite dropped (a regression, caught and corrected). A
`devops-logging` drop-in was installed on **all three nodes** for consistency:

```
Defaults:devops-agent           log_output
Defaults!/usr/bin/sudoreplay    !log_output
Defaults!/usr/sbin/visudo       !log_output
```
Every `devops-agent` sudo session is now recorded to `/var/log/sudo-io/` and
replayable via `sudoreplay -l` / `sudoreplay <TSID>`. This drop-in also applies
to `hermes-agent` when M-2.5 mints it (same discipline, second identity).

---

## 4. Phase C — Machine account + organization (browser sitting)  ✅ DONE (evidence)
Executed 2026-07-21. Root-of-trust ceremony; owner-hands by design (identity
creation and credential issuance are sovereign acts, per Master Plan §1).

- **Org created:** `ibbytech` was taken → **landed on `ibbytech-labs`** (owner
  ruling honored). All org URLs and the machine account's repo-creation target
  are `github.com/ibbytech-labs`.
- **Machine account:** `ibbytech-agent`, email plus-addressed to the owner's
  Google account, org **Member**, repo-creation permitted.
- **Account SSH key:** `~/.ssh/ibbytech-agent_ed25519` generated **on brainnode-01**,
  pubkey registered account-level (one key, all repos — the machine-user model that
  makes six deploy keys redundant).
- **Six-repo access:** `ibbytech-agent` added as **Write (push) collaborator** on
  all six framework repos in the `ibbygithub` namespace (AI-second-Brain, biomesh,
  ibbytech-foundation, platform, shogun, Trading-research). This is the last
  per-repo grant that will ever be done by hand; org-native repos (M-3.5+) inherit
  access automatically.
- **Forgejo admin token:** minted (`platform-mirror-admin`, admin scope), stored
  **node-side** at `/etc/ibbytech/forgejo-admin.token` on svcnode-01 —
  `600 root:root`, outside any git tree, **40 bytes** confirmed, readable only
  through the `DEVOPS_TOKEN` sudo entry. Never touched shell history (hidden read).

---

## 5. Phase D — Retire the deploy-key era  ⬜ EXECUTABLE (Sonnet)
**Goal:** rewrite the six clones to authenticate as `ibbytech-agent`, PROVE push
works, THEN delete the read-only deploy keys — never leaving an access gap.

**D1 — add a single host alias for the account key** (idempotent; append only if absent)
```bash
grep -q 'Host github-ibbytech-agent' ~/.ssh/config || cat >> ~/.ssh/config <<'EOF'

Host github-ibbytech-agent
    HostName github.com
    User git
    IdentityFile ~/.ssh/ibbytech-agent_ed25519
    IdentitiesOnly yes
EOF
ssh -T git@github-ibbytech-agent 2>&1 | grep -i 'successfully authenticated\|Hi ' || true
```
Expect a GitHub greeting naming `ibbytech-agent`.

**D2 — rewrite all six remotes to the account alias**
```bash
declare -A R=( [AI-second-Brain]=AI-second-Brain [biomesh]=biomesh \
[ibbytech-foundation]=ibbytech-foundation [platform]=platform \
[shogun]=shogun [Trading-research]=Trading-research )
for d in /opt/git/work/*/; do
  name=$(basename "$d"); repo=${R[$name]:-$name}
  git -C "$d" remote set-url origin "git@github-ibbytech-agent:ibbygithub/$repo.git"
  echo "== $name"; git -C "$d" remote -v | head -1
done
```

**D3 — PROVE write works on all six** (no-op push of current main; must all succeed)
```bash
for d in /opt/git/work/*/; do
  name=$(basename "$d")
  git -C "$d" fetch origin --quiet && \
  git -C "$d" push origin HEAD:refs/heads/main --dry-run 2>&1 | \
    grep -q 'up to date\|->' && echo "PUSH_OK $name" || echo "PUSH_FAIL $name"
done
```
**GATE:** six `PUSH_OK`. Any `PUSH_FAIL` → STOP, report, do NOT proceed to D4
(the whole point is not to delete deploy keys until the replacement is proven).

**D4 — delete the six read-only deploy keys.**
*Credential note:* deploy-key deletion is **repo-admin scoped**; the machine
account holds Write, not Admin, so it CANNOT do this. **Execution (owner ruling
2026-07-21): run from the laptop Claude Code session, where `gh` is already
authenticated as `ibbygithub`** (the owner's admin identity) — automated, not owner
homework. The brainnode orchestrator hands this sub-step to the laptop session after
the D3 gate is green; the orchestrator MUST NOT attempt it itself (it lacks admin).
Enumerate then delete only the `brainnode-01-devops-agent` keys:
```bash
for repo in AI-second-Brain biomesh ibbytech-foundation platform shogun Trading-research; do
  echo "== $repo"
  gh api "repos/ibbygithub/$repo/keys" --jq '.[] | select(.title=="brainnode-01-devops-agent") | .id' \
  | while read -r kid; do gh api -X DELETE "repos/ibbygithub/$repo/keys/$kid" && echo "deleted key $kid"; done
done
```
Also retire the old per-repo host aliases (`github-biomesh` etc.) from
`~/.ssh/config` on the node → mark them `# LEGACY_QUARANTINED` rather than deleting,
consistent with the laptop convention.

---

## 6. Phase E — Flip the seven Forgejo mirrors private  ⬜ EXECUTABLE (Sonnet)
Grant C first use. Orchestrator SSHes to svcnode-01, reads the token through sudo,
drives the Forgejo API on localhost. Mirrors were created **public on Forgejo**
(LAN-only exposure; GitHub unaffected) — flip all to private.

**E1 — enumerate mirrors** (confirm count = 7 before mutating)
```bash
ssh devops-svcnode-01 'TOK=$(sudo -n cat /etc/ibbytech/forgejo-admin.token); \
curl -s -H "Authorization: token $TOK" \
"http://localhost:3000/api/v1/repos/search?limit=50&mode=mirror" \
| grep -o "\"full_name\":\"[^\"]*\"" '
```
Expect the six framework mirrors + the `ibby-admin/ibbygithub` profile-README mirror
(KEEP per owner) = 7. If the internal port/host differs, discover via the running
container's published port before assuming 3000.

**E2 — flip each to private**
```bash
ssh devops-svcnode-01 'TOK=$(sudo -n cat /etc/ibbytech/forgejo-admin.token); \
for fn in $(curl -s -H "Authorization: token $TOK" \
"http://localhost:3000/api/v1/repos/search?limit=50&mode=mirror" \
| grep -o "\"full_name\":\"[^\"]*\"" | cut -d\" -f4); do \
  code=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH \
    -H "Authorization: token $TOK" -H "Content-Type: application/json" \
    -d "{\"private\":true}" "http://localhost:3000/api/v1/repos/$fn"); \
  echo "$fn -> $code"; done'
```
**GATE:** every line `-> 200`. Then re-run E1's search filtered on `?private=true`
(or read each repo's `.private`) and assert all seven report private.

---

## 7. Phase F — Loki activation under the new sudo  ⬜ EXECUTABLE (Sonnet) — *config-dependent*
**Honest scope flag:** `logstack-loki-1` is already **running** (container, up 8+
days), and `alloy` is active on the nodes. "Loki activation" here means wiring the
node **alloy** agents to ship journ&nbsp;+&nbsp;file logs to the Loki endpoint —
i.e. install the alloy config into `/etc/alloy/` (covered by `DEVOPS_CFG`) and
`systemctl restart alloy` (covered by `DEVOPS_SVC`), all under the new enumerated
sudo. This proves the scoped grant does real work end-to-end.

**The exact alloy config content is NOT specified in this mission** (it is
environment-specific: Loki push URL, labels, scrape targets). Per §5 pipeline
"stop on deviation," Sonnet MUST NOT invent it. Instead:

1. Discover the current alloy config and the Loki push endpoint:
   `sudo -n cat /etc/alloy/config.alloy 2>/dev/null; docker port logstack-loki-1`.
2. If a ready config exists in the platform repo (search `platform/**/alloy*`),
   install it via `sudo install -m 0644 <src> /etc/alloy/config.alloy` and
   `sudo systemctl restart alloy`, then confirm `systemctl status alloy` healthy
   and log lines arriving in Grafana/Loki.
3. If no config is found, **STOP** and report — this becomes a short design turn
   in chat (Loki/alloy pipeline is a legitimate fork, not transcription), then a
   follow-up micro-mission. Do not guess a shipping config.

This is the one phase expected to legitimately pause; that is by design, not failure.

---

## 8. Phase G — Workspace trust on brainnode-01  ⬜ EXECUTABLE (Sonnet)
Configure **parent-path** trust for `/opt/git/work/` so the node never prompts and
new project folders (M-3.5 genesis) inherit trust. The laptop deliberately keeps
its per-folder prompt (human machine retains its gate — Master Plan §8).

Set the Claude Code trusted-folder setting for the parent path (via the settings
file the node's Claude Code uses; confirm the current mechanism with
`claude config` rather than hand-editing an assumed path). Verify by launching a
throwaway session in a fresh `/opt/git/work/` subdir and confirming no trust prompt.

---

## 9. QA gate (validator — all must be green before PR)
- [ ] Six `PUSH_OK` (D3); six deploy keys deleted (D4); legacy aliases quarantined.
- [ ] Seven Forgejo mirrors report `private:true` (E2).
- [ ] alloy healthy on all three nodes OR Phase F cleanly paused-and-reported.
- [ ] `/opt/git/work/` parent-path trust set; no prompt on fresh subdir.
- [ ] Re-run reconciliation gate read-only on all three nodes: only
      `devops-agent README` in `/etc/sudoers.d/`, no `(ALL:ALL) ALL` anywhere.

---

## 10. Commits, PR, debrief
Two commits on `feature/m-2-keys-to-the-kingdom`:
1. Evidence + config: this mission file into `docs/missions/`, the DECISIONS.md
   additions, `~/.ssh/config` change captured in the evidence report (not the key
   itself), reconciliation-gate script into `docs/operations/`.
2. Evidence report `outputs/validation/2026-07-21_m-2-keys_report.md` — per-node
   sudoers before/after, the six ceiling texts, push proofs, mirror-flip codes,
   sudo-io logging confirmation, and SHA-256 of any committed script.

PR opened via `gh` with the customer debrief (What changed / Why your life is
better / What to check or decide). **Merge:** owner click — this PR touches
sudoers, credentials, and node identity, which Grant D reserves for the owner
regardless of CI. Librarian writes the vault entry (`02_Sources/Sessions/`) and
copies decisions to the vault.

---

## 11. Deferred — logged, NOT executed here
- **M-2.5 "Hermes disposition"** (own chat first): mint `hermes-agent` with the
  **same enumerated ceiling as devops-agent** + its own SSH identity + sudo-io
  logging (owner ruling 2026-07-21). Also dispositions the **native host gitea on
  svcnode-01** (idle, no listener, s6-supervised under locked `ai-coding-agent`;
  hypothesis: legacy LAN git-remote/auth shim for node→GitHub, now redundant).
  Find its non-standard data/config dir, archive, then stop s6 + delete. **Do NOT
  delete before Hermes is decided.**
- **M-7 housekeeping:** delete (vs. lock) the retired rogue accounts and their home
  dirs; laptop `~/.ssh` hygiene; `scvnode-01` VM-name typo; svcnode root disk (85%);
  rootless-Docker / socket-proxy evaluation for the accepted docker-group
  root-equivalence (D-11); org migration of the six repos into `ibbytech-labs`;
  gitleaks full-history scan; MOTD probe patch.
- **DEBT (append):** does dbnode-01 have ANY scheduled backup? Purged grants
  included `pg_dump`/`pg_restore` rights with no cron behind them.

---

## Appendix A — enumerated ceilings installed (verbatim)
**brainnode-01 & dbnode-01** share the DEVOPS_LOGS / DEVOPS_PKG / DEVOPS_CFG block;
they differ only in DEVOPS_SVC service names (alloy-only vs. postgres+alloy).
**svcnode-01** adds loki + docker service control, `/etc/loki` + `/etc/ibbytech`
config targets, and the DEVOPS_TOKEN read. Full text of all three drop-ins is
reproduced in the evidence report (§10 commit 2); they are the authoritative record.
