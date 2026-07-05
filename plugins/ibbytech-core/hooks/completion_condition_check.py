#!/usr/bin/env python3
"""UserPromptSubmit hook: soft-warn reminder to state a completion condition.

Reads the user's prompt (`prompt` field, falling back to the raw stdin text)
and, if it looks like a substantive build/change task with no acceptance
signal, prints one advisory line to stdout. Never blocks; exits 0 always.
Conservative by design - on any doubt it stays silent.
"""
import json
import re
import sys

IMPERATIVE_RE = re.compile(
    r"\b(build|implement|add|create|fix|refactor|deploy|migrate|write|set up)\b",
    re.IGNORECASE,
)

ACCEPTANCE_RE = re.compile(
    r"(test|verify|done when|should\s+(return|pass|produce)|acceptance|"
    r"completion condition|passing)",
    re.IGNORECASE,
)

QUESTION_START_RE = re.compile(
    r"^\s*(who|what|why|how|does|can|is|should)\b", re.IGNORECASE
)


def get_prompt_text(payload) -> str:
    if isinstance(payload, dict):
        prompt = payload.get("prompt")
        if isinstance(prompt, str):
            return prompt
    return ""


def main():
    try:
        raw = sys.stdin.read()
        if not raw or not raw.strip():
            return 0

        text = ""
        try:
            payload = json.loads(raw)
            text = get_prompt_text(payload)
        except Exception:
            payload = None

        if not text:
            # Fall back to treating the raw stdin as the prompt text, in
            # case this hook is invoked without the usual JSON envelope.
            text = raw

        text = text.strip()
        if not text:
            return 0

        # Skip questions outright.
        if text.rstrip().endswith("?") and QUESTION_START_RE.match(text):
            return 0

        if len(text) <= 60:
            return 0

        if not IMPERATIVE_RE.search(text):
            return 0

        if ACCEPTANCE_RE.search(text):
            return 0

        print(
            "Reminder: state an observable completion condition (a passing "
            "test, a returned status, a row count) before proceeding."
        )
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
