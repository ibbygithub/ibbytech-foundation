"""Pure request-builder helpers for the homelab-logs (Loki) MCP server.

No dependency on the `mcp` package. `build_*` functions return plain dicts
describing an HTTP GET request:

    {"method": "GET", "url": "<full URL>", "params": {...}, "json": None}

Base URL comes from the `LOKI_BASE` env var — no auth/secrets involved per
loki.md ("Method: None (internal network, no auth required currently)").

Endpoint shape taken from loki.md and standard Loki HTTP API conventions:
  - GET /loki/api/v1/query_range?query=<LogQL>&start=<ns>&end=<ns>&limit=<n>

ASSUMPTION: loki.md documents the push endpoint (/loki/api/v1/push) in
detail but does not spell out the query_range parameters. This module uses
Loki's standard query_range contract (query/start/end/limit, start and end
as Unix nanosecond timestamps), which is the documented upstream Loki HTTP
API and is consistent with loki.md's log labels (service/level/node/...).
This server is read-only by design — no write/push endpoints are built here.
"""

from __future__ import annotations

import os
import re
import time
from typing import Any, Optional

DEFAULT_LOKI_BASE = "http://192.168.71.220:3100"

_DURATION_RE = re.compile(r"^(\d+)\s*(s|m|h|d)$", re.IGNORECASE)
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _loki_base() -> str:
    return os.environ.get("LOKI_BASE", DEFAULT_LOKI_BASE).rstrip("/")


def parse_duration_to_seconds(since: str) -> int:
    """Parse a duration like '1h', '30m', '15s', '2d' into seconds.

    Raises ValueError on an unrecognized format so callers can surface a
    clear error instead of silently defaulting.
    """
    match = _DURATION_RE.match(since.strip())
    if not match:
        raise ValueError(
            f"Invalid duration {since!r}; expected formats like '30m', '1h', '2d'"
        )
    value, unit = match.groups()
    return int(value) * _UNIT_SECONDS[unit.lower()]


def build_query_range(
    logql: str, since: str = "1h", limit: int = 200, now_ns: Optional[int] = None
) -> dict[str, Any]:
    """Build a GET /loki/api/v1/query_range request.

    `since` is a relative duration ('1h', '30m', ...) used to compute
    `start` as (now - since) and `end` as now, both in Unix nanoseconds
    (Loki's expected timestamp unit).
    """
    end_ns = now_ns if now_ns is not None else time.time_ns()
    start_ns = end_ns - parse_duration_to_seconds(since) * 1_000_000_000
    return {
        "method": "GET",
        "url": f"{_loki_base()}/loki/api/v1/query_range",
        "params": {
            "query": logql,
            "start": str(start_ns),
            "end": str(end_ns),
            "limit": limit,
        },
        "json": None,
    }


def build_service_selector(service: str) -> str:
    """Build a LogQL stream selector for a service/container name, per the
    label conventions in loki.md (`service` label on every log stream).
    """
    return f'{{service="{service}"}}'


def build_recent_service_logs(
    service: str, minutes: int = 30, limit: int = 200, now_ns: Optional[int] = None
) -> dict[str, Any]:
    """Convenience wrapper: build a query_range request for the last
    `minutes` of logs from a given service/container, using the
    `{service="..."}` selector documented in loki.md.
    """
    logql = build_service_selector(service)
    return build_query_range(logql, since=f"{minutes}m", limit=limit, now_ns=now_ns)


# ---------------------------------------------------------------------------
# Runtime HTTP call wrapper (thin; used only when the server actually runs)
# ---------------------------------------------------------------------------

def call(request: dict[str, Any], timeout: float = 30.0) -> dict[str, Any]:
    """Execute a built request dict with httpx and return a structured
    result. Never raises — non-200 responses and exceptions are converted
    into an {"error": ...} payload.
    """
    import httpx

    method = request["method"]
    url = request["url"]
    params = request.get("params")

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(method, url, params=params)
        if resp.status_code >= 400:
            return {
                "error": True,
                "status_code": resp.status_code,
                "message": f"{method} {url} returned {resp.status_code}",
                "body": _safe_text(resp),
            }
        try:
            return resp.json()
        except ValueError:
            return {"ok": True, "status_code": resp.status_code, "text": resp.text}
    except httpx.TimeoutException:
        return {"error": True, "message": f"Timed out calling {method} {url}"}
    except httpx.HTTPError as exc:
        return {"error": True, "message": f"HTTP error calling {method} {url}: {exc}"}


def _safe_text(resp: Any) -> str:
    try:
        return resp.text[:2000]
    except Exception:
        return ""
