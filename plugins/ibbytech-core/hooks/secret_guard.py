#!/usr/bin/env python3
"""PreToolUse hook (Write|Edit|MultiEdit|Bash): hard-block on live-looking credentials.

Reads a JSON payload on stdin describing the pending tool call, extracts the
text the tool would write/execute, and scans it for patterns that look like a
real, live credential (as opposed to a placeholder). On a match it prints a
human-readable reason to stderr and exits 2, which Claude Code treats as a
PreToolUse block. Any parsing failure fails OPEN (exit 0) - this hook must
never crash-loop the session.
"""
import json
import re
import sys

# Placeholders / non-secrets that must never be blocked, checked against the
# captured "value" portion of a generic key=value / key: value match.
PLACEHOLDER_PATTERNS = [
    r"^\$\{.*\}$",          # ${VAR} / ${VAR:-default}
    r"^<REDACTED>$",
    r"^<.*>$",              # <anything>
    r"^local-no-auth$",
    r"^changeme$",
    r"^x+$",                # xxx, xxxxxxxx
    r"^example$",
    r"^your_.*$",
    r"^dummy$",
    r"^$",                  # empty
]

LIVE_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("GitHub token", re.compile(r"gh[pousr]_[0-9A-Za-z]{36,}")),
    ("GitHub fine-grained PAT", re.compile(r"github_pat_[0-9A-Za-z_]{40,}")),
    ("GitLab token", re.compile(r"glpat-[0-9A-Za-z_\-]{20,}")),
    ("Slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
    ("private key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "database URL with inline password",
        re.compile(r"(postgres|postgresql|mysql|mongodb)(\+\w+)?://[^:\s/]+:[^@\s/]+@"),
    ),
    ("OpenAI/Anthropic API key", re.compile(r"sk-(ant-|proj-)?[A-Za-z0-9_\-]{20,}")),
]

# Generic key=value / key: "value" secret pattern. The keyword is allowed to
# be the tail of a larger identifier (DB_PASSWORD, AUTH_TOKEN, X_API_KEY,
# MYAPP_API_KEY, ...) - a plain \b would not fire between an underscore and
# the keyword since underscore is a word char, so prefixed names would slip
# through. Value captured separately so it can be checked against the
# placeholder allowlist and a minimum "looks real" length/shape heuristic.
GENERIC_SECRET_RE = re.compile(
    r"(?i)(?:^|[^A-Za-z0-9])[A-Za-z0-9_]*?"
    r"(password|passwd|api[_-]?key|secret|token)\s*[:=]\s*"
    r"(['\"]?)([^\s'\"]+)\2"
)


def is_placeholder(value: str) -> bool:
    if not value:
        return True
    for pat in PLACEHOLDER_PATTERNS:
        if re.match(pat, value, re.IGNORECASE):
            return True
    # All-caps env-var-style NAME with no value / self-referential, e.g.
    # `TAVILY_API_KEY` alone (value would just repeat an identifier), or an
    # all-caps identifier with underscores and no lowercase/digits variety
    # that looks like a variable name rather than a secret value.
    if re.match(r"^[A-Z][A-Z0-9_]*$", value):
        return True
    return False


def looks_real(value: str) -> bool:
    if is_placeholder(value):
        return False
    if len(value) < 8:
        return False
    return True


def extract_text(payload: dict) -> str:
    tool_name = payload.get("tool_name") or ""
    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return ""

    if tool_name == "Bash":
        return str(tool_input.get("command") or "")
    if tool_name == "Write":
        return str(tool_input.get("content") or "")
    if tool_name in ("Edit", "MultiEdit"):
        # MultiEdit may carry multiple edits; support both shapes defensively.
        parts = []
        if "new_string" in tool_input:
            parts.append(str(tool_input.get("new_string") or ""))
        edits = tool_input.get("edits")
        if isinstance(edits, list):
            for e in edits:
                if isinstance(e, dict):
                    parts.append(str(e.get("new_string") or ""))
        return "\n".join(parts)

    # Unknown tool: fall back to concatenating any string-ish values so we
    # still catch obvious secrets without erroring.
    parts = []
    for v in tool_input.values():
        if isinstance(v, str):
            parts.append(v)
    return "\n".join(parts)


def scan(text: str):
    for label, pattern in LIVE_PATTERNS:
        if pattern.search(text):
            return label
    for m in GENERIC_SECRET_RE.finditer(text):
        key = m.group(1)
        value = m.group(3)
        if looks_real(value):
            return f"{key} value"
    return None


def main():
    try:
        raw = sys.stdin.read()
        if not raw or not raw.strip():
            return 0
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            return 0
        text = extract_text(payload)
        if not text:
            return 0
        hit = scan(text)
        if hit:
            sys.stderr.write(
                "secret-guard: blocked - output appears to contain a live "
                f"{hit}. Reference secrets by env-var name; never inline a "
                "real credential.\n"
            )
            return 2
        return 0
    except Exception:
        # Fail open: never crash-loop the session on a malformed payload.
        return 0


if __name__ == "__main__":
    sys.exit(main())
