"""Live book watcher: poll a token's book and log to CSV."""
import csv
import time

from pmkit.clob import get_book


def _best(book):
    bids = book.get("bids") or []
    asks = book.get("asks") or []
    bb = max(bids, key=lambda x: float(x["price"])) if bids else None
    ba = min(asks, key=lambda x: float(x["price"])) if asks else None
    return (
        float(bb["price"]) if bb else 0.0,
        float(ba["price"]) if ba else 1.0,
        int(float(bb["size"])) if bb else 0,
        int(float(ba["size"])) if ba else 0,
    )


def watch(token_id, out_csv="watch.csv", interval=5.0, duration=60.0, quiet=True):
    """Poll the book every interval seconds for duration seconds."""
    rows = []
    start = time.time()
    while time.time() - start < duration:
        try:
            bb, ba, bbs, bas = _best(get_book(token_id))
            mid = (bb + ba) / 2 if bb > 0 and ba < 1 else None
            rows.append([round(time.time(), 1), bb, bbs, ba, bas, mid])
            if not quiet:
                print(f"bid {bb:.3f} x{bbs} | ask {ba:.3f} x{bas} | mid {mid}")
        except Exception as e:
            rows.append([round(time.time(), 1), "ERR", str(e)[:40], "", "", None])
        time.sleep(interval)
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts", "best_bid", "bid_size", "best_ask", "ask_size", "mid"])
        w.writerows(rows)
    return rows
