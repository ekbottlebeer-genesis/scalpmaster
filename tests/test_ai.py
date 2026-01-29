import unittest
import pandas as pd
from modules.ai.regime_filter import RegimeFilter
from modules.ai.post_trade_adaptor import PostTradeAdaptor

class TestAI(unittest.TestCase):
    def setUp(self):
        self.regime = RegimeFilter()
        self.adaptor = PostTradeAdaptor()

    def test_regime_dates_heuristic(self):
        # Create a DF that looks like an UPTREND
        # Needs 14+ rows. We'll make 15.
        data = [{'ADX_14': 20, 'compression': 0.5, 'EMA_20': 1.0, 'EMA_50': 1.0, 'close': 1.0}] * 14
        data.append({
            'ADX_14': 30, 'compression': 0.8,
            'EMA_20': 1.1020, 'EMA_50': 1.1000, 'close': 1.1030
        })
        df_trend = pd.DataFrame(data)
        
        regime = self.regime.detect_regime(df_trend)
        self.assertEqual(regime, "TREND_UP")

    def test_regime_chop(self):
        # Low ADX, Low Compression
        data = [{'ADX_14': 25, 'compression': 0.5, 'EMA_20': 1.0, 'EMA_50': 1.0, 'close': 1.0}] * 14
        data.append({
            'ADX_14': 15, 'compression': 0.2,
            'EMA_20': 1.1, 'EMA_50': 1.1, 'close': 1.1
        })
        df_chop = pd.DataFrame(data)
        regime = self.regime.detect_regime(df_chop)
        self.assertEqual(regime, "CHOP")

    def test_adaptor_tightening(self):
        # Initial state
        initial_adx = self.adaptor.min_adx
        
        # Simulate Loss
        self.adaptor.update_thresholds(-50.0)
        
        # Expect ADX requirement to increase
        self.assertGreater(self.adaptor.min_adx, initial_adx)

    def test_adaptor_relaxing(self):
        # Setup high threshold
        self.adaptor.min_adx = 30.0
        
        # Simulate Win
        self.adaptor.update_thresholds(100.0)
        
        # Expect ADX requirement to decrease
        self.assertLess(self.adaptor.min_adx, 30.0)

if __name__ == '__main__':
    unittest.main()
