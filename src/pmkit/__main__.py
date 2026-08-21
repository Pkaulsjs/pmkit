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
    args = ap.parse_args()

    if args.cmd == "scan":
        from pmkit.arb import scan_binary_arbs, scan_negrisk_events
        arbs = scan_binary_arbs(max_pages=args.pages, threshold=args.threshold)
        print(json.dumps({"binary_arbs": len(arbs), "results": arbs[:5]}, indent=1))
        evs = scan_negrisk_events(max_pages=max(args.pages * 3, 30), buffer=args.negrisk_buffer)
        print(json.dumps({"negrisk_deviations": len(evs), "top": evs[:5]}, indent=1))
        return 0

    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
