import unittest
from unittest.mock import MagicMock
from modules.execution.order_manager import OrderManager
from modules.data.mt5_loader import MT5
from config.config import Config

class TestOrderManager(unittest.TestCase):
    def setUp(self):
        MT5.reset_mock()
        self.om = OrderManager()
        # Ensure we have a valid magic number in mock
        Config.MAGIC_NUMBER = 123456

    def test_count_open_trades(self):
        # Mock positions_get to return 2 positions with our magic
        p1 = MagicMock(magic=123456)
        p2 = MagicMock(magic=123456)
        p3 = MagicMock(magic=999999) # Different magic
        
        MT5.positions_get.return_value = [p1, p2, p3]
        
        count = self.om.count_open_trades("EURUSD") # Symbol filter done inside? 
        # Our implementation: get_open_positions(symbol) -> MT5.positions_get(symbol=symbol)
        # So we should verify call args too
        
        # Test 1: Symbol passed to MT5
        self.om.count_open_trades("EURUSD") 
        MT5.positions_get.assert_called_with(symbol="EURUSD")
        
        # Test 2: Filtering logic (if no symbol passed / general)
        # Re-mock logic if necessary or just trust the mock return is parsed
        self.assertEqual(len(self.om.get_open_positions("EURUSD")), 2)

    def test_execute_trade_success(self):
        # 1. No existing trades
        MT5.positions_get.return_value = []
        
        # 2. Mock Tick
        mock_tick = MagicMock()
        mock_tick.ask = 1.1005
        mock_tick.bid = 1.1000
        MT5.symbol_info_tick.return_value = mock_tick
        
        # 3. Mock Order Result
        mock_result = MagicMock()
        mock_result.retcode = 10009 # Done
        mock_result.order = 777
        MT5.order_send.return_value = mock_result
        
        success = self.om.execute_trade("EURUSD", "BUY", 0.1, 1.0900, 1.1100)
        
        self.assertTrue(success)
        MT5.order_send.assert_called_once()
        args = MT5.order_send.call_args[0][0]
        self.assertEqual(args['action'], MT5.TRADE_ACTION_DEAL)
        self.assertEqual(args['type'], MT5.ORDER_TYPE_BUY)
        self.assertEqual(args['price'], 1.1005) # Ask

    def test_execute_trade_duplicate_prevention(self):
        # Mock existing trade
        p1 = MagicMock(magic=123456)
        MT5.positions_get.return_value = [p1]
        
        success = self.om.execute_trade("EURUSD", "BUY", 0.1, 1.0, 1.2)
        
        self.assertFalse(success)
        # Ensure we didn't send an order
        MT5.order_send.assert_not_called()

    def test_execute_trade_failure_response(self):
        MT5.positions_get.return_value = []
        MT5.symbol_info_tick.return_value = MagicMock(ask=1.0)
        
        # Mock failure (e.g. invalid volume -> 10014)
        mock_result = MagicMock()
        mock_result.retcode = 10014
        MT5.order_send.return_value = mock_result
        
        success = self.om.execute_trade("EURUSD", "BUY", 0.1, 0.9, 1.1)
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()
