#!/usr/bin/env python3
"""Stop hook: soft-warn nudge to verify via observable evidence before
declaring done. Always prints its one-line note and exits 0. Never blocks.
"""
import sys


def main():
    try:
        # Drain stdin defensively even though this hook doesn't need the
        # payload, so the harness doesn't see a broken pipe.
        sys.stdin.read()
    except Exception:
        pass
    print(
        "Before finishing, confirm the change via observable evidence "
        "(test/endpoint/row-count), not self-report."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
