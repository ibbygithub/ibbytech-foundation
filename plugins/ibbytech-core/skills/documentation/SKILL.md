---
name: documentation
description: >
  When and how to update documentation — README files, PR descriptions,
  changelogs (Keep a Changelog), API docs, ADRs, and evidence-to-documentation
  flow. Use this skill when creating or updating documentation, writing a PR
  description, generating a changelog entry, or converting validation
  evidence into release notes.
user-invocable: true
---

# Documentation — When and How to Document

## Purpose

Prevent both under-documentation (missing context that blocks future agents) and
over-documentation (noise that buries signal). Every artifact must earn its
existence by answering a question someone will actually ask.

---

## README Files

### Triggers for README Update

- New feature that changes usage, new API endpoint or auth change
- New dependency, infrastructure requirement, or service
- Changed deployment procedure or environment variables

Does NOT trigger: internal refactoring, bug fixes (unless behavior changes),
test additions, evidence reports, planning documents.

### Service README — Required Sections

| Section | Required | Purpose |
|:--------|:---------|:--------|
| Title + one-line description | Always | What this is |
| Endpoints (FQDN table) | Always | How to reach it |
| Quick Start | Always | Copy-paste to get running |
| API (methods + examples) | Always | Every exposed HTTP endpoint |
| Environment Variables | If any | What to configure |
| Access Control | If applicable | Who can call it |

### Project README — Required Sections

| Section | Required | Purpose |
|:--------|:---------|:--------|
| Purpose | Always | What this project does and who it serves |
| Setup | Always | How to get a working dev environment |
| Usage | Always | How to run, deploy, or interact with it |
| Configuration | If applicable | Environment variables, config files |
| Dependencies | Always | Platform services, databases, tools needed |

### What Does NOT Belong in a README

Implementation details, debugging notes, meeting notes, decision history
(use ADRs), temporary workarounds (use TODO comments), or content duplicated
from CLAUDE.md or rules files.

---

## PR Description Format

Every PR must let a reviewer understand the change without reading every diff line.

```markdown
## Summary
[1-3 sentences: what changed and why. Lead with motivation, not mechanics.]

## Changes
- [Bulleted list of significant changes — files, features, fixes]

## Breaking Changes
[What breaks and what consumers must do. Omit section if none.]

## Test Plan
- [ ] [Specific verification steps, not "run tests"]

## Links
- Planning: [link to planning doc if one exists]
- Issue: [link to tracking issue if applicable]
- Evidence: [link to validation report if deployment involved]
```

**Quality rules:**
- Summary explains WHY, not just WHAT
- Breaking changes are never buried in the Changes list
- Test plan is actionable ("Send a message and verify response within 5s")
- Omit sections that do not apply — do not write "N/A"

This is the standard the `commit-push-pr` command uses when opening a PR.

---

## Changelog — Keep a Changelog Convention

```markdown
# Changelog

## [Unreleased]

### Added
- New search endpoint `/v1/items/search_text` (#42)

### Changed
- Default upstream model changed for cost/latency reasons

### Fixed
- Gateway no longer drops payloads over 10MB
```

| Category | When to use |
|:---------|:------------|
| Added | New feature, endpoint, service, or capability |
| Changed | Existing behavior modified (non-breaking) |
| Deprecated | Feature marked for future removal |
| Removed | Feature or endpoint deleted |
| Fixed | Bug fix |
| Security | Vulnerability fix, credential rotation, access change |

Update `[Unreleased]` with every PR that changes user-visible behavior.
Internal refactoring and test-only PRs do not need entries. When cutting
a release, move items under a versioned heading: `## [1.2.0] - YYYY-MM-DD`.

---

## API Documentation

Update when: endpoint added/removed/renamed, request/response schema changed,
auth method changed, new error codes, or rate limiting changed.

Per endpoint, always document: HTTP method + path, request body with example,
response schema with example, error responses (minimum 400, 404, 500), and
authentication requirements. For services with an OpenAPI spec, keep the
repo spec synchronized rather than letting docs drift from the schema.

---

## Evidence-to-Documentation Flow

Evidence reports (validation/build output, test runs) are audit artifacts
for traceability. They are NOT documentation. Do not link them from READMEs,
do not restructure them into tutorials, do not delete them after extracting
information.

### Evidence to Documentation Mapping

| Evidence contains... | Update... |
|:---------------------|:----------|
| New service deployed | Create service README + service doc |
| API endpoint changed | API docs and OpenAPI spec |
| Infrastructure state changed | CLAUDE.md "Known Infrastructure State" |
| New env var required | README, `.env.example`, service doc |
| Service decommissioned | Mark service doc deprecated, update service index |

### Planning to Documentation Mapping

| Planning contains... | Update... |
|:---------------------|:----------|
| Approved architecture decision | Create ADR |
| Technology choice rationale | CLAUDE.md "Technology Registry" |
| Open question resolved | CLAUDE.md "Open Architecture Decisions" |
| New service designed | Nothing yet — wait for deployment evidence |

---

## Code Comment Standards

**Comment WHY, not WHAT.**

```python
# Good: this provider requires the system prompt as the first message,
# not a separate parameter — this reshaping handles that difference.
messages = [{"role": "system", "content": system_prompt}] + messages

# Bad: Prepend system prompt to messages
messages = [{"role": "system", "content": system_prompt}] + messages
```

**Required:** non-obvious business logic, upstream bug workarounds, known
limitations, TODO items with task references.

**Forbidden:** restating what code says (`# increment counter` above
`counter += 1`), commented-out code kept "just in case", explaining
standard library usage any developer would know.

---

## Architecture Decision Records (ADR)

Create when: choosing a technology over alternatives, making a design decision
that constrains future work, or reversing a prior decision.

```markdown
# ADR: [Title — the decision, not the question]
**Date:** YYYY-MM-DD
**Status:** Accepted / Superseded by [ADR link]

## Context
[What problem prompted this. Include constraints.]

## Decision
[What was decided. Name the technology, pattern, or approach.]

## Consequences
[Positive and negative. What becomes easier? Harder? Ruled out?]
```

Store ADRs under a project's planning/decision output location as
`adr-YYYYMMDD-<slug>.md`. ADRs are never deleted — superseded ones get a
status update and link to the replacement.

---

## Service Documentation Lifecycle

**Create** (new service deployed) — required artifacts:
1. Service doc under the repo's service-docs location
2. OpenAPI spec (if HTTP service)
3. Validation script or equivalent smoke check
4. Index entry in the service catalog
5. Service README

**Update** (behavior or config changed) — update only the section that
changed, update "Last Updated" in service doc, update OpenAPI if endpoints
changed. Do not rewrite the entire doc for a minor change.

**Deprecate** (being replaced) — add deprecation notice at top of service doc
and README: `> **DEPRECATED:** Replaced by [X]. Removal planned [date].`
Keep doc intact for migration. Update the service index.

**Decommission** (removed) — move service doc to an archive section in the
service index (do not delete). Remove from active routing and README lists.
Write evidence documenting the removal.

---

## CLAUDE.md Conventions

**Belongs in CLAUDE.md:** project identity, platform services consumed (FQDNs),
database routing, known infrastructure state (verified facts with dates),
open architecture decisions, technology registry, project-specific rules.

**Does NOT belong:** shared foundation rules (live in the shared rules/plugin
source), skill definitions (live in `skills/`), how-to guides (README or
docs/), temporary state (planning docs or evidence reports), implementation
details.

**When to update:** infrastructure change verified, platform service added or
removed, architecture decision resolved, technology registry changed, database
routing changed. Update the specific section — include verification date on
state changes. Never remove "Known Infrastructure State" entries without
verifying the new state first.

---

## Anti-Patterns

| Anti-pattern | Why it fails | Do this instead |
|:-------------|:-------------|:----------------|
| Document everything | Noise buries signal | Document decisions and interfaces |
| README as tutorial | Grows stale, duplicates code | Setup + usage only |
| Evidence as docs | Audit artifacts are not guides | Extract facts into proper docs |
| Copy-paste between docs | Diverges immediately | Single source of truth, link to it |
| "Will document later" | Later never comes | Document at PR time or not at all |
| Commenting obvious code | Clutter, not clarity | Comment the why, not the what |
