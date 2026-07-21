# Decisions Register
| # | Date | Decision |
|---|------|----------|
| 1 | 2026-07-19 | Grant A: scoped sudo for devops-agent on all three nodes (see Master Plan §2). |
| 2 | 2026-07-19 | Grant B: GitHub machine account ibbytech-agent + organization (try "ibbytech", fallback "ibbytech-labs"); new projects created in org, private by default; six existing repos stay put for now. |
| 3 | 2026-07-19 | Grant C: Forgejo admin API token, node-side storage only, agent-managed mirrors. |
| 4 | 2026-07-19 | Grant D: auto-merge on green for low-risk repos; owner merge retained for infra/credentials/deviations. |
| 5 | 2026-07-19 | Forgejo data volume on svcnode-01 local disk, never NFS/SMB. |
| 6 | 2026-07-19 | Forgejo 15.x accepted over spec'd 13.x (EOL at deploy). |
| 7 | 2026-07-18 | Handoffs, decisions, and rulings live in git; chat sessions read from repo. |
# DECISIONS.md — entries to APPEND (do not overwrite the existing 7)

> These continue the register created in the plan-persist mission. The librarian
> appends them; numbering picks up after the last existing entry. Each is a
> ruling made 2026-07-21 during the M-2 root-of-trust ceremony.

---

### D-8 — One enumerated identity per node
**Ruling:** every node in the estate carries exactly one sanctioned OS identity,
`devops-agent`, whose sudo authority is an **enumerated ceiling** in
`/etc/sudoers.d/devops-agent` (systemctl for named services, journalctl, package
queries, install/cp into named config dirs). No account is in the `sudo` group.
No `(ALL:ALL) ALL`. Escalation is a sudoers-amendment PR, never improvisation.
**Why:** an agent that can do "its job AND anything else" is not scoped; the
ceiling, not the floor, is the control.
**Evidence:** three nodes reconciled 2026-07-21; brainnode-01 live-fire proof.

### D-9 — Sudoers reconciliation is a permanent M-class gate
**Ruling:** enumerate `/etc/sudoers.d/`, check `sudo`-group membership, purge every
unsanctioned agent (de-sudo, remove drop-in, `usermod -L`, nologin), and assert the
single-identity end state — on every node this framework touches, forever, as a
mandatory verification. **Why:** the framework's first contact with three nodes
found undocumented standing root on all three; this gate is how that class of debt
stops recurring. **Origin:** a routine verification step caught `(ALL:ALL) ALL` on
node one; the gate generalizes that catch.

### D-10 — Rogue agent accounts: locked now, deleted in M-7
**Ruling:** unsanctioned agent accounts (`sysadmin-agent`, `ai-coding-agent` and its
underscore variant, `dba-agent`, `ai-coding-agent-dba`, `dba-agent-postgres`) are
**locked + nologin + de-sudoed + de-dockered** now; account/home deletion is
deferred to the M-7 housekeeping sweep. **Why:** locking is instant and fully
neuters privilege; deletion is irreversible and deserves a deliberate pass (home
dirs may hold keys/config worth reading first). Neutered-but-present preserves
forensic value at zero risk.

### D-11 — Docker-group membership on svcnode-01 is accepted root-equivalence
**Ruling:** `devops-agent` remains in the `docker` group on **svcnode-01 only**.
Docker-socket access is root-equivalent (`docker run -v /:/host --privileged`
escapes any sudoers enumeration), so this is an explicitly **accepted** grant, named
here rather than hidden behind a sudoers file that would imply false containment.
On svcnode the platform *is* Docker; service management is the agent's function.
**Revisit:** rootless Docker / socket-proxy evaluation in M-7. **Why documented:**
a named, owned risk is managed; an unnamed one is how you lose the plot.

### D-12 — Sudo I/O session logging on all nodes
**Ruling:** `Defaults:devops-agent log_output` (and for `hermes-agent` when it
exists), with `sudoreplay`/`visudo` exempted, on all three nodes → full replayable
capture in `/var/log/sudo-io/`. **Why:** keystroke-level evidence of autonomous
agent actions is exactly what review requires; the original svcnode operator had
this right and it must not regress. **Note:** a rewrite briefly dropped it; caught
and restored the same session.

### D-13 — Hermes becomes a governed second identity (`hermes-agent`)
**Ruling:** Hermes (AI agent on the Hermes node, ~192.168.71.111, historically
reaching brainnode-01/svcnode-01 via shared root accounts) will be sanctioned with
its own `hermes-agent` OS identity carrying the **same enumerated ceiling as
devops-agent**, its own SSH key, and its own sudo-io logging — NOT shared roots,
NOT full root. Executed as a dedicated mission **M-2.5** (designed in chat first).
**Interim:** the shared roots Hermes borrowed are already locked; some Hermes
function may be interrupted until M-2.5 mints its identity — watch for fallout.
**Why:** a second working agent is legitimate; a second *rogue* agent is the debt
the framework exists to collapse. Governance, not eviction.

### D-14 — Native host gitea on svcnode-01: tagged for review, not deleted
**Ruling:** the host-native `gitea web` on svcnode-01 (s6-supervised under the now-
locked `ai-coding-agent`; **no listener**, no standard `app.ini`, sparse data) is
**left running and tagged for M-2.5 review**, not killed. Hypothesis (owner): a
legacy LAN git-remote / auth shim for node→GitHub authentication failures during
Actions, predating the machine account and `platform-forgejo` — i.e. likely made
redundant by M-2. **Disposition:** in M-2.5, locate its non-standard data/config,
confirm nothing depends on it, archive, then stop s6 + delete. **Why not now:**
deliberately-built + Hermes-adjacent; deleting on a hunch could remove a push target
something quietly depends on.

### D-15 — Machine-user model for GitHub (account key, not deploy keys)
**Ruling:** GitHub access from the node is via the **`ibbytech-agent` machine
account** authenticating with a single account-level SSH key
(`~/.ssh/ibbytech-agent_ed25519`, generated on brainnode-01), holding **Write**
collaborator access on the six framework repos. The six per-repo read-only deploy
keys retire once the account key's push is proven (M-2 Phase D). Org landed as
**`ibbytech-labs`** (`ibbytech` was taken). **Why:** one identity replacing six
per-repo keys is the whole point of a machine account; deploy-key deletion is
gated behind proven replacement so no access gap opens.

