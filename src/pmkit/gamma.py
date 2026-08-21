"""Public Gamma API client: markets and events."""
import json
import time
import urllib.error
import urllib.request

GAMMA = "https://gamma-api.polymarket.com"
UA = {"User-Agent": "pmkit/0.1 (market analysis)"}


def _get_raw(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def _get_pages(path, limit=100, offset=0):
    """GET a paginated collection; returns [] on 422 (past last page)."""
    sep = "&" if "?" in path else "?"
    url = f"{GAMMA}{path}{sep}limit={limit}&offset={offset}"
    try:
        return _get_raw(url)
    except urllib.error.HTTPError as e:
        if e.code == 422:
            return []
        raise


def list_markets(limit=100, offset=0):
    return _get_pages("/markets", limit=limit, offset=offset)


def iter_markets(max_pages=10):
    offset = 0
    for _ in range(max_pages):
        rows = list_markets(offset=offset)
        if not rows:
            return
        yield from rows
        if len(rows) < 100:
            return
        offset += 100
        time.sleep(0.15)


def list_events(limit=100, offset=0):
    return _get_pages("/events?active=true&closed=false", limit=limit, offset=offset)
