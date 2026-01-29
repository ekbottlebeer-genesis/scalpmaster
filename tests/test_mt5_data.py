import unittest
import pandas as pd
from unittest.mock import MagicMock
from modules.data.connection_manager import ConnectionManager
from modules.data.market_data import MarketData
from modules.data.mt5_loader import MT5
from config.config import Config

class TestMT5Data(unittest.TestCase):
    def setUp(self):
        # Reset Mock state
        MT5.reset_mock()
        
        # Setup Config mocks
        Config.MT5_LOGIN = 123456
        Config.MT5_PASSWORD = "test_pass"
        Config.MT5_SERVER = "test_server"
        Config.MT5_PATH = "/path/to/terminal"

    def test_connection_initialize_success(self):
        """Test that initialize calls MT5.initialize and login."""
        MT5.initialize.return_value = True
        MT5.login.return_value = True
        
        result = ConnectionManager.initialize()
        
        self.assertTrue(result)
        MT5.initialize.assert_called_with(path=Config.MT5_PATH)
        MT5.login.assert_called_with(
            login=Config.MT5_LOGIN, 
            password=Config.MT5_PASSWORD, 
            server=Config.MT5_SERVER
        )

    def test_connection_initialize_fail(self):
        """Test failure when MT5.initialize fails."""
        MT5.initialize.return_value = False
        result = ConnectionManager.initialize()
        self.assertFalse(result)

    def test_get_candles_df_success(self):
        """Test that get_candles_df returns a valid DataFrame."""
        # Mock successful connection
        MT5.terminal_info.return_value.connected = True
        
        # Mock rates data (numpy record array style, but list of tuples/dicts works for pd.DataFrame)
        mock_rates = [
            {'time': 1600000000, 'open': 1.0, 'high': 1.2, 'low': 0.9, 'close': 1.1, 'tick_volume': 100},
            {'time': 1600000060, 'open': 1.1, 'high': 1.3, 'low': 1.0, 'close': 1.2, 'tick_volume': 200},
        ]
        
        MT5.copy_rates_from_pos.return_value = mock_rates
        
        df = MarketData.get_candles_df("EURUSD", MT5.TIMEFRAME_M1, 100)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertListEqual(list(df.columns), ['time', 'open', 'high', 'low', 'close', 'tick_volume'])
        self.assertEqual(df.iloc[0]['close'], 1.1)

    def test_get_candles_df_failure(self):
        """Test that get_candles_df returns empty DataFrame on failure."""
        # Mock return None or empty
        MT5.copy_rates_from_pos.return_value = None
        
        df = MarketData.get_candles_df("EURUSD", MT5.TIMEFRAME_M1, 100)
        
        self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(df.empty)

if __name__ == '__main__':
    unittest.main()
