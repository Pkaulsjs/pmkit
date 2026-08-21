"""Public CLOB API client: order books and prices."""
import json
import urllib.request

CLOB = "https://clob.polymarket.com"
UA = {"User-Agent": "pmkit/0.1 (market analysis)"}


def _get_raw(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get_book(token_id):
    """Return the full order book dict for a token id."""
    return _get_raw(CLOB + "/book?token_id=" + str(token_id))


def best_bid(token_id):
    b = get_book(token_id)
    bids = b.get("bids") or []
    if not bids:
        return (0.0, 0.0)
    best = max(bids, key=lambda x: float(x["price"]))
    return (float(best["price"]), float(best["size"]))


def best_ask(token_id):
    b = get_book(token_id)
    asks = b.get("asks") or []
    if not asks:
        return (1.0, 0.0)
    best = min(asks, key=lambda x: float(x["price"]))
    return (float(best["price"]), float(best["size"]))


def midpoint(token_id):
    bb, _ = best_bid(token_id)
    ba, _ = best_ask(token_id)
    if bb <= 0 or ba >= 1:
        return None
    return (bb + ba) / 2
