# pmkit - Polymarket Dev Kit

A clean, documented Python toolkit for building read-only market analysis
and paper-trading tools on Polymarket's public APIs.

## What's inside

| Module | What it does |
|---|---|
| `pmkit.gamma` | Markets & events fetcher (public Gamma API) |
| `pmkit.clob` | Order-book depth, best bid/ask, midpoint prices |
| `pmkit.arb` | Binary YES+NO spread scanner + negative-risk event scanner with book-depth validation |
| `pmkit.paper` | Paper-trading ledger engine (no keys, no funds, pure simulation) |
| `pmkit.config` | Typed configuration with safe defaults |

## Honest positioning

This is **infrastructure and analysis tooling**. It places no order routing,
touches no funds, and makes **no profit claims**. Prediction-market trading
carries risk; nothing here is financial advice. The value is clean code,
working examples, and validated scanning logic -- not promises.

## Quickstart

```python
from pmkit.arb import scan_binary_arbs, scan_negrisk_events

# Binary markets where YES+NO < threshold
arbs = scan_binary_arbs(max_pages=10, threshold=0.995)
for a in arbs:
    print(a.question, a.edge_per_share)

# Negative-risk events whose sub-market mids sum > 1+buffer
events = scan_negrisk_events(max_pages=30, buffer=0.02)
```

## Install

```bash
pip install -e .
```

Python 3.10+. Zero hard dependencies (stdlib only).

## License

Commercial license for purchasers. See LICENSE.
