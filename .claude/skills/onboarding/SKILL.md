---
name: onboarding
description: >
  Use this skill when bringing a new repo onto the IbbyTech Claude Code
  framework for the first time, when starting a fresh session and needing
  project context fast without hand-pasting a context blob, when a repo is
  missing a CLAUDE.md or has one that's gone stale, or when deciding what a
  new session should read first (CLAUDE.md, memory, latest handoff note).
  Replaces the manual "/clear then paste 40 lines of context" pattern.
user-invocable: true
---

# Onboarding - Bring a Repo or a Session Onto the Framework

## Purpose

Two distinct onboarding problems, both solved by pointing at existing
structure instead of re-explaining it by hand each time:

1. **New-repo onboarding** - a repo has no `ibbytech-core` plugin enabled
   and no (or a stale) `CLAUDE.md`.
2. **New-session onboarding** - the repo is already set up; a fresh session
   just needs to load context fast.

Do not conflate them. A repo only goes through step 1 once (plus occasional
`CLAUDE.md` maintenance). Every session goes through step 2.

---

## Framework Layering - What "Onboarded" Means

```
Shared layer   ibbytech-core plugin (from ibbytech-marketplace)
               agents/ (planner, implementer, reviewer-validator, docs)
               hooks/  (guardrail hard-block + soft-warn)
               commands/ (e.g. /handoff)
               skills/ (e.g. team-orchestrator)
               -- same for every repo, maintained centrally --

Repo layer     CLAUDE.md + .claude/rules/ + .claude/skills/
               -- specific to this repo's purpose, topology, agreements --

Session layer  memory + outputs/work-log/ handoff notes
               -- specific to this moment in this repo's history --
```

A repo is "onboarded" when the shared layer is enabled AND the repo layer
exists and reflects reality. A session is "oriented" when it has read repo
layer + the most recent session layer artifact, without needing a human to
paste anything.

For plugin release/version mechanics themselves (validate, bump, cache
gotcha), that is the `marketplace-maintainer` skill's job, not this one -
this skill only covers *enabling* the plugin in a new repo, not maintaining
it.

---

## New-Repo Onboarding

### Step 1 - Enable the shared plugin

1. Check whether the marketplace is already registered for this repo's
   Claude Code environment:
   ```bash
   claude plugin marketplace list
   ```
   If `ibbytech-marketplace` is missing:
   ```bash
   claude plugin marketplace add <path-or-url-to-ibbytech-foundation>
   ```
2. Check the repo's `.claude/settings.json` for `enabledPlugins`. If absent
   or `false`, propose adding:
   ```json
   {
     "enabledPlugins": {
       "ibbytech-core@ibbytech-marketplace": true
     }
   }
   ```
   This is a normal reviewed diff in the target repo - write it, show it,
   do not silently auto-enable across repos you weren't asked to touch.
3. Verify with:
   ```bash
   claude plugin details ibbytech-core
   ```
   and by restarting the session (a fresh session picks up the newly
   enabled plugin; a session already running before the settings.json edit
   will not see it until restarted).

### Step 2 - Generate or repair the repo's CLAUDE.md

A good `CLAUDE.md` for this framework has these sections (model the shape,
don't copy text, from `biomesh/CLAUDE.md` and `Trading-research/CLAUDE.md`
- both are strong existing examples with different projects behind them):

| Section | Purpose | Example from the models |
|:--------|:--------|:-------------------------|
| **Project purpose / identity** | One paragraph: what this repo is, who it's for | Trading-research opens with what the lab is and who "the human" is |
| **Topology / paths** | Physical or logical layout the agent must respect | biomesh's node table (dbnode-01/svcnode-01/brainnode-01) and hard placement policy |
| **Stack / conventions** | Mandatory language, tooling, formatting choices, with "no alternative without an explicit decision recorded here" | biomesh section 3 (Technology Stack); Trading-research's Conventions section |
| **Working agreements** | How autonomous execution is scoped and validated - commit discipline, completion conditions | biomesh section 7; Trading-research's "Operating contract" |
| **Scope boundaries** | What's explicitly out of scope / deferred, and what NOT to do without asking | biomesh section 1 ("Out of scope for Phase 1") |
| **Session work logs** | Where/when to write handoff notes | Trading-research's "Session work logs" section, pointing at `outputs/work-log/` |
| **Open items** | Unresolved decisions, so the next session doesn't silently assume | biomesh section 8 |

When generating a starting `CLAUDE.md` for a new repo, draft each section
from that repo's actual purpose and layout - interview the person setting
it up (or infer from existing code) rather than inventing plausible-
sounding infrastructure. An empty or speculative section is worse than an
honest "not yet decided" placeholder (see biomesh's "Open Items" pattern).

If a `CLAUDE.md` already exists but is stale (infrastructure claims that no
longer match reality, missing a section from the table above), propose a
targeted diff to the specific stale section - do not rewrite the whole file
for a partial staleness issue (same discipline as `documentation-standard`'s
service-doc update rule).

---

## New-Session Onboarding

Goal: a fresh session gets oriented without a human hand-pasting a context
blob. Read, in this order:

1. **Repo `CLAUDE.md`** (root of the repo) - purpose, topology, standing
   rules. This is always-relevant and cheap to read in full.
2. **Any persisted memory** for the repo/session (MCP memory graph entities,
   or a project's own `.claude/rules/*.md` persona files that always-load)
   - if the repo uses either mechanism, load it before doing anything else.
3. **The latest handoff note** under `outputs/work-log/` - sort by
   filename (`YYYY-MM-DD-HH-MM-summary.md`) and read the newest one. This
   is written by the shared `handoff` command / `handoff_writer` Stop hook
   from `ibbytech-core`, and tells you: what was done last session, what
   files changed, decisions made, open items, and the concrete next step.
   Do not skip straight to "what do you want me to do" if a handoff note
   exists - read it first, then confirm scope with the human.
4. Only if a handoff note is absent or clearly stale (its "next session
   start point" no longer matches repo state), fall back to a quick
   `git log --oneline -10` and `git status` to reconstruct where things
   stand, and say so explicitly rather than pretending the handoff note
   was current.

### What this replaces

The old pattern - `/clear`, then a human pastes a 40-line context blob
every session - existed because there was no cheap way to reconstruct
state. With `CLAUDE.md` (repo layer) plus `outputs/work-log/` handoff notes
(session layer) both being maintained as standing artifacts, a session can
self-orient by reading three things instead of waiting on a human transcript
dump. If a repo doesn't yet have handoff notes flowing (no `outputs/work-log/`
activity, no Stop hook configured), that's a signal to run new-repo
onboarding's plugin-enable step, since `handoff_writer` ships with
`ibbytech-core`.

---

## Anti-Patterns

| Anti-pattern | Why it fails | Do this instead |
|:-------------|:--------------|:-----------------|
| Auto-enabling the plugin in a repo without showing the settings.json diff | Bypasses that repo's review process | Propose the diff, let it be reviewed and committed in that repo |
| Copying biomesh's or Trading-research's `CLAUDE.md` text into a new repo | Produces speculative, wrong-for-this-project content | Use the section table as a shape, draft content from this repo's actual facts |
| Skipping the handoff note and asking the human to re-explain state | Defeats the purpose of writing handoff notes at all | Read the latest `outputs/work-log/` note first |
| Rewriting an entire stale `CLAUDE.md` for one outdated section | Loses accumulated accurate context, risks introducing new errors | Patch only the stale section, per `documentation-standard` discipline |
| Treating "onboarded" as a one-time checkbox | Repo layer drifts (topology changes, new services) | Re-run the CLAUDE.md repair check whenever infra/architecture changes land |
