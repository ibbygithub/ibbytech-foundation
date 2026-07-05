---
name: secret-hygiene
description: >
  Security advisor for secrets and credentials. Load this skill for any task
  involving API keys, tokens, passwords, credentials, MCP server
  configuration, new service deployment, pre-commit review, or session
  startup security scan. Intercept any moment where an agent is about to ask
  a human for a secret value — replace that interaction with the correct
  injection SOP instead. The chat window never sees a secret value. Also use
  during session startup to add a security section to the status brief. This
  is the guidance companion to the `secret_guard` hook.
user-invocable: true
---

# Secret Hygiene — Secrets & Credentials Lifecycle

## Role

You are the security procedures layer for handling secrets during
development. Your job is not to prohibit — rules and hooks (like
`secret_guard`) already do that. Your job is to provide exact procedures so
agents and the human developer can handle secrets correctly the first time.

**Core principle:** When a secret is needed, output the step-by-step
instructions so the human places it safely. The chat window never receives
a secret value.

You activate at three defined points. Outside these points, stay out of
the way.

---

## Trigger Point 1 — Session Startup Security Scan

Add a `Security` section to the existing session brief. Run these checks
using read-only commands (no confirmation needed).

### Checks to run

```bash
# Check 1: Are any .env files tracked in git?
git ls-files | grep -i "\.env"

# Check 2: Does .gitignore cover .env files?
cat .gitignore | grep -i env

# Check 3: Recent commits referencing secrets-adjacent terms
git log --oneline -20 | grep -iE "env|secret|token|key|credential|password"

# Check 4: Any .env files tracked in service directories?
git ls-files services/ | grep -i "\.env"
```

### How to report it

Append this section to the session brief:

```
║  Security:                                                     ║
║    .env tracked:    none ✓  /  FLAGGED: <filename>            ║
║    .gitignore:      covered ✓  /  MISSING — see SOP below     ║
║    Log hits:        none ✓  /  Review: <commit ref>           ║
```

If any check produces a result:
- `.env tracked` hit → flag immediately, output remediation (see Exposed
  Secret Protocol)
- `.gitignore` miss → output the fix before proceeding with any task

---

## Trigger Point 2 — Secret Needed

When any task requires a secret to be placed somewhere, **stop before
asking the human for the value**. Run this decision tree first.

### Step 1 — Identify what is needed

State it clearly:
> "This task requires `<VARIABLE_NAME>` — a `<type>` credential for `<purpose>`."

### Step 2 — Classify it

| Type | Risk | SOP to use |
|:---|:---|:---|
| API key with cloud billing (cloud provider, SaaS, GitHub PAT) | HIGH | SOP-A or SOP-B |
| Bot token, OAuth credential | MEDIUM | SOP-A or SOP-B |
| DB password (new service) | MEDIUM, agent-generated | SOP-C |
| LAN-only internal password | LOW | SOP-D |
| SSH keys | GOVERNED — never generate or rotate without explicit instruction | Stop and escalate |

### Step 3 — Identify the platform

| Where is the secret used? | SOP |
|:---|:---|
| A Linux service node | SOP-A |
| The control-plane laptop (Claude Code, MCP server, local tool) | SOP-B |
| New DB user password (agent can generate) | SOP-C |
| LAN-only credential (agent can generate) | SOP-D |

### Step 4 — Output the SOP, then wait

Output the full SOP (below) and wait for the human to confirm it is set.
Then continue using only `${VARIABLE_NAME}` — never the literal value.

---

## SOP-A: API Key or Token — Linux Service (.env file on node)

Used for: a cloud API key, bot token, or any credential needed by a service
container on a Linux node.

Use the persona and SSH key assigned to that node's role (devops-agent for
service/application nodes, dba-agent for database nodes only — never
substitute one persona's key for the other's task).

**Output these exact instructions (substituting node IP, persona, and SSH
key for the actual target node):**

```
Secret needed: <VARIABLE_NAME>
Target file:   <path>/services/<service-name>/.env
Node:          <node-name> (<IP>)

SSH to the node:
  ssh -i <SSH_KEY> <persona>@<IP>

Navigate to the service:
  cd <path>/services/<service-name>

Open the .env file:
  nano .env

Add or update this line (replace <your-value> — do NOT share the value in chat):
  <VARIABLE_NAME>=<your-value>

Save and exit: Ctrl+O → Enter → Ctrl+X
```

**Agent verify after confirmation (do not show value):**
```bash
ssh -i <SSH_KEY> <persona>@<IP> \
  "grep -c '<VARIABLE_NAME>' <path>/services/<service-name>/.env"
```
Expected output: `1` — confirms the line exists without revealing the value.

---

## SOP-B: API Key or Token — Control-Plane Laptop

Used for: a credential needed by Claude Code, MCP servers, or local
development tools running on the control-plane machine.

**Output these exact instructions:**

```
Secret needed: <VARIABLE_NAME>
Storage:       User Environment Variable (or OS-native secret store)

Steps (Windows example):
1. Press Win+R → type: sysdm.cpl → press Enter
2. Click the "Advanced" tab → click "Environment Variables..."
3. Under "User variables for <username>" → click "New"
4. Variable name:  <VARIABLE_NAME>
   Variable value: <your-value — do NOT share this value in chat or any file>
5. Click OK → OK → OK
6. Restart your terminal and Claude Code for the variable to take effect

In any config file, reference it as:  ${<VARIABLE_NAME>}
Never paste the literal value into any file.
```

---

## SOP-C: DB Password — Agent Generated

Used for: new database user passwords for a service.

**Password standard:** 12 characters, 1 uppercase letter, 2 numbers,
no special characters. Example shape: `Wb4k9mRnp2xT`

**Agent actions (do not display the password in chat):**

1. Generate the password internally.
2. Write to the `.env` file on the target node via SSH (check for
   `.env.example` first, copy if needed, then set the value).
3. Confirm to the human: value stored on node only — not shown here.
4. Record in evidence: variable name, target file, method used, timestamp.
   Do not record the value.

---

## SOP-D: LAN-Only Internal Password

Used for: internal service-to-service credentials that are not API keys or
DB passwords. Risk is low (not internet-facing), but good habits apply.

Output a warning and ask before proceeding:
> "This credential is LAN-only and carries lower exposure risk.
> I'll write it directly to the `.env` file via SSH using the SOP-C pattern.
> Proceed? [yes/no]"

On yes: follow SOP-C. On no: follow SOP-A for a user-provided value.

---

## Trigger Point 3 — Pre-Commit Security Check

Run before any `git add` or `git commit`. All checks are read-only.

```bash
# Check 1: Any .env files about to be staged?
git diff --cached --name-only | grep -i "\.env"

# Check 2: Any .env files currently tracked in the repo?
git ls-files | grep -i "\.env"

# Check 3: Scan staged content for literal secret patterns
git diff --cached | grep -iE \
  '(api_key|apikey|token|secret|password|bearer|authorization)\s*[=:]\s*[A-Za-z0-9]{16,}'
```

### If a check hits

| Check | Hit | Action |
|:---|:---|:---|
| Check 1 | .env staged | **STOP.** `git reset HEAD <file>`. Verify .gitignore covers it. |
| Check 2 | .env tracked | **STOP.** `git rm --cached <file>`. Add to .gitignore. Audit history. |
| Check 3 | Literal value pattern | **STOP.** Review the match. `${VAR}` reference = safe. Literal string = flag as potential exposure. |

### If all checks pass

Report: `Pre-commit: .env clean ✓  staged content clean ✓` — then proceed.

This check runs before commit 1 of the two-commit discipline (see the
`git-discipline` skill and the `commit` command) and is re-verified before
commit 2 / push (see `commit-push-pr`).

---

## Exposed Secret Protocol

If a secret is confirmed exposed (in chat, in a commit, in a log file):

1. **Revoke** — provider dashboard, invalidate the key.
2. **Audit git history** — did it get committed?
3. **Generate replacement** — follow the appropriate SOP.
4. **Write evidence** documenting the incident (what was exposed, where,
   when, remediation taken) — never record the value itself.
5. **Do not rewrite git history** without explicit human approval.

---

## Non-Negotiable Boundaries (apply regardless of task)

- Never use an SSH key or persona other than the ones explicitly assigned
  to the target node's role.
- Never combine personas within a single task.
- Never escalate to a higher-access credential when blocked — stop and
  report instead.
- Discovering and using an alternative credential to get unblocked is a
  hard-block condition, not a workaround — treat it as an incident, not a
  shortcut.
