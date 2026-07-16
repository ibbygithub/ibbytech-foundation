"""Offline, deterministic self-test for the ibbytech-core bundled MCP
servers (Unit 5).

Tests ONLY the pure request builders in `_platform_api` and `_loki_api` —
no network calls are made. Also attempts to import the two FastMCP server
modules; if the `mcp` package is not installed, that specific check is
skipped (printed as SKIP) rather than failing the whole suite.

Run with: python selftest_mcp.py
"""

from __future__ import annotations

import sys
import traceback
from typing import Any, Callable

import _loki_api as loki_api
import _platform_api as api

passed = 0
failed = 0
skipped = 0


def check(name: str, condition: bool, detail: str = "") -> None:
    global passed, failed
    if condition:
        passed += 1
        print(f"PASS: {name}")
    else:
        failed += 1
        print(f"FAIL: {name} {('- ' + detail) if detail else ''}")


def run(name: str, fn: Callable[[], None]) -> None:
    global failed
    try:
        fn()
    except AssertionError as exc:
        failed += 1
        print(f"FAIL: {name} - {exc}")
    except Exception:
        failed += 1
        print(f"FAIL: {name} - unexpected exception:\n{traceback.format_exc()}")


def no_secret_material(obj: Any) -> bool:
    """Recursively check that no secret-looking material appears anywhere
    in a built request (only base URLs / plain params should be present).
    """
    banned_substrings = [
        "api_key", "apikey", "token", "secret", "bearer", "password",
        "authorization",
    ]
    text = repr(obj).lower()
    return not any(b in text for b in banned_substrings)


# ---------------------------------------------------------------------------
# _platform_api — Scraper
# ---------------------------------------------------------------------------

def test_web_scrape():
    req = api.build_web_scrape("https://example.com/article")
    check("web_scrape: method", req["method"] == "POST")
    check("web_scrape: url", req["url"] == "https://scrape.platform.ibbytech.com/v1/scrape")
    check("web_scrape: default formats", req["json"]["formats"] == ["markdown"])
    check("web_scrape: url in body", req["json"]["url"] == "https://example.com/article")
    check("web_scrape: no secrets", no_secret_material(req))


def test_web_crawl():
    req = api.build_web_crawl("https://docs.example.com", limit=20, max_depth=2)
    check("web_crawl: method", req["method"] == "POST")
    check("web_crawl: path", req["url"].endswith("/v1/crawl"))
    check("web_crawl: max_depth", req["json"]["max_depth"] == 2)
    check("web_crawl: limit", req["json"]["limit"] == 20)
    check("web_crawl: no secrets", no_secret_material(req))


def test_web_map():
    req = api.build_web_map("https://example.com", limit=500)
    check("web_map: method", req["method"] == "POST")
    check("web_map: path", req["url"].endswith("/v1/map"))
    check("web_map: limit", req["json"]["limit"] == 500)


def test_web_extract():
    req = api.build_web_extract(
        ["https://example.com/products"], prompt="Extract product names and prices."
    )
    check("web_extract: method", req["method"] == "POST")
    check("web_extract: path", req["url"].endswith("/v1/extract"))
    check("web_extract: urls list", req["json"]["urls"] == ["https://example.com/products"])
    check("web_extract: prompt", req["json"]["prompt"] == "Extract product names and prices.")


# ---------------------------------------------------------------------------
# _platform_api — Tavily
# ---------------------------------------------------------------------------

def test_web_search():
    req = api.build_web_search("tabelog ramen")
    check("web_search: method is POST", req["method"] == "POST")
    check(
        "web_search: url is tavily search path",
        req["url"] == "https://tavily.platform.ibbytech.com/v1/search",
    )
    check("web_search: query in body", req["json"]["query"] == "tabelog ramen")
    check("web_search: default max_results", req["json"]["max_results"] == 5)
    check("web_search: no secrets", no_secret_material(req))

    req2 = api.build_web_search("ramen", include_domains=["tabelog.com"])
    check("web_search: include_domains passed through", req2["json"]["include_domains"] == ["tabelog.com"])


# ---------------------------------------------------------------------------
# _platform_api — Google Places
# ---------------------------------------------------------------------------

def test_places_search():
    req = api.build_places_search("best rated ramen", 34.6937, 135.5023)
    check("places_search: method", req["method"] == "POST")
    check("places_search: path", req["url"].endswith("/v1/places/search_text"))
    check("places_search: uses text_query field", req["json"]["text_query"] == "best rated ramen")
    check("places_search: no legacy 'query' field", "query" not in req["json"])
    check("places_search: lat anchor required", req["json"]["lat"] == 34.6937)
    check("places_search: lng anchor required", req["json"]["lng"] == 135.5023)
    check("places_search: optional None fields omitted",
          all(k not in req["json"] for k in ("radius_m", "max_results", "region_code", "language_code")))
    check("places_search: no legacy 'location' field", "location" not in req["json"])
    check("places_search: no secrets (no bearer token)", no_secret_material(req))

    req2 = api.build_places_search("ramen", 34.6, 135.5, radius_m=1000, max_results=10)
    check("places_search: radius_m passed through", req2["json"]["radius_m"] == 1000)
    check("places_search: max_results passed through", req2["json"]["max_results"] == 10)


def test_places_nearby():
    req = api.build_places_nearby(["restaurant"], 34.6937, 135.5023, radius_m=1000)
    check("places_nearby: method", req["method"] == "POST")
    check("places_nearby: path", req["url"].endswith("/v1/places/nearby"))
    check("places_nearby: included_types is a list", req["json"]["included_types"] == ["restaurant"])
    check("places_nearby: lat anchor required", req["json"]["lat"] == 34.6937)
    check("places_nearby: lng anchor required", req["json"]["lng"] == 135.5023)
    check("places_nearby: radius_m passed through", req["json"]["radius_m"] == 1000)
    check("places_nearby: no legacy 'type'/'location'/'radius' fields",
          all(k not in req["json"] for k in ("type", "location", "radius")))
    check("places_nearby: optional None fields omitted",
          all(k not in req["json"] for k in ("max_results", "region_code", "language_code")))


def test_place_details():
    req = api.build_place_details("ChIJexample123")
    check("place_details: method", req["method"] == "GET")
    check("place_details: path", req["url"].endswith("/v1/places/details"))
    check("place_details: place_id param", req["params"]["place_id"] == "ChIJexample123")


# ---------------------------------------------------------------------------
# _platform_api — Reddit Gateway
# ---------------------------------------------------------------------------

def test_reddit_search():
    req = api.build_reddit_read("ramen hidden gem", mode="search", subreddit="japan", sort="top", time_filter="year", limit=10)
    check("reddit search: method", req["method"] == "POST")
    check("reddit search: path", req["url"].endswith("/v1/reddit/search"))
    check("reddit search: query", req["json"]["query"] == "ramen hidden gem")
    check("reddit search: subreddit", req["json"]["subreddit"] == "japan")
    check("reddit search: sort", req["json"]["sort"] == "top")


def test_reddit_post():
    req = api.build_reddit_read("abc123", mode="post")
    check("reddit post: method", req["method"] == "GET")
    check("reddit post: path", req["url"].endswith("/v1/reddit/post/abc123"))


def test_reddit_info():
    req = api.build_reddit_read("japan", mode="info")
    check("reddit info: method", req["method"] == "GET")
    check("reddit info: path", req["url"].endswith("/v1/reddit/subreddit/japan/info"))


def test_reddit_saved():
    req = api.build_reddit_read("local Japanese restaurant authentic not tourist", mode="saved", limit=10)
    check("reddit saved: method", req["method"] == "POST")
    check("reddit saved: path", req["url"].endswith("/v1/reddit/saved/search"))
    check("reddit saved: limit", req["json"]["limit"] == 10)


def test_reddit_invalid_mode():
    try:
        api.build_reddit_read("x", mode="bogus")
        check("reddit invalid mode raises", False, "expected ValueError")
    except ValueError:
        check("reddit invalid mode raises", True)


# ---------------------------------------------------------------------------
# _loki_api
# ---------------------------------------------------------------------------

def test_parse_duration():
    check("parse_duration 30m", loki_api.parse_duration_to_seconds("30m") == 1800)
    check("parse_duration 1h", loki_api.parse_duration_to_seconds("1h") == 3600)
    check("parse_duration 2d", loki_api.parse_duration_to_seconds("2d") == 172800)
    try:
        loki_api.parse_duration_to_seconds("bogus")
        check("parse_duration invalid raises", False, "expected ValueError")
    except ValueError:
        check("parse_duration invalid raises", True)


def test_build_query_range():
    now_ns = 1_700_000_000_000_000_000
    req = loki_api.build_query_range('{service="scraper"}', since="1h", limit=100, now_ns=now_ns)
    check("query_range: method", req["method"] == "GET")
    check("query_range: url", req["url"] == "http://192.168.71.220:3100/loki/api/v1/query_range")
    check("query_range: query param", req["params"]["query"] == '{service="scraper"}')
    check("query_range: limit param", req["params"]["limit"] == 100)
    expected_start = now_ns - 3600 * 1_000_000_000
    check(
        "query_range: start = now - 1h",
        int(req["params"]["start"]) == expected_start,
        f"got {req['params']['start']}",
    )
    check("query_range: end = now", int(req["params"]["end"]) == now_ns)
    check("query_range: no secrets", no_secret_material(req))


def test_build_service_selector():
    check(
        "service selector shape",
        loki_api.build_service_selector("platform-tavily") == '{service="platform-tavily"}',
    )


def test_recent_service_logs():
    now_ns = 1_700_000_000_000_000_000
    req = loki_api.build_recent_service_logs("platform-tavily", minutes=15, limit=200, now_ns=now_ns)
    check("recent_service_logs: method", req["method"] == "GET")
    check(
        "recent_service_logs: selector in query",
        req["params"]["query"] == '{service="platform-tavily"}',
    )
    start = int(req["params"]["start"])
    end = int(req["params"]["end"])
    delta_seconds = (end - start) / 1_000_000_000
    check(
        "recent_service_logs: start/end ~15 min apart",
        abs(delta_seconds - 15 * 60) < 1,
        f"got {delta_seconds}s",
    )
    check("recent_service_logs: no secrets", no_secret_material(req))


# ---------------------------------------------------------------------------
# Server module import check (best-effort — mcp package may not be installed)
# ---------------------------------------------------------------------------

def test_server_imports():
    global skipped
    try:
        import mcp.server.fastmcp  # noqa: F401
    except ImportError:
        skipped += 1
        print("SKIP: mcp package not installed (server import not verified)")
        return

    try:
        import platform_retrieval  # noqa: F401
        import homelab_logs  # noqa: F401
        check("server modules import cleanly", True)
    except Exception:
        check("server modules import cleanly", False, traceback.format_exc())


def main() -> int:
    run("web_scrape", test_web_scrape)
    run("web_crawl", test_web_crawl)
    run("web_map", test_web_map)
    run("web_extract", test_web_extract)
    run("web_search", test_web_search)
    run("places_search", test_places_search)
    run("places_nearby", test_places_nearby)
    run("place_details", test_place_details)
    run("reddit_search", test_reddit_search)
    run("reddit_post", test_reddit_post)
    run("reddit_info", test_reddit_info)
    run("reddit_saved", test_reddit_saved)
    run("reddit_invalid_mode", test_reddit_invalid_mode)
    run("parse_duration", test_parse_duration)
    run("build_query_range", test_build_query_range)
    run("build_service_selector", test_build_service_selector)
    run("recent_service_logs", test_recent_service_logs)
    run("server_imports", test_server_imports)

    total = passed + failed
    print()
    print(f"{passed}/{total} passed" + (f" ({skipped} skipped)" if skipped else ""))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
