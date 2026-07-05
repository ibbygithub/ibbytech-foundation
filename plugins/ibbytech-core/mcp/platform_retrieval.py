"""platform-retrieval — stdio MCP server exposing read-only retrieval tools
against the IbbyTech platform's Scraper, Tavily, Google Places, and Reddit
Gateway services.

All requests are built by `_platform_api` (pure, no `mcp` dependency) and
executed via `_platform_api.call`. Base URLs come from environment
variables set in the plugin's `.mcp.json` — no API keys are read, held, or
forwarded by this server; every upstream key lives server-side inside the
platform containers.
"""

from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

import _platform_api as api

mcp = FastMCP("platform-retrieval")


@mcp.tool()
def web_scrape(url: str, formats: Optional[list[str]] = None) -> dict[str, Any]:
    """Scrape a single URL via the platform Scraper service (Firecrawl
    backend) and return markdown/HTML content plus metadata. `formats`
    defaults to ["markdown"]; pass ["markdown", "html"] for both. Errors
    (timeouts, non-200 responses) are returned as a structured error object
    rather than raising.
    """
    request = api.build_web_scrape(url, formats=formats)
    return api.call(request, timeout=90.0)


@mcp.tool()
def web_crawl(
    url: str,
    limit: int = 20,
    max_depth: int = 2,
    formats: Optional[list[str]] = None,
) -> dict[str, Any]:
    """Crawl up to `limit` pages starting from `url` via the platform
    Scraper service. Blocks until the crawl completes (the wrapper polls
    Firecrawl's async job internally, up to ~5 minutes). Use `max_depth >= 2`
    — depth 1 only returns the root URL (a known Firecrawl quirk).
    """
    request = api.build_web_crawl(url, limit=limit, max_depth=max_depth, formats=formats)
    return api.call(request, timeout=360.0)


@mcp.tool()
def web_map(url: str, limit: int = 500) -> dict[str, Any]:
    """Discover all URLs on a site without scraping content, via the
    platform Scraper service's map endpoint. Requires the site to expose a
    sitemap.xml or a configured search API; otherwise only the root URL is
    returned (documented Firecrawl limitation).
    """
    request = api.build_web_map(url, limit=limit)
    return api.call(request, timeout=90.0)


@mcp.tool()
def web_extract(
    url: str,
    prompt: Optional[str] = None,
    schema_def: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Extract structured data from a page using the platform Scraper
    service's LLM-based extraction endpoint. Provide either a natural
    language `prompt` or a JSON `schema_def` (or both). NOTE: this endpoint
    is documented as degraded on the platform (requires an LLM provider key
    configured on the node) — a failure here may reflect that upstream gap
    rather than a bad request.
    """
    request = api.build_web_extract([url], prompt=prompt, schema_def=schema_def)
    return api.call(request, timeout=120.0)


@mcp.tool()
def web_search(
    query: str,
    max_results: int = 5,
    include_domains: Optional[list[str]] = None,
) -> dict[str, Any]:
    """AI-native web search via the platform Tavily gateway. Supports
    kanji + English queries natively. Pass `include_domains` (e.g.
    ["tabelog.com"]) to restrict results to specific domains; restriction is
    best-effort per Tavily's own documented behavior.
    """
    request = api.build_web_search(query, max_results=max_results, include_domains=include_domains)
    return api.call(request, timeout=30.0)


@mcp.tool()
def places_search(
    text_query: str,
    lat: float,
    lng: float,
    radius_m: Optional[int] = None,
    max_results: Optional[int] = None,
    region_code: Optional[str] = None,
    language_code: Optional[str] = None,
) -> dict[str, Any]:
    """ANCHORED text search for places (businesses, POIs) via the platform
    Google Places gateway. A location anchor is REQUIRED: you must supply
    `lat` and `lng` in addition to `text_query` — the gateway returns HTTP
    400 without them. `radius_m`, `max_results`, `region_code`, and
    `language_code` are optional. The gateway holds the Google API key
    server-side — no key is sent or required by callers.
    """
    request = api.build_places_search(
        text_query,
        lat,
        lng,
        radius_m=radius_m,
        max_results=max_results,
        region_code=region_code,
        language_code=language_code,
    )
    return api.call(request, timeout=30.0)


@mcp.tool()
def place_details(place_id: str) -> dict[str, Any]:
    """Fetch details (hours, website, phone) for a specific place by its
    Google Places `place_id`. NOTE: the platform's google-places service doc
    lists this capability as not yet exposed by the gateway
    (`available-upstream`) as of its last update — this tool may return a
    404/501 error until the gateway adds the endpoint. Kept as a best-effort
    request builder so the tool is ready once available.
    """
    request = api.build_place_details(place_id)
    return api.call(request, timeout=30.0)


@mcp.tool()
def reddit_read(
    target: str,
    mode: str = "search",
    subreddit: Optional[str] = None,
    sort: str = "relevance",
    time_filter: str = "all",
    limit: int = 25,
) -> dict[str, Any]:
    """Read Reddit content via the platform's read-only Reddit Gateway (no
    Reddit credentials required). `mode` selects the operation:
      - "search"    — keyword search; `target` is the query (Unicode/kanji OK)
      - "subreddit" — browse a subreddit listing; `target` is the subreddit name
      - "post"      — fetch a post + its comments; `target` is the post id
      - "info"      — subreddit metadata; `target` is the subreddit name
      - "saved"     — semantic search over previously stored posts (pgvector);
                       `target` is the query, no live Reddit call is made
    `subreddit`, `sort`, `time_filter`, `limit` are only used by "search"/
    "subreddit" modes and mirror reddit-gateway.md's documented fields.
    """
    request = api.build_reddit_read(
        target,
        mode=mode,
        subreddit=subreddit,
        sort=sort,
        time_filter=time_filter,
        limit=limit,
    )
    return api.call(request, timeout=30.0)


if __name__ == "__main__":
    mcp.run()
