"""CLI: python -m pmkit <command>"""
import argparse
import json
import sys


def main():
    ap = argparse.ArgumentParser(prog="pmkit", description="Polymarket analysis toolkit")
    sub = ap.add_subparsers(dest="cmd")
    p_scan = sub.add_parser("scan", help="scan for arb candidates")
    p_scan.add_argument("--pages", type=int, default=10)
    p_scan.add_argument("--threshold", type=float, default=0.995)
    p_scan.add_argument("--negrisk-buffer", type=float, default=0.02)
    p_watch = sub.add_parser("watch", help="poll a book and log to CSV")
    p_watch.add_argument("--token", required=True)
    p_watch.add_argument("--out", default="watch.csv")
    p_watch.add_argument("--interval", type=float, default=5.0)
    p_watch.add_argument("--duration", type=float, default=60.0)
    p_mk = sub.add_parser("markets", help="browse active markets")
    p_mk.add_argument("--min-volume", type=float, default=1000.0)
    p_mk.add_argument("--limit", type=int, default=15)
    p_mk.add_argument("--q", default=None, help="substring filter on question")
    args = ap.parse_args()

    if args.cmd == "scan":
        from pmkit.arb import scan_binary_arbs, scan_negrisk_events
        arbs = scan_binary_arbs(max_pages=args.pages, threshold=args.threshold)
        print(json.dumps({"binary_arbs": len(arbs), "results": arbs[:5]}, indent=1))
        evs = scan_negrisk_events(max_pages=max(args.pages * 3, 30), buffer=args.negrisk_buffer)
        print(json.dumps({"negrisk_deviations": len(evs), "top": evs[:5]}, indent=1))
        return 0

    if args.cmd == "markets":
        from pmkit.gamma import iter_markets
        rows = []
        for m in iter_markets(max_pages=10):
            try:
                vol = float(m.get("volume24hr") or 0)
            except Exception:
                continue
            if vol < args.min_volume:
                continue
            q = m.get("question") or ""
            if args.q and args.q.lower() not in q.lower():
                continue
            try:
                prices = [round(float(x), 3) for x in json.loads(m.get("outcomePrices") or "[]")]
            except Exception:
                prices = []
            rows.append({"q": q[:70], "vol24h": round(vol), "prices": prices})
            if len(rows) >= args.limit:
                break
        print(json.dumps(rows, indent=1))
        return 0

    if args.cmd == "watch":
        from pmkit.watch import watch
        rows = watch(args.token, out_csv=args.out, interval=args.interval, duration=args.duration)
        print(f"logged {len(rows)} rows -> {args.out}")
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
