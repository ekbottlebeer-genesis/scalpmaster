import sys
import platform
import logging
from unittest.mock import MagicMock

logger = logging.getLogger(__name__)

# Check OS
IS_WINDOWS = platform.system() == 'Windows'

try:
    if IS_WINDOWS:
        import MetaTrader5 as mt5
    else:
        raise ImportError("Not on Windows")
except ImportError:
    logger.warning("MetaTrader5 package not found or not on Windows. Using MOCK object.")
    
    # Create a comprehensive Mock object
    mt5 = MagicMock()
    
    # Mock constants
    mt5.TIMEFRAME_M1 = 1
    mt5.TIMEFRAME_M5 = 5
    mt5.TIMEFRAME_H1 = 16385
    mt5.COPY_TICKS_ALL = -1
    mt5.ORDER_TYPE_BUY = 0
    mt5.ORDER_TYPE_SELL = 1
    mt5.TRADE_ACTION_DEAL = 1
    
    # Mock return values for success checks
    mt5.initialize.return_value = True
    mt5.login.return_value = True
    
    # Mock terminal info
    mock_terminal_info = MagicMock()
    mock_terminal_info.connected = True
    mt5.terminal_info.return_value = mock_terminal_info

    # Mock symbol info
    mock_symbol_info = MagicMock()
    mock_symbol_info.spread = 10
    mock_symbol_info.visible = True
    mt5.symbol_info.return_value = mock_symbol_info

# Expose the mt5 object (either real or mock)
MT5 = mt5
