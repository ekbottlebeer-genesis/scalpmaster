import unittest
from datetime import datetime
from core.context import TradeContext
from strategies.checklist import StrategyChecklist

class TestStrategyChecklist(unittest.TestCase):
    def setUp(self):
        # Create a "Perfect" context that should pass all checks
        self.valid_ctx = TradeContext(
            symbol="EURUSD",
            timestamp=datetime.now(),
            current_price=1.1000,
            spread=10,  # Valid (<20)
            session_name="LONDON",
            is_news_event=False,
            indicators={"RSI_14": 50.0, "ATR_14": 0.0010},
            market_regime="TREND_UP",
            trend_bias="LONG",
            cooldown_remaining=0,
            pullback_candles=3,
            risk_status={"can_trade": True}
        )
        self.checklist = StrategyChecklist()

    def test_pass_all_checks(self):
        decision = self.checklist.run(self.valid_ctx)
        self.assertTrue(decision.can_trade)
        self.assertEqual(decision.reasons, ["ALL CHECKS PASSED"])

    def test_fail_spread(self):
        # Create context with high spread - requires using object params that are frozen
        # But Since dataclass is frozen, we must instantiate new one.
        # Python 3.10+ supports replace() if created, but we'll just new it.
        ctx = TradeContext(
            symbol="EURUSD", timestamp=datetime.now(), current_price=1.1, spread=21, # > 20
            session_name="L", is_news_event=False, indicators={}, market_regime="T",
            trend_bias="L", cooldown_remaining=0, pullback_candles=0, risk_status={"can_trade":True}
        )
        decision = self.checklist.run(ctx)
        self.assertFalse(decision.can_trade)
        self.assertIn("SPREAD_TOO_HIGH", decision.reasons[0])

    def test_fail_risk(self):
        ctx = TradeContext(
            symbol="EURUSD", timestamp=datetime.now(), current_price=1.1, spread=10,
            session_name="L", is_news_event=False, indicators={}, market_regime="T",
            trend_bias="L", cooldown_remaining=0, pullback_candles=0, risk_status={"can_trade":False}
        )
        decision = self.checklist.run(ctx)
        self.assertFalse(decision.can_trade)
        self.assertIn("RISK_LIMIT_HIT", decision.reasons[0])

    def test_fail_regime(self):
        ctx = TradeContext(
            symbol="EURUSD", timestamp=datetime.now(), current_price=1.1, spread=10,
            session_name="L", is_news_event=False, indicators={"RSI_14": 50, "ATR_14": 0.001},
            market_regime="CHOP", # Fail
            trend_bias="LONG", cooldown_remaining=0, pullback_candles=0, risk_status={"can_trade":True}
        )
        decision = self.checklist.run(ctx)
        self.assertFalse(decision.can_trade)
        self.assertIn("BAD_REGIME", decision.reasons[0])

    def test_fail_news(self):
        ctx = TradeContext(
            symbol="EURUSD", timestamp=datetime.now(), current_price=1.1, spread=10,
            session_name="L", is_news_event=True, # Fail
            indicators={"RSI_14": 50, "ATR_14": 0.001}, market_regime="TREND_UP",
            trend_bias="LONG", cooldown_remaining=0, pullback_candles=0, risk_status={"can_trade":True}
        )
        decision = self.checklist.run(ctx)
        self.assertFalse(decision.can_trade)
        self.assertIn("NEWS_EVENT_ACTIVE", decision.reasons[0])

if __name__ == '__main__':
    unittest.main()
