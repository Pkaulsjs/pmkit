"""Record a live book sample for the backtest demo."""
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pmkit.gamma import list_markets
from pmkit.watch import watch

rows = list_markets(limit=100)
best = None
for m in rows:
    try:
        vol = float(m.get("volume24hr") or 0)
    except Exception:
        continue
    toks = json.loads(m.get("clobTokenIds") or "[]")
    if len(toks) == 2 and (best is None or vol > best[0]):
        best = (vol, toks[0])
if not best:
    raise SystemExit("no active markets")
print(f"recording {best[1][:16]}... (24h vol ${int(best[0]):,})")
watch(best[1], out_csv="data/sample_watch.csv", interval=5, duration=600)
