"""Read-only arbitrage scanners."""
import json
import time

from pmkit.gamma import iter_markets, list_events
from pmkit.clob import best_bid


def scan_binary_arbs(max_pages=10, threshold=0.995):
    """Binary markets where YES+NO midpoint sum < threshold."""
    found = []
    for m in iter_markets(max_pages=max_pages):
        try:
            prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except Exception:
            continue
        if len(prices) != 2:
            continue
        s = sum(prices)
        if s < threshold:
            found.append({
                "question": m.get("question"),
                "sum": s,
                "edge_per_share": round(1 - s, 4),
            })
    return found


def scan_negrisk_events(max_pages=30, buffer=0.02):
    """negRisk events whose sub-market midpoints sum above 1+buffer."""
    found = []
    offset = 0
    for _ in range(max_pages):
        evs = list_events(offset=offset)
        if not evs:
            return found
        for ev in evs:
            mkts = ev.get("markets") or []
            nr = [m for m in mkts if m.get("negRisk")]
            if len(nr) < 3 or len(nr) != len(mkts):
                continue
            s = 0.0
            ok = True
            for m in nr:
                try:
                    prices = json.loads(m.get("outcomePrices") or "[]")
                except Exception:
                    ok = False
                    break
                if len(prices) != 2:
                    ok = False
                    break
                s += float(prices[0])
            if ok and (s - 1.0) > buffer:
                found.append({
                    "event": ev.get("title"),
                    "slug": ev.get("slug"),
                    "n_markets": len(nr),
                    "sum_pyes": round(s, 4),
                })
        if len(evs) < 100:
            return found
        offset += 100
        time.sleep(0.1)
    return found
