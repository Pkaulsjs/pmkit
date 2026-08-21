"""Record a live book sample for the backtest demo."""
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pmkit.gamma import list_markets
from pmkit.clob import get_book
from pmkit.watch import watch


def pick_live_market():
    rows = list_markets(limit=250)
    candidates = []
    for m in rows:
        try:
            vol = float(m.get("volume24hr") or 0)
        except Exception:
            continue
        if not m.get("acceptingOrders", False):
            continue
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if len(toks) == 2:
            candidates.append((vol, toks[0], m.get("question", "?")))
    candidates.sort(reverse=True)
    # pre-flight: confirm the book endpoint actually serves this token
    for vol, tok, q in candidates[:5]:
        try:
            get_book(tok)
            return vol, tok, q
        except Exception:
            continue
    raise SystemExit("no tradeable market found in top 5")


if __name__ == "__main__":
    vol, tok, q = pick_live_market()
    print(f"recording: {q[:60]} (24h vol ${int(vol):,})")
    watch(tok, out_csv="data/sample_watch.csv", interval=5, duration=600)
