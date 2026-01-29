import unittest
from config.config import Config

class TestConfigValidation(unittest.TestCase):
    def setUp(self):
        # Save original state
        self.original_login = Config.MT5_LOGIN
        self.original_password = Config.MT5_PASSWORD
        self.original_server = Config.MT5_SERVER
        self.original_path = Config.MT5_PATH
        self.original_token = Config.TELEGRAM_TOKEN
        self.original_pairs = Config.TRADING_PAIRS

    def tearDown(self):
        # Restore original state
        Config.MT5_LOGIN = self.original_login
        Config.MT5_PASSWORD = self.original_password
        Config.MT5_SERVER = self.original_server
        Config.MT5_PATH = self.original_path
        Config.TELEGRAM_TOKEN = self.original_token
        Config.TRADING_PAIRS = self.original_pairs

    def test_validate_success(self):
        """Test that validation passes with mock valid data."""
        # Mock valid data
        Config.MT5_LOGIN = 123456
        Config.MT5_PASSWORD = "pass"
        Config.MT5_SERVER = "server"
        Config.MT5_PATH = "C:\\path"
        Config.TELEGRAM_TOKEN = "token"
        Config.TRADING_PAIRS = ["EURUSD"]
        
        try:
            Config.validate()
        except ValueError:
            self.fail("Config.validate raised ValueError unexpectedly!")

    def test_missing_mt5_login(self):
        """Test that missing MT5_LOGIN raises ValueError."""
        Config.MT5_LOGIN = 0
        with self.assertRaises(ValueError) as cm:
            Config.validate()
        self.assertIn("MT5_LOGIN", str(cm.exception))

    def test_missing_telegram_token(self):
        """Test that missing TELEGRAM_TOKEN raises ValueError."""
        # Ensure other fields are valid first
        Config.MT5_LOGIN = 123456
        Config.MT5_PASSWORD = "pass"
        Config.MT5_SERVER = "server"
        Config.MT5_PATH = "C:\\path"
        
        Config.TELEGRAM_TOKEN = ""
        with self.assertRaises(ValueError) as cm:
            Config.validate()
        self.assertIn("TELEGRAM_TOKEN", str(cm.exception))

    def test_missing_trading_pairs(self):
        """Test that missing trading pairs in settings raises ValueError."""
        # Ensure secrets are valid
        Config.MT5_LOGIN = 123456
        Config.MT5_PASSWORD = "pass"
        Config.MT5_SERVER = "server"
        Config.MT5_PATH = "C:\\path"
        Config.TELEGRAM_TOKEN = "token"

        Config.TRADING_PAIRS = []
        with self.assertRaises(ValueError) as cm:
            Config.validate()
        self.assertIn("trading.pairs", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
