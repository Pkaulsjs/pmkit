import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from pmkit.paper import PaperLedger


class TestPaperLedger(unittest.TestCase):
    def test_buy_sell_roundtrip(self):
        led = PaperLedger(starting_cash=100.0)
        self.assertTrue(led.buy("T1", 10, 0.5))
        self.assertEqual(led.cash, 95.0)
        self.assertTrue(led.sell("T1", 10, 0.6))
        self.assertAlmostEqual(led.cash, 101.0)
        self.assertEqual(led.equity(), led.cash)

    def test_insufficient_cash_rejected(self):
        led = PaperLedger(starting_cash=1.0)
        self.assertFalse(led.buy("T1", 100, 0.5))

    def test_oversell_rejected(self):
        led = PaperLedger(starting_cash=100.0)
        self.assertTrue(led.buy("T1", 10, 0.5))
        self.assertFalse(led.sell("T1", 20, 0.6))


if __name__ == "__main__":
    unittest.main()
