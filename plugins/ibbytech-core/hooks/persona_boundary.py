#!/usr/bin/env python3
"""PreToolUse hook (Bash): hard-block SSH persona/key misuse.

Sanctioned keys (see ibbytech-foundation SSH persona rules, global CLAUDE.md):
  - devops-agent_ed25519_clean  -> service/app nodes (svcnode, brainnode)
  - dba-agent_ed25519           -> database node only (dbnode)

Only inspects commands containing "ssh". Blocks (exit 2) when:
  1. An `ssh -i <key>` references a key file not in the sanctioned set
     (credential escalation / unknown identity).
  2. The devops key is used against the DB node, or the dba key is used
     against a service/app node (persona/node mismatch).

If the command uses ssh without a recognizable `-i <key>` and without a
recognizable sanctioned hostname/IP, it exits 0 - this hook does not want to
over-block generic ssh usage it can't classify.
"""
import json
import re
import sys

DEVOPS_KEY = "devops-agent_ed25519_clean"
DBA_KEY = "dba-agent_ed25519"
SANCTIONED_KEYS = (DEVOPS_KEY, DBA_KEY)

DB_NODE_MARKERS = ("dbnode", "192.168.71.221")
SVC_NODE_MARKERS = ("svcnode", "brainnode", "192.168.71.220", "192.168.71.222")

IDENTITY_RE = re.compile(r"-i\s+(\S+)")


def extract_key_name(command: str):
    m = IDENTITY_RE.search(command)
    if not m:
        return None
    path = m.group(1).strip("'\"")
    # normalize path separators, take the basename
    path = path.replace("\\", "/")
    return path.rsplit("/", 1)[-1]


def classify_key(key_name: str):
    if key_name is None:
        return None
    for sanctioned in SANCTIONED_KEYS:
        if key_name == sanctioned or key_name.endswith("/" + sanctioned):
            return sanctioned
    return "UNKNOWN"


def target_class(command: str):
    lowered = command.lower()
    is_db = any(marker in lowered for marker in DB_NODE_MARKERS)
    is_svc = any(marker in lowered for marker in SVC_NODE_MARKERS)
    if is_db and not is_svc:
        return "db"
    if is_svc and not is_db:
        return "svc"
    return None


def main():
    try:
        raw = sys.stdin.read()
        if not raw or not raw.strip():
            return 0
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return 0
        if payload.get("tool_name") != "Bash":
            return 0
        tool_input = payload.get("tool_input") or {}
        command = str(tool_input.get("command") or "")
        if not command or "ssh" not in command.lower():
            return 0

        key_name = extract_key_name(command)
        target = target_class(command)

        if key_name is not None:
            classified = classify_key(key_name)
            if classified == "UNKNOWN":
                sys.stderr.write(
                    "persona-boundary: HARD BLOCK (CREDENTIAL_ESCALATION) - "
                    f"ssh command uses key '{key_name}', which is not a "
                    "sanctioned persona key (devops-agent_ed25519_clean or "
                    "dba-agent_ed25519). Use the sanctioned persona for the "
                    "target node; do not switch keys to gain access.\n"
                )
                return 2

            if classified == DEVOPS_KEY and target == "db":
                sys.stderr.write(
                    "persona-boundary: HARD BLOCK (CREDENTIAL_ESCALATION) - "
                    "devops-agent key used against the database node. Use "
                    "the sanctioned persona for the target node; do not "
                    "switch keys to gain access.\n"
                )
                return 2

            if classified == DBA_KEY and target == "svc":
                sys.stderr.write(
                    "persona-boundary: HARD BLOCK (CREDENTIAL_ESCALATION) - "
                    "dba-agent key used against a service/app node. Use the "
                    "sanctioned persona for the target node; do not switch "
                    "keys to gain access.\n"
                )
                return 2

        # No -i key and/or no recognizable sanctioned host: don't over-block
        # generic ssh usage this hook can't confidently classify.
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
