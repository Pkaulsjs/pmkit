"""Paper-trading ledger engine. No keys, no funds, pure simulation."""
import time


class PaperLedger:
    """Simulated fills at stated prices; tracks positions and cash."""

    def __init__(self, starting_cash=1000.0):
        self.cash = float(starting_cash)
        self.positions = {}
        self.fills = []

    def buy(self, token_id, shares, price):
        cost = shares * price
        if cost > self.cash:
            return False
        self.cash -= cost
        pos = self.positions.get(token_id, {"shares": 0.0, "cost": 0.0})
        pos["shares"] += shares
        pos["cost"] += cost
        self.positions[token_id] = pos
        self.fills.append({"ts": time.time(), "side": "BUY", "token": str(token_id)[:12],
                           "shares": shares, "price": price})
        return True

    def sell(self, token_id, shares, price):
        pos = self.positions.get(token_id)
        if not pos or pos["shares"] < shares:
            return False
        proceeds = shares * price
        self.cash += proceeds
        pos["shares"] -= shares
        self.fills.append({"ts": time.time(), "side": "SELL", "token": str(token_id)[:12],
                           "shares": shares, "price": price})
        return True

    def equity(self, mark_prices=None):
        mark_prices = mark_prices or {}
        total = self.cash
        for tid, pos in self.positions.items():
            px = mark_prices.get(tid)
            if px is None:
                px = pos["cost"] / pos["shares"] if pos["shares"] else 0
            total += pos["shares"] * px
        return total
