#!/usr/bin/env python3
"""PostToolUse hook (Bash): soft-warn when `restart` is used instead of
rebuilding.

`docker compose restart` / `docker restart` reuse the existing image, so
code changes baked into a fresh build won't take effect. This never blocks
- it only emits a note (delivered via the asyncRewake wrapper in
hooks.json). Fails open on any parse error.
"""
import json
import re
import sys

RESTART_RE = re.compile(
    r"docker(?:-|\s+)compose\b.*\brestart\b|\bdocker\s+restart\b",
    re.IGNORECASE | re.DOTALL,
)


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

        if RESTART_RE.search(command):
            print(
                "deploy-verify: 'restart' reuses the OLD image - code "
                "changes won't take effect. If you rebuilt code, use "
                "'docker compose up -d --build' instead."
            )
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
