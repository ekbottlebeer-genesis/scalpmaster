import unittest
import pandas as pd
import numpy as np
from modules.indicators.indicators import Indicators

class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Create sample OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=300, freq='1min')
        self.df = pd.DataFrame({
            'time': dates,
            'open': np.random.uniform(1.1000, 1.2000, 300),
            'high': np.random.uniform(1.2000, 1.3000, 300),
            'low': np.random.uniform(1.0000, 1.1000, 300),
            'close': np.random.uniform(1.1000, 1.2000, 300),
            'tick_volume': np.random.randint(10, 1000, 300)
        })
        # Set datetime index for Pandas TA if needed, but our wrapper handles column access
        # pandas_ta usually infers, but explicit index is safer. 
        # However, our Indicators class passes Series explicitly so index type matters less 
        # unless indicator relies on time.
        self.df.set_index('time', inplace=True)

    def test_add_emas(self):
        df = Indicators.add_emas(self.df)
        self.assertIn('EMA_20', df.columns)
        self.assertIn('EMA_50', df.columns)
        self.assertIn('EMA_200', df.columns)
        # Check values are calculated (last row shouldn't be NaN for 300 pts)
        self.assertFalse(pd.isna(df['EMA_20'].iloc[-1]))

    def test_add_rsi(self):
        df = Indicators.add_rsi(self.df)
        self.assertIn('RSI_14', df.columns)
        self.assertFalse(pd.isna(df['RSI_14'].iloc[-1]))

    def test_add_atr(self):
        df = Indicators.add_atr(self.df)
        self.assertIn('ATR_14', df.columns)
        self.assertFalse(pd.isna(df['ATR_14'].iloc[-1]))

    def test_add_adx(self):
        df = Indicators.add_adx(self.df)
        # pandas_ta ADX output columns might vary by version, usually ADX_14, DMP_14, DMN_14
        cols = [c for c in df.columns if 'ADX' in c]
        self.assertTrue(len(cols) > 0)

    def test_add_vwap(self):
        df = Indicators.add_vwap(self.df)
        self.assertIn('VWAP', df.columns)
        self.assertFalse(pd.isna(df['VWAP'].iloc[-1]))

    def test_add_candle_metrics(self):
        df = Indicators.add_candle_metrics(self.df)
        self.assertIn('range', df.columns)
        self.assertIn('body', df.columns)
        self.assertIn('compression', df.columns)
        
    def test_add_all(self):
        df = Indicators.add_all(self.df)
        self.assertIn('EMA_20', df.columns)
        self.assertIn('RSI_14', df.columns)
        self.assertIn('compression', df.columns)

    def test_empty_df(self):
        empty_df = pd.DataFrame()
        res = Indicators.add_all(empty_df)
        self.assertTrue(res.empty)

if __name__ == '__main__':
    unittest.main()
