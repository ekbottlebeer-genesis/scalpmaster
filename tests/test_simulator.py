import unittest
from unittest.mock import MagicMock
from modules.execution.simulator import SimulatedExecution
from modules.data.mt5_loader import MT5

class TestSimulator(unittest.TestCase):
    def setUp(self):
        MT5.reset_mock()
        self.sim = SimulatedExecution()

    def test_execute_trade(self):
        # Mock MT5 tick for price fetching
        mock_tick = MagicMock()
        mock_tick.ask = 1.1000
        mock_tick.bid = 1.0990
        MT5.symbol_info_tick.return_value = mock_tick

        success = self.sim.execute_trade("EURUSD", "BUY", 0.1, 1.0900, 1.1100)
        self.assertTrue(success)
        
        positions = self.sim.get_open_positions("EURUSD")
        self.assertEqual(len(positions), 1)
        self.assertEqual(positions[0].symbol, "EURUSD")
        self.assertEqual(positions[0].volume, 0.1)

    def test_duplicate_prevention(self):
        # Mock tick
        MT5.symbol_info_tick.return_value = MagicMock(ask=1.0)
        
        # Open first trade
        self.sim.execute_trade("EURUSD", "BUY", 0.1, 1.0, 1.2)
        
        # Try second trade
        success = self.sim.execute_trade("EURUSD", "SELL", 0.1, 1.0, 0.8)
        self.assertFalse(success)
        self.assertEqual(len(self.sim.get_open_positions("EURUSD")), 1)

    def test_close_trade(self):
        MT5.symbol_info_tick.return_value = MagicMock(ask=1.0)
        self.sim.execute_trade("EURUSD", "BUY", 0.1, 1.0, 1.2)
        
        positions = self.sim.get_open_positions("EURUSD")
        ticket = positions[0].ticket
        
        success = self.sim.close_trade(ticket, "EURUSD")
        self.assertTrue(success)
        self.assertEqual(len(self.sim.get_open_positions("EURUSD")), 0)

if __name__ == '__main__':
    unittest.main()
