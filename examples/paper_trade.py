"""Paper-trade a simple strategy against live book prices. No keys needed."""
from pmkit.clob import best_bid, best_ask
from pmkit.paper import PaperLedger

if __name__ == "__main__":
    ledger = PaperLedger(starting_cash=1000.0)
    # example token id (a live market); replace with any clobTokenId
    token = "21742633143463906290569050155826241533067279536803137953470645380173117809916"
    bb = best_bid(token)
    ba = best_ask(token)
    print(f"best bid: {bb}  best ask: {ba}")
    if ledger.buy(token, 10.0, ba[0] if ba[0] < 1 else 0.5):
        print("paper buy filled at ask")
    print(f"equity: {ledger.equity():.2f}")
