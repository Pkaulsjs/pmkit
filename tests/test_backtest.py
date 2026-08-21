import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pmkit.backtest import Backtest, sma_strategy, load_recording


class TestBacktest(unittest.TestCase):
    def test_roundtrip_with_spread(self):
        rows = [
            {"ts": 1.0, "bid": 0.49, "ask": 0.51},
            {"ts": 2.0, "bid": 0.55, "ask": 0.57},
        ]
        bt = Backtest(cash=1000.0)
        res = bt.run(rows, lambda r: "BUY" if r["ts"] == 1.0 else "SELL")
        # buy 10 @0.51=5.10, sell 10 @0.55=5.50 -> +0.40
        self.assertAlmostEqual(res["final_equity"], 1000.40, places=2)
        self.assertEqual(res["trades"], 2)

    def test_no_churning_without_signal(self):
        rows = [{"ts": float(i), "bid": 0.50, "ask": 0.501} for i in range(20)]
        bt = Backtest(cash=1000.0)
        res = bt.run(rows, lambda r: None)
        self.assertEqual(res["trades"], 0)
        self.assertAlmostEqual(res["final_equity"], 1000.0, places=2)


if __name__ == "__main__":
    unittest.main()
