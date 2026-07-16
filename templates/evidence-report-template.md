# Evidence Report — [Task Name]

**Date:** YYYY-MM-DD
**Branch:** [feature/<name> or fix/<name>]
**Task:** [Plain English description of what was done]
**Node(s):** [svcnode-01 / dbnode-01 / brainnode-01 / laptop only]
**Persona(s):** [devops-agent / dba-agent / none]

---

## Objective

[One paragraph: what this task was trying to accomplish and why.]

---

## Actions Taken

### 1. [Action title]

[Description of what was done. Include commands run, configs changed, decisions made.]

```bash
# Commands run (where relevant)
```

### 2. [Action title]

[Continue for each significant action.]

---

## Verification

[How was the result confirmed? Include command output, test results, or observations.]

```
[Raw output or test results]
```

---

## Green Gate Checklist

| # | Item | Status |
|:--|:-----|:-------|
| 1 | Validate PASS | PASS / SKIP (reason) / FAIL (reason) |
| 2 | Loki Level 1 | PASS / WARN (gap documented) / SKIP |
| 3 | OpenAPI spec | committed / SKIP |
| 4 | Capability registry | current / SKIP |
| 5 | _index.md | updated / SKIP |
| 6 | Evidence report | PASS — this file |
| 7 | .env.example | current / no new vars / SKIP |

---

## Outcome

**[COMPLETE / PARTIAL / ABANDONED]** — [One sentence describing the result and
any follow-up actions needed.]
