"""Whale-watcher: surface large recent trades via the public data API."""
import json
import time
import urllib.request

DATA_API = "https://data-api.polymarket.com"
UA = {"User-Agent": "pmkit/0.1 (market analysis)"}


def _get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def recent_trades(market_hash=None, limit=100):
    """Recent trades across markets (optionally filtered by condition id)."""
    url = f"{DATA_API}/trades?limit={limit}"
    if market_hash:
        url += "&market=" + market_hash
    try:
        return _get(url)
    except Exception:
        return []


def whales(trades, min_usd=500.0):
    """Filter trades to those above a USD threshold."""
    out = []
    for t in trades:
        try:
            usd = float(t.get("size", 0)) * float(t.get("price", 0))
        except (TypeError, ValueError):
            continue
        if usd >= min_usd:
            t = dict(t)
            t["usd"] = round(usd, 2)
            out.append(t)
    out.sort(key=lambda x: -x["usd"])
    return out


def watch_whales(min_usd=500.0, interval=30.0, duration=300.0, on_whale=None):
    """Poll for large trades; call on_whale(trade) for each new one."""
    seen = set()
    end = time.time() + duration
    while time.time() < end:
        for t in whales(recent_trades(limit=100), min_usd=min_usd):
            tid = t.get("transactionHash")
            if tid and tid not in seen:
                seen.add(tid)
                if on_whale:
                    on_whale(t)
        time.sleep(interval)
