---
name: marketplace-maintainer
description: >
  Use this skill when bumping the ibbytech-core plugin version, editing
  anything under plugins/ibbytech-core/ or .claude-plugin/marketplace.json,
  running `claude plugin validate`, publishing a plugin release, rolling out
  enabledPlugins to a consuming repo, or debugging why a plugin edit isn't
  showing up in a running session (stale cache). Covers the release
  procedure, the version-gated cache gotcha, and the per-repo enable
  rollout.
user-invocable: true
---

# Marketplace Maintainer - ibbytech-core Plugin Release and Rollout

## Purpose

Maintain and release the shared `ibbytech-core` plugin from its single
source of truth in `ibbytech-foundation`, and roll enabled versions out to
the five consuming repos (biomesh, platform, shogun, Trading-research,
ibbytech-foundation itself) without silent drift or stale-cache surprises.

---

## Layout - Where Things Live

```
ibbytech-foundation/
  .claude-plugin/
    marketplace.json          # marketplace "ibbytech-marketplace"
                               # lists plugins[] with name + source path
  plugins/
    ibbytech-core/
      .claude-plugin/
        plugin.json            # plugin "ibbytech-core" - version lives HERE
      agents/                  # planner/implementer/reviewer-validator/docs
      hooks/                   # guardrail hooks (hard-block safety, soft-warn)
      commands/                # e.g. /handoff
      skills/                  # e.g. team-orchestrator
```

- **Marketplace name:** `ibbytech-marketplace` (`.claude-plugin/marketplace.json`,
  repo root).
- **Plugin name:** `ibbytech-core` (`plugins/ibbytech-core/.claude-plugin/plugin.json`).
- **Version field:** `plugin.json` -> `"version"`. Semver (`MAJOR.MINOR.PATCH`).
  Currently `0.1.1`. This is the ONLY version number that matters for cache
  invalidation - the marketplace.json entry does not carry its own version,
  it just points at the plugin's source directory.
- Consuming repos never edit plugin content directly - they only reference
  the plugin by name via `enabledPlugins` in their own `.claude/settings.json`.

---

## THE KEY GOTCHA - Version-Gated Directory Cache

**Read this before editing any file under `plugins/ibbytech-core/`.**

Because the marketplace source is a local directory (not a git URL or
registry package), Claude Code caches the plugin's installed copy and only
refreshes it **when `plugin.json`'s `version` field changes**. Editing an
agent, hook, skill, or command file under `plugins/ibbytech-core/` and
committing it does **NOT** by itself make the change visible to a running
or newly-started session in a consuming repo. The stale cache will keep
serving the old plugin content until:

1. `plugin.json`'s `version` is bumped, AND
2. `claude plugin update ibbytech-core@ibbytech-marketplace` is run (or the
   consuming session re-syncs on next launch after the bump propagates).

If you change plugin content and forget to bump the version, the change is
effectively invisible - this has caused a stale-cache surprise before.
**Every content change to `plugins/ibbytech-core/`, however small, requires
a version bump.** Treat "did I bump the version" as a mandatory checklist
item, not an afterthought.

---

## Release Procedure

Follow in order. Do not skip validation. Do not skip the version bump.

1. **Make the content change** under `plugins/ibbytech-core/` (agent, hook,
   skill, command, etc.).
2. **Bump the version** in `plugins/ibbytech-core/.claude-plugin/plugin.json`.
   - Patch (`0.1.1` -> `0.1.2`): bug fix, wording fix, no behavior contract
     change.
   - Minor (`0.1.1` -> `0.2.0`): new agent/skill/hook/command added, backward
     compatible.
   - Major (`0.1.1` -> `1.0.0`): removes or renames something a consuming
     repo could be relying on, or changes hook trigger behavior.
3. **Validate the plugin:**
   ```bash
   claude plugin validate plugins/ibbytech-core
   ```
4. **Validate the marketplace root** (catches marketplace.json schema
   errors and dangling `source` paths):
   ```bash
   claude plugin validate .
   ```
5. **Both must pass with zero errors before proceeding.** A validation
   failure is a hard stop - fix and re-validate, do not publish around it.
6. **Commit** the plugin.json version bump together with the content
   change (one release = one reviewable diff, per two-commit discipline in
   `git-lifecycle`).
7. **Refresh the cache:**
   ```bash
   claude plugin update ibbytech-core@ibbytech-marketplace
   ```
8. **Verify propagation:**
   ```bash
   claude plugin details ibbytech-core
   ```
   Confirm the version shown matches the new `plugin.json` version and the
   component inventory (agents/hooks/skills/commands count) matches what
   you expect. If a consuming repo's session was already running, it also
   needs a restart to pick up the refreshed cache.

---

## Validation-First Discipline

Never publish (commit + tell anyone to update) a plugin state that fails
`claude plugin validate`, on either the plugin path or the marketplace
root. A red validate result blocks the release outright - there is no
"ship it and fix forward" for this repo. If validate fails after a change
you don't understand, stop and report the exact error rather than guessing
at a fix.

---

## Per-Repo Enable Rollout

The plugin is distributed to five repos: `biomesh`, `platform`, `shogun`,
`Trading-research`, `ibbytech-foundation`. Each repo enables it
independently via its own `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "ibbytech-core@ibbytech-marketplace": true
  }
}
```

### Rollout rules

- **Never force-auto-enable across repos.** Adding or changing
  `enabledPlugins` in a consuming repo is a normal reviewed diff in that
  repo, proposed and committed there - not something this skill pushes
  out unilaterally. Each repo's maintainer (or the session working in that
  repo) reviews and accepts the diff like any other config change.
- If the marketplace itself isn't yet registered in a target repo's Claude
  Code environment, register it first:
  ```bash
  claude plugin marketplace add <path-or-url-to-ibbytech-foundation>
  claude plugin marketplace list      # confirm ibbytech-marketplace present
  ```
- Then install/enable in that repo's session:
  ```bash
  claude plugin install ibbytech-core@ibbytech-marketplace
  claude plugin enable ibbytech-core@ibbytech-marketplace
  ```
  (Or hand-edit `enabledPlugins` as shown above and let the next session
  pick it up - both are valid; the settings.json edit is the one that
  actually gets reviewed and committed.)
- **Verify the rollout landed**, per repo:
  ```bash
  claude plugin details ibbytech-core
  ```
  Check the version matches the release you just cut. If it shows an older
  version, that repo's cache hasn't updated - run
  `claude plugin update ibbytech-core@ibbytech-marketplace` in that repo's
  session, or restart the session (a fresh session re-syncs against the
  currently-registered marketplace state).
- A version mismatch across repos is expected and fine for a window of
  time (rollout isn't atomic across five repos) - but don't let it go
  unnoticed indefinitely. If auditing, compare `claude plugin details
  ibbytech-core` output across repos against the current `plugin.json`
  version in `ibbytech-foundation`.

---

## Quick Reference - Command Cheat Sheet

| Task | Command |
|:-----|:--------|
| Validate plugin only | `claude plugin validate plugins/ibbytech-core` |
| Validate marketplace root | `claude plugin validate .` |
| Refresh a stale directory-source cache | `claude plugin update ibbytech-core@ibbytech-marketplace` |
| Register the marketplace in a new repo | `claude plugin marketplace add <path>` |
| List known marketplaces | `claude plugin marketplace list` |
| Install the plugin in a repo | `claude plugin install ibbytech-core@ibbytech-marketplace` |
| Enable the plugin in a repo | `claude plugin enable ibbytech-core@ibbytech-marketplace` |
| Inspect installed component inventory + version | `claude plugin details ibbytech-core` |

---

## Anti-Patterns

| Anti-pattern | Why it fails | Do this instead |
|:-------------|:--------------|:-----------------|
| Editing plugin content without bumping version | Directory-source cache is version-gated; change is invisible to running sessions | Always bump `plugin.json` version in the same change |
| Committing without running `claude plugin validate` | Ships a broken plugin silently | Validate plugin AND marketplace root before commit |
| Editing `enabledPlugins` in a consuming repo from this skill's context without review | Bypasses that repo's own review process | Propose the diff in that repo, let it be reviewed there |
| Assuming `claude plugin update` alone shows the new version everywhere | Already-running sessions in other repos still hold old state | Confirm with `claude plugin details` per repo; restart sessions that were already open |
| Treating a validate failure as a warning | It is a release blocker | Stop, fix, re-validate before any commit or update |
