"""Scan for binary and negRisk arb candidates. Read-only."""
import json
from pmkit.arb import scan_binary_arbs, scan_negrisk_events

if __name__ == "__main__":
    print("scanning binary markets...")
    arbs = scan_binary_arbs(max_pages=10)
    print(f"binary arbs found: {len(arbs)}")
    for a in arbs[:10]:
        print(json.dumps(a))

    print("scanning negRisk events...")
    evs = scan_negrisk_events(max_pages=30)
    print(f"negrisk deviations found: {len(evs)}")
    for e in evs[:10]:
        print(json.dumps(e))
