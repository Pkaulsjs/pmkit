"""Paper-trade against a live market's real book prices. No keys needed."""
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pmkit.gamma import list_markets
from pmkit.clob import best_bid, best_ask
from pmkit.paper import PaperLedger

if __name__ == "__main__":
    # pick the highest-volume active binary market right now
    rows = list_markets(limit=100)
    best = None
    for m in rows:
        try:
            vol = float(m.get("volume24hr") or 0)
        except Exception:
            continue
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if len(toks) == 2 and (best is None or vol > best[0]):
            best = (vol, toks[0], m.get("question"))
    if not best:
        raise SystemExit("no active markets found")
    vol, token, question = best
    print(f"market: {question[:60]} (24h vol ${int(vol):,})")

    ledger = PaperLedger(starting_cash=1000.0)
    bb = best_bid(token)
    ba = best_ask(token)
    print(f"best bid: {bb}  best ask: {ba}")
    if ledger.buy(token, 10.0, ba[0]):
        print("paper buy filled at ask:", round(ba[0], 3))
    print(f"equity: {ledger.equity():.2f}")
