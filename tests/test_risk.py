import unittest
from core.risk import RiskManager
from config.config import Config

class TestRiskManager(unittest.TestCase):
    def setUp(self):
        # Reset Config defaults for testing
        Config.RISK_PER_TRADE_PERCENT = 0.5
        Config.MAX_DAILY_LOSS_PERCENT = 4.0
        
        self.rm = RiskManager()
        # Init with 100k balance
        self.rm.snapshot_account(100000.0)

    def test_can_trade_success(self):
        # Current equity same as start
        can_trade, reason = self.rm.can_trade(100000.0, 1000)
        self.assertTrue(can_trade)
        self.assertEqual(reason, "OK")

    def test_daily_loss_limit(self):
        # Max loss is 4% of 100k = 4000.
        # If equity drops to 96000, we should stop.
        
        # Case 1: Just above limit (Loss 3999) -> OK
        can_trade, _ = self.rm.can_trade(96001.0, 1000)
        self.assertTrue(can_trade)

        # Case 2: At/Below limit (Loss 4000) -> FAIL
        can_trade, reason = self.rm.can_trade(96000.0, 1000)
        self.assertFalse(can_trade)
        self.assertIn("DAILY_LOSS_LIMIT", reason)
        self.assertTrue(self.rm.is_hard_stopped)

    def test_adaptive_risk_streaks(self):
        # Base risk 0.5%
        # 0 losses
        self.assertEqual(self.rm.get_adaptive_risk(100000), 0.5)
        
        # 1 loss
        self.rm.update_metrics(-100)
        self.assertEqual(self.rm.loss_streak, 1)
        self.assertEqual(self.rm.get_adaptive_risk(100000), 0.5) # Still base (wait for 2)

        # 2 losses -> Halve
        self.rm.update_metrics(-100)
        self.assertEqual(self.rm.loss_streak, 2)
        self.assertEqual(self.rm.get_adaptive_risk(100000), 0.25)
        
        # Win resets
        self.rm.update_metrics(200)
        self.assertEqual(self.rm.loss_streak, 0)
        self.assertEqual(self.rm.get_adaptive_risk(100000), 0.5)

    def test_adaptive_risk_drawdown(self):
        # Max loss 4000. Half limit is 2000.
        # If drawdown > 2000, risk halves.
        
        # Drawdown 2100 (Equity 97900)
        risk = self.rm.get_adaptive_risk(97900.0)
        self.assertEqual(risk, 0.25) # 0.5 / 2

    def test_lot_size(self):
        # 100k balance, 0.5% risk = $500 risk amount
        # Entry 1.1000, SL 1.0990 (10 pips = 0.0010 dist)
        # Lots = 500 / (100000 * 0.0010) = 500 / 100 = 5.0 lots
        
        lots = self.rm.calculate_lot_size(100000.0, 1.1000, 1.0990, 0.5)
        self.assertAlmostEqual(lots, 5.0)

if __name__ == '__main__':
    unittest.main()
