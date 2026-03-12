# [Project Name] — Agent Behavior Rules

## Foundation Reference
Engineering standards: ../ibbytech-foundation
Launch command: claude --add-dir ../ibbytech-foundation

## Session Startup
Run `/start-session` at the start of every session.
Rules, behavioral directives, and skills are loaded from `../ibbytech-foundation`.

---

## Project Identity

- **Project:** [One-line description of what this project is and does]
- **Users:** [Who uses this — internal, family, customers, etc.]
- **Node (app):** [svcnode-01 / brainnode-01] — [what runs here] — persona: devops-agent
- **Node (db):** dbnode-01 — [which database] — persona: dba-agent
- **brainnode-01:** [Not yet onboarded / Active — describe what runs here]

---

## Platform Services Consumed

List which platform services this project uses. Check `../platform/.claude/services/_index.md`
before building anything that might already exist.

- [Service name]: [what this project uses it for]
- [Service name]: [what this project uses it for]

---

## Database Routing

- **Primary database:** [database_name] on dbnode-01
- **Schema:** [schema name]
- **App user:** [app_user]
- [Any routing decisions or restrictions specific to this project]

---

## Known Infrastructure State — Last Verified [YYYY-MM-DD]

Document confirmed facts that future agents need at session start.
Update this section when state changes. Do not remove entries without verifying.

- [Node/service]: [State description — what's running, what's not, open issues]
- [Node/service]: [State description]

---

## Open Architecture Decisions

Items that need resolution before work can proceed. Remove when resolved.

- [Item]: [What the question is, what constraints apply]

---

## Technology Registry (Approved)

| Technology | Role | Rationale | Date |
|------------|------|-----------|------|
| [Tech] | [What it does in this project] | [Why this was chosen] | [YYYY-MM-DD] |

---

## Project-Specific Rules

[Any rules that extend or specialize the foundation rules for this project.
Do not repeat foundation rules here — only project-specific additions.]
