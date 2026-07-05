"""homelab-logs — stdio MCP server exposing read-only log query tools
against the platform's Loki log aggregation service.

All requests are built by `_loki_api` (pure, no `mcp` dependency) and
executed via `_loki_api.call`. Only the Loki `query_range` read endpoint is
used — no write/push endpoints are exposed by this server, per the task's
read-only requirement.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

import _loki_api as api

mcp = FastMCP("homelab-logs")


@mcp.tool()
def query_logs(logql: str, since: str = "1h", limit: int = 200) -> dict[str, Any]:
    """Run a LogQL query against Loki over a relative time window and
    return matching log lines. `logql` is a full LogQL query (e.g.
    '{service="scraper", level="error"}'). `since` is a relative duration
    like '30m', '1h', '2d' — used to compute the query's start time; `end`
    is now. `limit` caps the number of returned entries.
    """
    request = api.build_query_range(logql, since=since, limit=limit)
    return api.call(request, timeout=30.0)


@mcp.tool()
def recent_service_logs(service: str, minutes: int = 30, limit: int = 200) -> dict[str, Any]:
    """Convenience wrapper: fetch the last `minutes` of logs for a given
    service/container name, using the `{service="<name>"}` stream selector
    documented in loki.md's standard log labels. Equivalent to calling
    `query_logs('{service="<name>"}', since=f"{minutes}m", limit=limit)`.
    """
    request = api.build_recent_service_logs(service, minutes=minutes, limit=limit)
    return api.call(request, timeout=30.0)


if __name__ == "__main__":
    mcp.run()
