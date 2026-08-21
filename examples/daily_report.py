"""Generate/update the daily market-quality report from live scans."""
import json
import sys, os
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from pmkit.gamma import list_markets, list_events
from pmkit.arb import scan_negrisk_events

DOCS = os.path.join(os.path.dirname(__file__), "..", "docs")


def snapshot():
    rows = list_markets(limit=250)
    binary = 0
    spreads = 0
    total_vol = 0.0
    top = []
    for m in rows:
        try:
            prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
            vol = float(m.get("volume24hr") or 0)
        except Exception:
            continue
        if len(prices) != 2:
            continue
        binary += 1
        total_vol += vol
        if sum(prices) < 0.995:
            spreads += 1
        if len(top) < 5:
            top.append((m.get("question", "?")[:55], int(vol)))
    evs = scan_negrisk_events(max_pages=10, buffer=0.02)
    return {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "binary_scanned": binary,
        "binary_spreads": spreads,
        "vol24h_total": int(total_vol),
        "negrisk_deviations": len(evs),
        "top_deviation": max((e["sum_pyes"] - 1 for e in evs), default=0),
        "top_markets": top,
    }


def render(snap):
    lines = [
        f"# Market Quality Report - {snap['ts']}",
        "",
        "Auto-generated hourly by [pmkit](https://github.com/Pkaulsjs/pmkit). Read-only scan of Polymarket's public APIs.",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Binary markets scanned | {snap['binary_scanned']} |",
        f"| YES+NO spreads < 0.995 | {snap['binary_spreads']} |",
        f"| negRisk groups deviating > 2% | {snap['negrisk_deviations']} |",
        f"| Largest deviation | +{snap['top_deviation']:.1%} |",
        f"| Trailing 24h volume (sampled) | ${snap['vol24h_total']:,} |",
        "",
        "## Most active markets right now",
        "",
    ]
    for q, v in snap["top_markets"]:
        lines.append(f"- {q} - ${v:,}/24h")
    lines += [
        "",
        "Deviations are midpoint artifacts pending book-depth validation - see the",
        "[phantom-arb writeup](https://pkaulsjs.github.io/pmkit/scan-arbitrage-python.html).",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    snap = snapshot()
    os.makedirs(DOCS, exist_ok=True)
    path = os.path.join(DOCS, "report.md")
    open(path, "w", encoding="utf-8").write(render(snap))
    # append to history log
    hist = os.path.join(DOCS, "report-history.jsonl")
    with open(hist, "a", encoding="utf-8") as f:
        f.write(json.dumps(snap) + "\n")
    print("report written:", snap["ts"], "| deviations:", snap["negrisk_deviations"])
