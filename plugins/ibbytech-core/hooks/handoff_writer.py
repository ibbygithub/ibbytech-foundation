#!/usr/bin/env python3
"""Stop hook: soft-warn suggesting a one-page handoff be written.

Ensures `${CLAUDE_PROJECT_DIR}/outputs/work-log/` exists (falling back to
`cwd` from stdin when the env var isn't set), and if no `*.md` file there was
modified in the last 120 minutes, prints a suggestion to write one. Never
blocks; always exits 0.
"""
import json
import os
import sys
import time


def resolve_project_dir(payload) -> str:
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return env_dir
    if isinstance(payload, dict):
        cwd = payload.get("cwd")
        if isinstance(cwd, str) and cwd:
            return cwd
    return os.getcwd()


def main():
    try:
        raw = sys.stdin.read()
        payload = None
        if raw and raw.strip():
            try:
                payload = json.loads(raw)
            except Exception:
                payload = None

        project_dir = resolve_project_dir(payload)
        work_log_dir = os.path.join(project_dir, "outputs", "work-log")

        try:
            os.makedirs(work_log_dir, exist_ok=True)
        except Exception:
            # Can't create it (e.g. read-only fs) - nothing more to do,
            # fail open silently.
            return 0

        now = time.time()
        recent_cutoff = 120 * 60  # 120 minutes in seconds

        recent_md_found = False
        try:
            for name in os.listdir(work_log_dir):
                if not name.lower().endswith(".md"):
                    continue
                full_path = os.path.join(work_log_dir, name)
                try:
                    mtime = os.path.getmtime(full_path)
                except OSError:
                    continue
                if (now - mtime) <= recent_cutoff:
                    recent_md_found = True
                    break
        except Exception:
            return 0

        if not recent_md_found:
            print(
                "handoff-writer: no recent handoff note found. Consider "
                "writing one-page handoff at "
                "outputs/work-log/YYYY-MM-DD-HH-MM-summary.md covering: "
                "what was done, files changed, decisions made, and the "
                "next-session start point."
            )
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
