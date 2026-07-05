"""Pure request-builder helpers for the platform-retrieval MCP server.

This module has NO dependency on the `mcp` package. Every `build_*` function
takes plain Python arguments and returns a plain dict describing the HTTP
request to make:

    {"method": "GET" | "POST", "url": "<full URL>", "params": {...} | None,
     "json": {...} | None}

Nothing in this module reads or embeds secrets. All base URLs come from
environment variables (server-side keys live only inside the platform
containers, never here). The thin `call_*` wrappers at the bottom perform
the actual HTTP calls at runtime using `httpx`, and are never exercised by
the offline self-test.

Endpoint shapes were taken from the platform service docs in
`platform/.claude/services/`:
  - scraper.md       -> POST /v1/scrape, /v1/crawl, /v1/map, /v1/extract
  - tavily.md        -> POST /v1/search
  - google-places.md -> POST /v1/places/search_text, /v1/places/nearby
                         (place details endpoint is NOT documented as
                         implemented — see ASSUMPTIONS below)
  - reddit-gateway.md -> POST /v1/reddit/search, /v1/reddit/subreddit/posts,
                         GET /v1/reddit/post/{id}, GET
                         /v1/reddit/subreddit/{name}/info,
                         POST /v1/reddit/saved/search

ASSUMPTIONS (doc was ambiguous or silent):
  - google-places.md's capability table marks "Place details (hours, website,
    phone)" as `available-upstream` (not yet exposed by the gateway). The task
    still asks for a `place_details(place_id)` tool, so this module builds a
    request to `GET /v1/places/details` with `place_id` as a query param, by
    analogy with the Google Places API's own `place_id` semantics. This
    endpoint is NOT confirmed to exist on the live gateway; flag before use.
  - The doc's worked Python example for Places hits a generic `POST /search`
    endpoint with a Bearer token supplied by the *caller*. The capability
    table (the more current section) lists the real implemented paths as
    `POST /v1/places/search_text` and `POST /v1/places/nearby` with the key
    held server-side. This module follows the capability table and does not
    send any Authorization header — consistent with "no secrets" and with
    every other service in this plugin.
  - `web_crawl`/`web_map`/`web_extract` request bodies are built directly
    from the JSON examples in scraper.md.
"""

from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urljoin

DEFAULT_SCRAPE_BASE = "https://scrape.platform.ibbytech.com"
DEFAULT_TAVILY_BASE = "https://tavily.platform.ibbytech.com"
DEFAULT_PLACES_BASE = "https://places.platform.ibbytech.com"
DEFAULT_REDDIT_BASE = "https://reddit.platform.ibbytech.com"


def _scrape_base() -> str:
    return os.environ.get("PLATFORM_SCRAPE_BASE", DEFAULT_SCRAPE_BASE).rstrip("/")


def _tavily_base() -> str:
    return os.environ.get("PLATFORM_TAVILY_BASE", DEFAULT_TAVILY_BASE).rstrip("/")


def _places_base() -> str:
    return os.environ.get("PLATFORM_PLACES_BASE", DEFAULT_PLACES_BASE).rstrip("/")


def _reddit_base() -> str:
    return os.environ.get("PLATFORM_REDDIT_BASE", DEFAULT_REDDIT_BASE).rstrip("/")


def _join(base: str, path: str) -> str:
    return f"{base}{path}"


# ---------------------------------------------------------------------------
# Scraper — scraper.md
# ---------------------------------------------------------------------------

def build_web_scrape(url: str, formats: Optional[list[str]] = None) -> dict[str, Any]:
    """Build a POST /v1/scrape request (scraper.md)."""
    return {
        "method": "POST",
        "url": _join(_scrape_base(), "/v1/scrape"),
        "params": None,
        "json": {"url": url, "formats": formats or ["markdown"]},
    }


def build_web_crawl(
    url: str, limit: int = 20, max_depth: int = 2, formats: Optional[list[str]] = None
) -> dict[str, Any]:
    """Build a POST /v1/crawl request (scraper.md).

    Note: scraper.md documents max_depth=1 as a known quirk (only root URL
    is crawled) — the platform API defaults to max_depth=2, which this
    helper mirrors.
    """
    return {
        "method": "POST",
        "url": _join(_scrape_base(), "/v1/crawl"),
        "params": None,
        "json": {
            "url": url,
            "max_depth": max_depth,
            "limit": limit,
            "formats": formats or ["markdown"],
        },
    }


def build_web_map(url: str, limit: int = 500) -> dict[str, Any]:
    """Build a POST /v1/map request (scraper.md)."""
    return {
        "method": "POST",
        "url": _join(_scrape_base(), "/v1/map"),
        "params": None,
        "json": {"url": url, "limit": limit},
    }


def build_web_extract(
    urls: list[str],
    prompt: Optional[str] = None,
    schema_def: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Build a POST /v1/extract request (scraper.md).

    Degraded upstream per scraper.md (requires OPENAI_API_KEY on the node) —
    the request shape is still built and callable; runtime errors from the
    dependency are surfaced through the standard error handling in the
    server tool.
    """
    body: dict[str, Any] = {"urls": urls}
    if prompt is not None:
        body["prompt"] = prompt
    if schema_def is not None:
        body["schema_def"] = schema_def
    return {
        "method": "POST",
        "url": _join(_scrape_base(), "/v1/extract"),
        "params": None,
        "json": body,
    }


# ---------------------------------------------------------------------------
# Tavily — tavily.md
# ---------------------------------------------------------------------------

def build_web_search(
    query: str,
    max_results: int = 5,
    include_domains: Optional[list[str]] = None,
    search_depth: str = "basic",
) -> dict[str, Any]:
    """Build a POST /v1/search request (tavily.md)."""
    body: dict[str, Any] = {
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
    }
    if include_domains:
        body["include_domains"] = include_domains
    return {
        "method": "POST",
        "url": _join(_tavily_base(), "/v1/search"),
        "params": None,
        "json": body,
    }


# ---------------------------------------------------------------------------
# Google Places — google-places.md
# ---------------------------------------------------------------------------

def build_places_search(
    text_query: str,
    lat: float,
    lng: float,
    radius_m: Optional[int] = None,
    max_results: Optional[int] = None,
    region_code: Optional[str] = None,
    language_code: Optional[str] = None,
) -> dict[str, Any]:
    """Build a POST /v1/places/search_text request.

    Field names are DEFINITIVE — taken from the gateway's own source
    (app.py, route v1_places_search_text). This is an ANCHORED text search:
    the service requires a location anchor (`lat`/`lng`) in addition to the
    query, and returns HTTP 400 "Missing: lat/lng (anchor required)"
    without it.

    Required body fields: `text_query`, `lat`, `lng`.
    Optional body fields (omitted when None): `radius_m`, `max_results`,
    `region_code`, `language_code`.
    """
    body: dict[str, Any] = {"text_query": text_query, "lat": lat, "lng": lng}
    if radius_m is not None:
        body["radius_m"] = radius_m
    if max_results is not None:
        body["max_results"] = max_results
    if region_code is not None:
        body["region_code"] = region_code
    if language_code is not None:
        body["language_code"] = language_code
    return {
        "method": "POST",
        "url": _join(_places_base(), "/v1/places/search_text"),
        "params": None,
        "json": body,
    }


def build_places_nearby(
    included_types: list[str],
    lat: float,
    lng: float,
    radius_m: Optional[int] = None,
    max_results: Optional[int] = None,
    region_code: Optional[str] = None,
    language_code: Optional[str] = None,
) -> dict[str, Any]:
    """Build a POST /v1/places/nearby request.

    Field names are DEFINITIVE — taken from the gateway's own source
    (app.py, google_places_nearby_search).

    Required body fields: `included_types` (a LIST of place-type strings),
    `lat`, `lng`.
    Optional body fields (omitted when None): `radius_m`, `max_results`,
    `region_code`, `language_code`.
    """
    body: dict[str, Any] = {
        "included_types": included_types,
        "lat": lat,
        "lng": lng,
    }
    if radius_m is not None:
        body["radius_m"] = radius_m
    if max_results is not None:
        body["max_results"] = max_results
    if region_code is not None:
        body["region_code"] = region_code
    if language_code is not None:
        body["language_code"] = language_code
    return {
        "method": "POST",
        "url": _join(_places_base(), "/v1/places/nearby"),
        "params": None,
        "json": body,
    }


def build_place_details(place_id: str) -> dict[str, Any]:
    """Build a GET /v1/places/details request for a single place.

    ASSUMPTION: google-places.md lists place details as
    `available-upstream` (not yet exposed by the gateway as of the doc's
    last update). This builder targets a plausible path/param shape
    (`GET /v1/places/details?place_id=...`) so the tool has a working
    request builder ready for when the gateway exposes it, but it is NOT
    verified against a live endpoint. The caller-facing tool should
    surface a clear error if the gateway returns 404/501.
    """
    return {
        "method": "GET",
        "url": _join(_places_base(), "/v1/places/details"),
        "params": {"place_id": place_id},
        "json": None,
    }


# ---------------------------------------------------------------------------
# Reddit Gateway — reddit-gateway.md
# ---------------------------------------------------------------------------

def build_reddit_read(
    target: str,
    mode: str = "search",
    subreddit: Optional[str] = None,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 25,
) -> dict[str, Any]:
    """Build a request for reading Reddit content (reddit-gateway.md).

    `mode` selects which documented endpoint to use:
      - "search"    -> POST /v1/reddit/search        (target = query string)
      - "subreddit" -> POST /v1/reddit/subreddit/posts (target = subreddit name)
      - "post"      -> GET  /v1/reddit/post/{id}      (target = post id)
      - "info"      -> GET  /v1/reddit/subreddit/{name}/info (target = subreddit name)
      - "saved"     -> POST /v1/reddit/saved/search   (target = query string)
    """
    base = _reddit_base()
    if mode == "search":
        body: dict[str, Any] = {
            "query": target,
            "sort": sort,
            "time_filter": time_filter,
            "limit": limit,
        }
        if subreddit:
            body["subreddit"] = subreddit
        return {
            "method": "POST",
            "url": _join(base, "/v1/reddit/search"),
            "params": None,
            "json": body,
        }
    if mode == "subreddit":
        body = {
            "subreddit": target,
            "sort": sort,
            "time_filter": time_filter,
            "limit": limit,
        }
        return {
            "method": "POST",
            "url": _join(base, "/v1/reddit/subreddit/posts"),
            "params": None,
            "json": body,
        }
    if mode == "post":
        return {
            "method": "GET",
            "url": _join(base, f"/v1/reddit/post/{target}"),
            "params": None,
            "json": None,
        }
    if mode == "info":
        return {
            "method": "GET",
            "url": _join(base, f"/v1/reddit/subreddit/{target}/info"),
            "params": None,
            "json": None,
        }
    if mode == "saved":
        return {
            "method": "POST",
            "url": _join(base, "/v1/reddit/saved/search"),
            "params": None,
            "json": {"query": target, "limit": limit},
        }
    raise ValueError(f"Unknown reddit_read mode: {mode!r}")


# ---------------------------------------------------------------------------
# Runtime HTTP call wrappers (thin; used only when the server actually runs)
# ---------------------------------------------------------------------------

def call(request: dict[str, Any], timeout: float = 30.0) -> dict[str, Any]:
    """Execute a built request dict with httpx and return a structured
    result. Never raises — non-200 responses and exceptions are converted
    into an {"error": ...} payload so MCP tools can return a clear error
    instead of crashing.
    """
    import httpx

    method = request["method"]
    url = request["url"]
    params = request.get("params")
    json_body = request.get("json")

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(method, url, params=params, json=json_body)
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
