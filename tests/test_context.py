import unittest
from datetime import datetime
from dataclasses import FrozenInstanceError
from core.context import TradeContext

class TestTradeContext(unittest.TestCase):
    def setUp(self):
        self.ctx = TradeContext(
            symbol="EURUSD",
            timestamp=datetime.now(),
            current_price=1.1234,
            spread=10,
            session_name="USA_OPEN",
            is_news_event=False,
            indicators={"RSI_14": 55.0},
            market_regime="TREND_UP",
            trend_bias="LONG",
            cooldown_remaining=0,
            pullback_candles=3,
            risk_status={"can_trade": True}
        )

    def test_immutability(self):
        """Test that modifying fields raises an error."""
        with self.assertRaises(FrozenInstanceError):
            self.ctx.symbol = "GBPUSD"
            
        with self.assertRaises(FrozenInstanceError):
            self.ctx.trend_bias = "SHORT"

    def test_access(self):
        """Test that fields are accessible."""
        self.assertEqual(self.ctx.symbol, "EURUSD")
        self.assertEqual(self.ctx.indicators["RSI_14"], 55.0)

if __name__ == '__main__':
    unittest.main()
