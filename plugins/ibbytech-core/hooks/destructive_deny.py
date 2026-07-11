#!/usr/bin/env python3
"""PreToolUse hook (Bash): hard-block irreversible/destructive commands.

Reads the pending Bash command from stdin JSON and blocks (exit 2) if it
matches a known-destructive pattern: force pushes (bare --force/-f, but NOT
--force-with-lease), hard resets, forced cleans, branch force-delete, `rm -rf
/` or `~`, `chmod 777`, docker kill/rm/rmi, service stop/disable, reboot/
shutdown/poweroff, destructive SQL via psql, and remote destructive commands
over ssh. Fails open (exit 0) on any parse error or when nothing matches.
"""
import json
import re
import sys

RULES = []


def rule(name, pattern, flags=re.IGNORECASE):
    RULES.append((name, re.compile(pattern, flags)))


# --- git ---------------------------------------------------------------
# Force push: block bare --force / -f, but allow --force-with-lease.
rule(
    "git push --force",
    r"\bgit\s+push\b[^\n]*--force\b(?!-with-lease)",
)
rule(
    "git push -f",
    r"\bgit\s+push\b[^\n]*\s-f\b(?!\w)",
)
rule("git reset --hard", r"\bgit\s+reset\s+--hard\b")
rule("git clean -fd/-fdx", r"\bgit\s+clean\s+-[a-z]*f[a-z]*d[a-z]*\b")
# Case-sensitive on purpose: -D (force-delete, Red Zone per 04-git-discipline)
# must block, but safe -d (post-merge delete, Yellow Zone with human confirm)
# must pass. The module default IGNORECASE made -d match too, overblocking
# the sanctioned operation.
rule("git branch -D", r"\bgit\s+branch\s+-D\b", flags=0)

# --- filesystem ----------------------------------------------------------
rule("rm -rf /", r"\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+/(?:\s|$)")
rule("rm -rf ~", r"\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+~(?:\s|$|/)")
rule("chmod 777", r"\bchmod\s+(-R\s+)?777\b")

# --- docker ----------------------------------------------------------------
rule("docker kill", r"\bdocker\s+kill\b")
rule("docker rm", r"\bdocker\s+rm\b\s")
rule("docker rmi", r"\bdocker\s+rmi\b\s")

# --- system ------------------------------------------------------------
rule("systemctl stop", r"\bsystemctl\s+stop\b")
rule("systemctl disable", r"\bsystemctl\s+disable\b")
rule("reboot", r"(?<![\w-])reboot\b")
rule("shutdown", r"(?<![\w-])shutdown\b")
rule("poweroff", r"(?<![\w-])poweroff\b")

# --- sql via psql ------------------------------------------------------
rule("psql destructive SQL", r"\bpsql\b.*\b(DROP|DELETE|TRUNCATE)\s+")

# --- remote destructive over ssh ----------------------------------------
rule("ssh ... sudo rm", r"\bssh\b[^\n]*\bsudo\s+rm\s+")
rule("ssh ... rmdir", r"\bssh\b[^\n]*\brmdir\s+")


def scan(command: str):
    if not command:
        return None
    for name, pattern in RULES:
        if pattern.search(command):
            return name
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
        if not command:
            return 0
        hit = scan(command)
        if hit:
            sys.stderr.write(
                f"destructive-deny: blocked '{hit}' - irreversible. Confirm "
                "intent and run manually if truly required.\n"
            )
            return 2
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
