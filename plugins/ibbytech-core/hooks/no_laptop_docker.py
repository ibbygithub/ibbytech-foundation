#!/usr/bin/env python3
"""PreToolUse hook (Bash): hard-block local docker bring-up of tracked prod
services.

The laptop is a control-plane machine, not a deploy target. Blocks (exit 2)
a LOCAL `docker compose ... up` or `docker run` that references a tracked
prod service (docker-compose.svc.yml, or an image/service name prefixed
biomesh-svc-, platform-, or shogun-) when the command shows no remote
target (no `ssh `, ` -H `, `DOCKER_HOST=`, or a 192.168.71.* address).
"""
import json
import re
import sys

COMPOSE_UP_RE = re.compile(r"docker(?:-|\s+)compose\b.*\bup\b", re.IGNORECASE | re.DOTALL)
DOCKER_RUN_RE = re.compile(r"\bdocker\s+run\b", re.IGNORECASE)

TRACKED_MARKERS = [
    "docker-compose.svc.yml",
    "biomesh-svc-",
    "platform-",
    "shogun-",
]

REMOTE_MARKERS = [
    re.compile(r"\bssh\s"),
    re.compile(r"\s-H\s"),
    re.compile(r"DOCKER_HOST="),
    re.compile(r"192\.168\.71\."),
]


def find_tracked_marker(command: str):
    for marker in TRACKED_MARKERS:
        if marker.lower() in command.lower():
            return marker
    return None


def has_remote_target(command: str) -> bool:
    return any(p.search(command) for p in REMOTE_MARKERS)


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

        is_bringup = bool(COMPOSE_UP_RE.search(command)) or bool(DOCKER_RUN_RE.search(command))
        if not is_bringup:
            return 0

        marker = find_tracked_marker(command)
        if not marker:
            return 0

        if has_remote_target(command):
            return 0

        sys.stderr.write(
            f"no-laptop-docker: blocked - {marker} is a tracked prod service "
            "and must run on svcnode-01, not the laptop. Deploy via ssh to "
            "svcnode-01 (devops-agent) and run compose there.\n"
        )
        return 2
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
