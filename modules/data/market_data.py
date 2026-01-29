import pandas as pd
import logging
from datetime import datetime
from modules.data.mt5_loader import MT5
from modules.data.connection_manager import ConnectionManager
from config.config import Config

logger = logging.getLogger(__name__)

class MarketData:
    @staticmethod
    def check_symbol_availability(symbol):
        """
        Checks if a symbol is available and visible in Market Watch.
        Attempts to add it if not visible.
        """
        if not MT5.symbol_select(symbol, True):
            logger.error(f"Failed to select symbol {symbol}")
            return False
            
        info = MT5.symbol_info(symbol)
        if info is None:
            logger.error(f"Symbol {symbol} not found")
            return False
            
        logger.info(f"Symbol {symbol} available. Spread: {info.spread}")
        return True

    @staticmethod
    def get_candles_df(symbol, timeframe, limit=500):
        """
        Fetches OHLCV data for a symbol.
        
        Args:
            symbol (str): Trading pair (e.g. "EURUSD")
            timeframe (int): MT5 timeframe constant (e.g. MT5.TIMEFRAME_M1)
            limit (int): Number of candles to fetch
            
        Returns:
            pd.DataFrame: Columns ['time', 'open', 'high', 'low', 'close', 'tick_volume']
                          Returns empty DataFrame on failure.
        """
        # Ensure connection is alive
        if not ConnectionManager.ensure_connected():
            return pd.DataFrame()

        # Copy rates
        rates = MT5.copy_rates_from_pos(symbol, timeframe, 0, limit)
        
        if rates is None or len(rates) == 0:
            logger.warning(f"No data received for {symbol}")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(rates)
        
        # Keep only relevant columns if available
        # MT5 returns structured array with: time, open, high, low, close, tick_volume, spread, real_volume
        # We enforce a standard schema
        
        if 'time' in df.columns:
            df['time'] = pd.to_datetime(df['time'], unit='s')
        
        required_cols = ['time', 'open', 'high', 'low', 'close', 'tick_volume']
        # Filter columns that exist
        available_cols = [c for c in required_cols if c in df.columns]
        
        return df[available_cols]

    @staticmethod
    def get_tick_info(symbol):
        """
        Returns the latest tick info (bid, ask) for a symbol.
        """
        tick = MT5.symbol_info_tick(symbol)
        if tick is None:
            return None
        return tick
