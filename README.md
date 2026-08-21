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
| `pmkit.stream` | Zero-dependency WebSocket streaming of live order-book events |
| `pmkit.whales` | Whale-watcher: surface large trades via the public data API |
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

## CLI

Example - live liquid markets at publish time:

```json
[
 {
  "q": "Will Graham Platner win the 2028 Democratic presidential nomination?",
  "vol24h": 221377,
  "prices": [
   0.002,
   0.999
  ]
 },
 {
  "q": "Will Abigail Spanberger win the 2028 Democratic presidential nominatio",
  "vol24h": 274095,
  "prices": [
   0.002,
```


```bash
python -m pmkit scan --pages 10              # arb scan (binary + negRisk)
python -m pmkit markets --min-volume 50000   # browse liquid markets
python -m pmkit watch --token <id> --interval 5   # poll a book to CSV
```

## Live streaming (no dependencies)

```python
from pmkit.stream import stream_market

stream_market(["<token_id>"], print, duration=60)  # prints live book events
```

A minimal RFC 6455 client implemented on raw sockets - no `websockets`,
no `aiohttp`, nothing to install.

## Install

```bash
pip install -e .
```

Python 3.10+. Zero hard dependencies (stdlib only).

## License

Commercial license for purchasers. See LICENSE.
