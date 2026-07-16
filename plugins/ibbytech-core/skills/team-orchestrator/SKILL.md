---
name: team-orchestrator
description: >
  Use this skill when decomposing complex goals into multi-agent tasks,
  coordinating parallel work, managing agent handoffs, or planning team
  execution strategies. Knows the skills inventory and routes work to the
  right specialist agent. Essential for any task that spans multiple
  services, repos, or domains.
user-invocable: true
---

# Team Orchestrator — Multi-Agent Task Coordination

## Purpose

Turn a high-level goal into a coordinated execution plan across multiple
agents, each scoped to a specific concern with the right skill loaded.
Prevent agent thrashing, scope overlap, and cascading failures.

---

## Task Decomposition Patterns

### When to Parallelize

Agents can run in parallel when their work is **independent** — no shared
files, no dependency on each other's output.

**Good parallel candidates:**
- Frontend component work + backend API work (different file trees)
- Database schema research + UI design research (read-only, no writes)
- Multiple service investigations (each agent reads its own service)
- Test writing + documentation updates (non-overlapping files)

**Pattern:** Spawn agents simultaneously with `run_in_background: true`.
Each agent gets a clear scope declaration and returns a structured result.

### When to Sequence

Agents must run sequentially when there's a **dependency chain** — one
agent's output is another's input.

**Must-sequence examples:**
- Schema change → API endpoint → Frontend integration (each builds on prior)
- Plan → Implement → Review (decisions feed downstream — this is the
  `planner` → `implementer` → `reviewer-validator` chain used on this project)
- Build → Test → Deploy (each validates the prior step)

**Pattern:** Run agent 1, wait for result, validate, then spawn agent 2
with agent 1's output as context.

### Hybrid: Parallel with Sync Points

For complex tasks, use parallel execution with validation checkpoints:

```
Phase 1 (parallel):
  Agent A: Backend API changes
  Agent B: Database migration
  → Sync point: both complete, verify DB migration + API are compatible

Phase 2 (parallel):
  Agent C: Frontend integration (depends on Phase 1 API)
  Agent D: Test writing (depends on Phase 1 API)
  → Sync point: both complete, run tests

Phase 3 (sequential):
  reviewer-validator → docs (handoff note) → Merge Ready
```

---

## Agent Scoping Rules

Every agent task must declare its scope upfront. No exceptions.

### Scope Declaration Format

Before spawning an agent, state:
1. **What it will do** (one sentence)
2. **What files/directories it may modify** (explicit list)
3. **What skill(s) it should use** (from the inventory)
4. **What it returns** (expected output format)

### Hard Rules

- **One agent per concern.** Don't give one agent both "fix the API" and
  "update the UI" — split them.
- **No overlapping file scope.** If two agents might touch the same file,
  they cannot run in parallel. Sequence them or merge into one agent.
- **Declare skill assignments.** Each agent should be told which skill(s)
  to reference — e.g. an agent doing a release should be told to use the
  `git-discipline` skill.
- **Keep agents focused.** An agent that's doing 5+ things is too broad.
  Split it. 2-3 related actions per agent is the sweet spot.

---

## Dependency Management

### Blocking Dependencies

One task cannot start until another completes:
- Schema must exist before API can query it
- API must exist before frontend can call it
- Build must succeed before deploy
- A `planner` spec must exist before `implementer` starts

**Handling:** Run the blocking task first. Validate its result. Only then
spawn the dependent task with the prior result as context.

### Non-Blocking Dependencies

Tasks benefit from each other's output but can start independently:
- Frontend can start with mock data while backend builds the real API
- Tests can be written against the API contract before implementation
- Documentation can be drafted alongside implementation

**Handling:** Run in parallel. Share the interface contract (API shape,
schema definition) upfront. Reconcile at the sync point.

### Identifying Dependencies

Before spawning any agents, ask:
1. Does Agent B need Agent A's output to start? → Blocking
2. Does Agent B need Agent A's output to finish correctly? → Non-blocking
3. Are Agents A and B completely independent? → Parallel

---

## Validation Checkpoints

Between phases, verify:

| Check | How |
|-------|-----|
| Build succeeds | Run build command, confirm no errors |
| No regressions | Run existing tests if they exist |
| Files are consistent | No merge conflicts, no orphaned references |
| Schema matches API | If both changed, verify they agree |
| Evidence written | Each agent phase should produce observable output |
| Scope matches completion condition | `reviewer-validator` checks the change against the planner's stated scope |

### Checkpoint Format

After a phase completes, produce:
```
Phase N complete:
  ✅ Agent A: [what it did] — [files changed]
  ✅ Agent B: [what it did] — [files changed]
  Validation: [what was checked]
  Proceeding to Phase N+1
```

---

## Failure Handling

### Single Agent Failure

If one agent fails:
1. **Stop dependent agents** — don't let them proceed on bad state
2. **Don't stop independent agents** — they can continue
3. **Report the failure** with context (what failed, why, what state was left)
4. **Don't retry blindly** — diagnose first, then decide whether to retry
   or take a different approach

### Cascading Failure Prevention

- Never let a failed agent's partial output feed into the next agent
- If a phase fails, roll back to the last validated state before retrying
- If the same agent fails twice, escalate to the human — don't loop

### Recovery Pattern

```
Agent failure detected:
  Failed: Agent B (database migration)
  Error: [error description]
  State: [what was partially done]

  Independent agents (continue): Agent C (documentation)
  Dependent agents (stopped): Agent D (API integration)

  Recommended action: [fix suggestion or escalation]
```

---

## Handoff Format

Every agent should return a structured result:

```
Task: [what was requested]
Status: complete / partial / failed
Changes:
  - [file]: [what changed]
  - [file]: [what changed]
Validated:
  - [what was tested/verified]
Warnings:
  - [any concerns or edge cases]
Next steps:
  - [what the next agent or phase should know]
```

This is also the shape a `docs` agent should use when writing a session
handoff note (see the `handoff` command).

---

## Skill Routing

Before assigning work, check the skills inventory at
`references/skills-inventory.md` to determine which skill each agent needs.

### Baseline Agent Roles (this project)

| Agent | Role |
|-------|------|
| `planner` | Turns a request into a scoped plan with an observable completion condition. Read-only. |
| `implementer` | Executes exactly one planner-scoped spec — no scope expansion. |
| `reviewer-validator` | Read-only; checks the change against scope/completion condition, then reviews for defects. |
| `docs` | Writes handoff notes, service docs, and reference/index updates. |

### Routing Quick Reference

| Task involves... | Assign skill |
|------------------|-------------|
| Git branches, merging, changelogs, releases | git-discipline |
| README, PR descriptions, changelogs, ADRs | documentation |
| Secrets, credentials, API keys, security | secret-hygiene |
| Task decomposition, multi-agent coordination | team-orchestrator |

Repo- or domain-specific skills (API integrations, frontend systems,
database schemas, infra discovery, etc.) live alongside this plugin in each
project and should be added to the routing table there — this shared table
only covers the cross-cutting skills every repo has in common.

### Multi-Skill Agents

Some tasks need multiple skills. An agent doing a release might need both
`git-discipline` (tagging/promotion procedure) and `documentation`
(changelog format). Declare all relevant skills in the agent spawn
description.

---

## Example: Decomposing a Complex Request

**Request:** "Add a new search endpoint with caching and update the docs"

**Decomposition:**

```
Phase 1 — Plan (sequential, read-only):
  planner: Survey existing endpoint conventions and caching patterns,
    produce a scoped spec with an observable completion condition
    (e.g. "GET /v1/search returns cached results on second call within 50ms")

Phase 2 — Implement (sequential):
  implementer: Build the endpoint and caching layer exactly per the
    planner's spec

Phase 3 — Validate (sequential):
  reviewer-validator: Check the change against the plan's scope and
    completion condition; review for correctness bugs

Phase 4 — Document + Handoff (parallel):
  docs: Update the service README and changelog (documentation skill)
  docs: Write the session handoff note (team-orchestrator handoff format)
```

This keeps each agent focused on one concern instead of one sprawling
agent trying to do everything and getting half of it wrong.
