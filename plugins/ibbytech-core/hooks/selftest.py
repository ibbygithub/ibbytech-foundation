#!/usr/bin/env python3
"""Self-test harness for the ibbytech-core hard-block hooks.

For each hard-block hook, pipes crafted stdin JSON payloads through the
script as a subprocess and asserts the exit code: an OFFENDING input must
exit 2 (blocked), a BENIGN input must exit 0 (allowed). Prints PASS/FAIL per
case and a summary; exits non-zero if any case fails.

Run with: python selftest.py
"""
import json
import subprocess
import sys
from pathlib import Path

HOOKS_DIR = Path(__file__).resolve().parent

results = []


def run_hook(script_name: str, payload: dict) -> int:
    script_path = HOOKS_DIR / script_name
    proc = subprocess.run(
        [sys.executable, str(script_path)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def check(label: str, script_name: str, payload: dict, expected_code: int):
    code, out, err = run_hook(script_name, payload)
    ok = code == expected_code
    results.append((label, ok, expected_code, code, err.strip()))
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label} (expected exit {expected_code}, got {code})")
    if not ok:
        print(f"         stdout: {out.strip()!r}")
        print(f"         stderr: {err.strip()!r}")


def bash_payload(command: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "cwd": "C:/git/work/ibbytech-foundation",
        "transcript_path": "C:/tmp/transcript.jsonl",
        "session_id": "selftest-session",
        "tool_name": "Bash",
        "tool_input": {"command": command},
    }


def write_payload(file_path: str, content: str) -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "cwd": "C:/git/work/ibbytech-foundation",
        "transcript_path": "C:/tmp/transcript.jsonl",
        "session_id": "selftest-session",
        "tool_name": "Write",
        "tool_input": {"file_path": file_path, "content": content},
    }


def edit_payload(file_path: str, new_string: str, old_string: str = "old") -> dict:
    return {
        "hook_event_name": "PreToolUse",
        "cwd": "C:/git/work/ibbytech-foundation",
        "transcript_path": "C:/tmp/transcript.jsonl",
        "session_id": "selftest-session",
        "tool_name": "Edit",
        "tool_input": {
            "file_path": file_path,
            "old_string": old_string,
            "new_string": new_string,
        },
    }


def main():
    print("=== secret_guard.py ===")
    check(
        "OFFENDING: AWS access key in Bash command",
        "secret_guard.py",
        bash_payload("export AWS_ACCESS_KEY_ID=AKIAABCDEFGHIJKLMNOP"),
        2,
    )
    check(
        "OFFENDING: private key block in Write content",
        "secret_guard.py",
        write_payload("id_rsa", "-----BEGIN RSA PRIVATE KEY-----\nMIIB...\n-----END RSA PRIVATE KEY-----"),
        2,
    )
    check(
        "OFFENDING: DB URL with inline password in Edit new_string",
        "secret_guard.py",
        edit_payload("config.py", "DATABASE_URL = 'postgres://admin:SuperSecret1@dbnode-01:5432/app'"),
        2,
    )
    check(
        "OFFENDING: generic password=<realvalue>",
        "secret_guard.py",
        bash_payload('curl -u admin:hunter2ReallyReal --header "password=Sup3rSecretPW!"'),
        2,
    )
    check(
        "OFFENDING: GitHub token",
        "secret_guard.py",
        write_payload(".env", "GITHUB_TOKEN=ghp_" + "a" * 40),
        2,
    )
    check(
        "OFFENDING: prefixed env-var DB_PASSWORD with real value",
        "secret_guard.py",
        bash_payload("export DB_PASSWORD=Sup3rS3cretP@ssw0rd99"),
        2,
    )
    check(
        "OFFENDING: prefixed env-var AUTH_TOKEN with real value",
        "secret_guard.py",
        write_payload(".env", "AUTH_TOKEN=Sup3rS3cretP@ssw0rd99"),
        2,
    )
    check(
        "OFFENDING: OpenAI/Anthropic sk- API key",
        "secret_guard.py",
        write_payload(".env", "OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz1234567890ABCD"),
        2,
    )
    check(
        "BENIGN: DB_PASSWORD=${DB_PASSWORD}",
        "secret_guard.py",
        bash_payload("export DB_PASSWORD=${DB_PASSWORD}"),
        0,
    )
    check(
        "BENIGN: DB_PASSWORD=local-no-auth",
        "secret_guard.py",
        write_payload(".env", "DB_PASSWORD=local-no-auth"),
        0,
    )
    check(
        "BENIGN: FIRECRAWL_API_KEY=local-no-auth",
        "secret_guard.py",
        write_payload(".env", "FIRECRAWL_API_KEY=local-no-auth"),
        0,
    )
    check(
        "BENIGN: API_KEY=${API_KEY}",
        "secret_guard.py",
        bash_payload("export API_KEY=${API_KEY}"),
        0,
    )
    check(
        "BENIGN: bare env-var NAME with no value",
        "secret_guard.py",
        write_payload(".env.example", "TAVILY_API_KEY"),
        0,
    )
    check(
        "BENIGN: placeholder <REDACTED>",
        "secret_guard.py",
        write_payload("config.yaml", "token: <REDACTED>"),
        0,
    )
    check(
        "BENIGN: changeme placeholder",
        "secret_guard.py",
        write_payload("config.yaml", "password: changeme"),
        0,
    )
    check(
        "BENIGN: ordinary bash command",
        "secret_guard.py",
        bash_payload("git status && npm test"),
        0,
    )

    print("\n=== destructive_deny.py ===")
    check(
        "OFFENDING: git push --force",
        "destructive_deny.py",
        bash_payload("git push origin main --force"),
        2,
    )
    check(
        "OFFENDING: git push -f",
        "destructive_deny.py",
        bash_payload("git push origin main -f"),
        2,
    )
    check(
        "OFFENDING: git reset --hard",
        "destructive_deny.py",
        bash_payload("git reset --hard HEAD~3"),
        2,
    )
    check(
        "OFFENDING: rm -rf /",
        "destructive_deny.py",
        bash_payload("rm -rf / --no-preserve-root"),
        2,
    )
    check(
        "OFFENDING: docker kill",
        "destructive_deny.py",
        bash_payload("docker kill biomesh-svc-api"),
        2,
    )
    check(
        "OFFENDING: psql DROP",
        "destructive_deny.py",
        bash_payload('psql -h dbnode-01 -c "DROP TABLE users;"'),
        2,
    )
    check(
        "BENIGN: git push --force-with-lease",
        "destructive_deny.py",
        bash_payload("git push origin feature-branch --force-with-lease"),
        0,
    )
    check(
        "BENIGN: git status",
        "destructive_deny.py",
        bash_payload("git status"),
        0,
    )
    check(
        "BENIGN: docker ps",
        "destructive_deny.py",
        bash_payload("docker ps -a"),
        0,
    )

    print("\n=== persona_boundary.py ===")
    check(
        "OFFENDING: unsanctioned ssh key",
        "persona_boundary.py",
        bash_payload("ssh -i ~/.ssh/personal_key devops-agent@192.168.71.220 uptime"),
        2,
    )
    check(
        "OFFENDING: devops key against db node",
        "persona_boundary.py",
        bash_payload("ssh -i ~/.ssh/devops-agent_ed25519_clean devops-agent@dbnode-01 psql"),
        2,
    )
    check(
        "OFFENDING: dba key against svc node",
        "persona_boundary.py",
        bash_payload("ssh -i ~/.ssh/dba-agent_ed25519 dba-agent@svcnode-01 uptime"),
        2,
    )
    check(
        "BENIGN: devops key -> svc node (remote docker compose up)",
        "persona_boundary.py",
        bash_payload(
            "ssh -i ~/.ssh/devops-agent_ed25519_clean devops-agent@192.168.71.220 "
            "docker compose -f docker-compose.svc.yml up -d"
        ),
        0,
    )
    check(
        "BENIGN: dba key -> db node",
        "persona_boundary.py",
        bash_payload("ssh -i ~/.ssh/dba-agent_ed25519 dba-agent@192.168.71.221 psql -c 'select 1'"),
        0,
    )
    check(
        "BENIGN: non-ssh command",
        "persona_boundary.py",
        bash_payload("ls -la"),
        0,
    )

    print("\n=== no_laptop_docker.py ===")
    check(
        "OFFENDING: local compose up of tracked prod service",
        "no_laptop_docker.py",
        bash_payload("docker compose -f docker-compose.svc.yml up -d"),
        2,
    )
    check(
        "OFFENDING: local docker run of biomesh-svc image",
        "no_laptop_docker.py",
        bash_payload("docker run -d --name biomesh-svc-api biomesh-svc-api:latest"),
        2,
    )
    check(
        "BENIGN: remote compose up over ssh",
        "no_laptop_docker.py",
        bash_payload(
            "ssh -i ~/.ssh/devops-agent_ed25519_clean devops-agent@192.168.71.220 "
            "docker compose -f docker-compose.svc.yml up -d"
        ),
        0,
    )
    check(
        "BENIGN: ad-hoc non-prod container",
        "no_laptop_docker.py",
        bash_payload("docker run --rm -it alpine sh"),
        0,
    )
    check(
        "BENIGN: local compose up of non-tracked project",
        "no_laptop_docker.py",
        bash_payload("docker compose up -d"),
        0,
    )

    print("\n=== summary ===")
    total = len(results)
    passed = sum(1 for r in results if r[1])
    failed = total - passed
    print(f"{passed}/{total} passed, {failed} failed")

    if failed:
        print("\nFailures:")
        for label, ok, expected, got, err in results:
            if not ok:
                print(f"  - {label}: expected {expected}, got {got} ({err})")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
