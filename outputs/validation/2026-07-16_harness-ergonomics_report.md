# Evidence Report — Harness Ergonomics Micro-Mission

**Date:** 2026-07-16
**Branch:** fix/harness-ergonomics
**Task:** Add routine gh CLI operations to the permission allowlist (with owner-only merge and no-delete denies), set `defaultMode: acceptEdits` in the live settings, and codify the Mission Debrief Standard in `.claude/CLAUDE.md` — landing per two-commit discipline with the PR description as the debrief format's first demonstration.
**Node(s):** laptop only
**Persona(s):** none (laptop-local)

---

## Objective

Reduce permission-prompt friction for the GitHub operations every mission uses (PR creation, status reads) without widening anything write-shaped: merges stay owner-only, repo deletion and DELETE-method API calls are denied outright, and file edits stop prompting via `acceptEdits` while non-allowlisted commands still gate. Separately, make the three-part customer debrief — first used ad hoc at the close of Phase 2A — a written standard so mission completion always includes one.

---

## Actions Taken

### 1. gh CLI permission entries (both settings files)

Added to `.claude/settings.json` and `templates/settings-baseline.json` identically (9 allows, 6 denies):

**Allow:** `gh auth status` (exact), `gh pr create*`, `gh pr view*`, `gh pr list*`, `gh pr diff*`, `gh repo view*`, `gh api -X GET *`, `gh api --method GET *`, `gh api --method=GET *`.

**Deny:** `gh repo delete*`, `gh pr merge*`, and `gh api *-X*DELETE*` / `*-X*delete*` / `*--method*DELETE*` / `*--method*delete*`.

Design decisions:
- **`gh auth status` has no wildcard** — `gh auth status --show-token` prints the live OAuth token to the terminal; the starred form would have auto-allowed it. Redirect-suffixed variants (`2>&1`) now prompt instead; accepted cost.
- **`gh api` GET allows require the method flag explicitly.** A bare `gh api <endpoint>` is only GET until a `-f`/`-F` field flag is present, at which point gh silently switches to POST — a prefix glob cannot distinguish the two, so "read-only GET" is only true when the method is stated. Bare `gh api` calls prompt.
- **DELETE denies use collapsed wildcards** (`gh api *-X*DELETE*` etc.) so `-X DELETE`, `-XDELETE`, `--method DELETE`, and `--method=DELETE` are all caught at any argument position, upper- or lowercase. Over-matching on the deny side is the safe direction.
- **`gh pr merge*` denied outright**, per the mission's "merges are owner-only." This is stricter than Doctrine v2's "agent merges on explicit instruction" — see What to check or decide.

### 2. Mission Debrief Standard (`.claude/CLAUDE.md`)

New section inserted after Communication Standards: every mission concludes with a plain-language debrief for the repo owner as customer, exactly three parts (What changed / Why your life is better / What to check or decide), posted as the PR description and mirrored at the end of the evidence artifact; a terse changelog alone does not satisfy mission completion.

### 3. `defaultMode: acceptEdits` (live settings only)

Set in `.claude/settings.json` `permissions` block. Deliberately **not** added to the baseline template: the mission's Task 1 names both files while Task 3 names only `.claude/settings.json`, so the template continues to leave mode choice to each instantiating repo.

### 4. Landing

Two logical commits per Doctrine v2 Rule 3: `1811ac3` (implementation — 3 files) and this evidence commit. PR opened `fix/harness-ergonomics` → `main` with the description in debrief format; left open for owner review (and the agent can no longer merge it anyway — see denies above).

---

## Verification

```
settings.json PARSE: OK
defaultMode: acceptEdits
allow: 146  deny: 125
baseline PARSE: OK
baseline defaultMode: '' (expected empty)
baseline allow: 146  deny: 125
gh allow entries: 9   (auth status, pr create/view/list/diff, repo view, 3 GET-api forms)
gh deny entries: 6    (repo delete, pr merge, 4 DELETE-api forms)
```

Debrief standard present: `grep -n "Mission Debrief Standard" .claude/CLAUDE.md` → section at the expected location, three parts enumerated. Branch naming `fix/harness-ergonomics` is Doctrine v2-compliant (`fix/<name>`, date optional). PR URL recorded in the session transcript and on the PR itself.

---

## Green Gate Checklist

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Validate PASS | SKIP (non-service task; JSON parse verification above) |
| 2 | Loki Level 1 | SKIP (non-service task) |
| 3 | OpenAPI spec | SKIP (non-service task) |
| 4 | Capability registry | SKIP (non-service task) |
| 5 | _index.md | SKIP (non-service task) |
| 6 | Evidence report | PASS — this file |
| 7 | .env.example | SKIP (no env vars involved) |

---

## Outcome

**COMPLETE** — gh allowlist live in both files, denies in place, acceptEdits active, debrief standard codified, PR open with the standard's first demonstration as its description.

---

## Mission Debrief (mirrored from the PR description, per the new standard)

### What changed

Routine GitHub work — opening PRs, checking their status, reading diffs — no longer trips permission prompts, while the dangerous end of the gh CLI got locked instead of loosened: the agent now *cannot* merge a PR, delete the repo, or fire DELETE API calls, even if asked. File edits auto-accept; anything off the allowlist still prompts. And the three-part customer debrief you got at the end of Phase 2A is now the written standard for how every mission ends — posted on the PR, mirrored in the evidence report.

### Why your life is better

Fewer interruptions for the operations that were always going to be approved anyway, with the merge button held back for you alone — the agent asking "may I run gh pr view" was noise; the agent being unable to merge is signal. Future missions also can't quietly end with a bare changelog: the debrief you're reading is now the contract, so you'll always get the judgment calls and open decisions surfaced instead of buried in commit messages.

### What to check or decide

1. **The `gh pr merge*` deny is stricter than Doctrine v2.** The doctrine allows agent merges "on explicit human instruction" (which is how PRs #4/#5 landed); the new deny blocks the command entirely, instruction or not. If you want to keep delegating merges the way you did today, either merge in the GitHub UI going forward or lift this one deny — as written, owner-only wins.
2. **`gh auth status` is exact-match on purpose** — the wildcard form would have auto-allowed `--show-token`, which prints your live token. If you see an occasional prompt on redirect-suffixed variants, that's the trade.
3. **Bare `gh api <endpoint>` still prompts** even for reads, because gh silently upgrades bare calls to POST when field flags appear; only explicit `-X GET` / `--method GET` forms are auto-allowed. Minor friction, deliberate.
4. **`acceptEdits` went into the live settings only, not the baseline template** — each repo instantiating the template still chooses its own mode. Copy it into the template too if you'd rather every repo inherit it.
