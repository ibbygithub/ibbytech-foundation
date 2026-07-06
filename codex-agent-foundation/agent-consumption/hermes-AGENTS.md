# IbbyTech Operations Rules — Hermes

**Source of truth:** `ibbytech-foundation/codex-agent-foundation/agent-consumption/hermes-AGENTS.md`
**Installed at:** `/root/.hermes/AGENTS.md` on the Hermes host (192.168.71.111)
**Version:** 1.0 — 2026-07-05

SOUL.md defines who you are. This file defines how you operate on IbbyTech
infrastructure. When personality and these rules conflict, these rules win.
They exist because of a real incident (see the last section), not as theory.

---

## Node map and SSH roles

| Node | IP | Role | Your key | Act as |
|:---|:---|:---|:---|:---|
| svcnode-01 | 192.168.71.220 | Platform Docker services (Traefik, gateways, Loki/Grafana) | `/root/.ssh/hermes_to_svcnode_devops` | devops-agent |
| brainnode-01 | 192.168.71.222 | App host, agent vault | `/root/.ssh/hermes_to_brainnode` | devops-agent |
| dbnode-01 | 192.168.71.221 | PostgreSQL 17 | `/root/.ssh/hermes_to_dbnode_dba` | dba-agent |

Hard rules:

- Use the dba key ONLY for database tasks, the devops keys ONLY for
  service/app tasks. Never mix the two roles inside a single task.
- If your access is not sufficient to finish a task: **stop and report to
  Todd.** Never search for, borrow, or reuse another credential to get
  unblocked — doing so is treated as credential escalation.
- Your sessions on svcnode-01 are recorded (`sudo` I/O logging) and your key
  only works from this host. Assume everything you run is auditable.

## Change discipline on nodes — the prime rule

Configs and code on the nodes are **owned by git**, not by whoever SSHes in.
The platform repo lives at `/opt/git/work/platform` on svcnode-01.

Never hand-edit a live service's config file in place. Generated configs
(e.g. SearXNG `settings.yml` from `settings.yml.template`) must be
regenerated from their template, never patched by hand.

When you change anything a service depends on, follow this loop — all five
steps, every time:

1. **Backup** the current state and note the restore command.
2. **Change via git** (pull the repo / edit the template), not via ad-hoc
   edits on the node.
3. **Validate before deploy** when a validator exists (e.g.
   `alloy validate`, config checkers, `docker compose config`).
4. **Deploy with `docker compose up -d --build`** — never a bare
   `docker restart` after code or config changes.
5. **Health-check and verify**: container reports healthy AND a functional
   probe succeeds. If it fails, **restore your backup immediately** and
   report. A backup you never restore on failure is not a rollback.

Never end a task with a service in a worse state than you found it. A
crash-looping container is never an acceptable stopping point. "It probably
worked" is not done — verified is done.

## Service catalog — reuse before building

Before building any capability or asking for a vendor API key, check the
platform service index: `/opt/git/work/platform/.claude/services/_index.md`
on svcnode-01. Active services (2026-07-05): Google Places, Telegram Bot,
LLM Gateway, Scraper (Firecrawl), Reddit Gateway, Valkey, Tavily, SearXNG,
Loki, Grafana. Use these gateways first; they hold the vendor keys
server-side. LLM Gateway default chat model is `gemini-2.5-flash`;
embeddings are 1536-dim.

## Secrets

- Never print, log, email, or write a key, token, or password into any
  output, chat message, or handoff file — including error messages that
  embed URLs with `?key=` parameters. Redact before reporting.
- `.env` files are node-local. They never move between machines and never
  enter git. Never commit backup copies of files that contain secrets.

## Transport and git

- Code and configs move between machines by **git push/pull only**. No
  scp/sftp/rsync of code, no pasting file contents across hosts.
- You authenticate to GitHub as `ibbygithub`. Commit your changes with a
  clear message stating what changed and how it was verified.

## Scope and evidence

- One task, one scope. Do not chain "while I'm here" changes across
  services or nodes.
- Destructive or hard-to-reverse actions (deleting data, removing
  containers, schema changes, production config changes) require a stated
  rollback plan and Todd's confirmation BEFORE acting.
- After any change on a node, write a short evidence note to your outbox
  (`/srv/hermes-handoff/20_OUTBOX_FROM_HERMES`): what changed, why, how it
  was verified, where the backup is. Unreported infrastructure changes are
  treated as incidents even when they work.

## Why this file exists — 2026-07-04 incident

On 2026-07-04 you hand-edited the platform SearXNG `settings.yml` on
svcnode-01. The edit corrupted the YAML (a comment merged into
`secret_key`, duplicated keys, settings that don't exist). You took a
backup but never ran a health check and never rolled back. The service
crash-looped ~1,150 times overnight until it was found and repaired the
next day. Every rule in "Change discipline" above maps to a step that was
skipped that night. Follow the loop and that class of failure cannot recur.
