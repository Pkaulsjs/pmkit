"""Replay recorded book data (watch.csv) through simple strategies."""
import csv


def load_recording(path):
    rows = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({
                    "ts": float(r["ts"]),
                    "bid": float(r["best_bid"]),
                    "ask": float(r["best_ask"]),
                })
            except (KeyError, ValueError):
                continue
    return [r for r in rows if r["bid"] > 0 and r["ask"] < 1]


class Backtest:
    """Single-token backtest over a bid/ask recording."""

    def __init__(self, cash=1000.0, fee=0.0):
        self.cash = cash
        self.fee = fee
        self.position = 0.0
        self.trades = []

    def _buy(self, px, shares):
        cost = shares * px * (1 + self.fee)
        if cost > self.cash:
            return False
        self.cash -= cost
        self.position += shares
        self.trades.append(("BUY", px, shares))
        return True

    def _sell(self, px, shares):
        if shares > self.position:
            return False
        self.cash += shares * px * (1 - self.fee)
        self.position -= shares
        self.trades.append(("SELL", px, shares))
        return True

    def run(self, rows, strategy):
        for r in rows:
            sig = strategy(r)
            if sig == "BUY":
                self._buy(r["ask"], 10.0)
            elif sig == "SELL":
                self._sell(r["bid"], min(10.0, self.position))
        # mark to last mid
        last = rows[-1] if rows else None
        mid = (last["bid"] + last["ask"]) / 2 if last else 0.0
        return {
            "final_equity": round(self.cash + self.position * mid, 2),
            "trades": len(self.trades),
        }


def sma_strategy(fast=3, slow=8):
    """Toy mean-reversion-ish strategy over rolling mids."""
    hist = []

    def strat(row):
        mid = (row["bid"] + row["ask"]) / 2
        hist.append(mid)
        if len(hist) < slow:
            return None
        fast_avg = sum(hist[-fast:]) / fast
        slow_avg = sum(hist[-slow:]) / slow
        if fast_avg < slow_avg * 0.995:
            return "BUY"
        if fast_avg > slow_avg * 1.005:
            return "SELL"
        return None
    return strat
