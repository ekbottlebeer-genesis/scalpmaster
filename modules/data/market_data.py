import pandas as pd
import logging
from datetime import datetime
from modules.data.mt5_loader import MT5
from modules.data.connection_manager import ConnectionManager
from modules.data.connection_manager import ConnectionManager
from config.config import Config

# Mapping for string -> MT5 constant
TIMEFRAME_MAP = {
    "M1": MT5.TIMEFRAME_M1,
    "M5": MT5.TIMEFRAME_M5,
    "M15": MT5.TIMEFRAME_M15,
    "M30": MT5.TIMEFRAME_M30,
    "H1": MT5.TIMEFRAME_H1,
    "H4": MT5.TIMEFRAME_H4,
    "D1": MT5.TIMEFRAME_D1,
}

logger = logging.getLogger(__name__)

class MarketData:
    @staticmethod
    def check_symbol_availability(symbol):
        """
        Checks if a symbol is available and visible in Market Watch.
        Attempts to add it if not visible.
        """
        """
        # Resolve broker-specific symbol (e.g. "EURUSD" -> "EURUSD.a")
        mt_symbol = Config.get_mt5_symbol(symbol)
        
        if not MT5.symbol_select(mt_symbol, True):
            logger.error(f"Failed to select symbol {mt_symbol}")
            return False
            
        info = MT5.symbol_info(mt_symbol)
        if info is None:
            logger.error(f"Symbol {mt_symbol} not found")
            return False
            
        logger.info(f"Symbol {mt_symbol} available. Spread: {info.spread}")
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

        # Resolve broker specific symbol
        mt_symbol = Config.get_mt5_symbol(symbol)
        
        # Resolve Timeframe (String -> Int)
        mt_tf = TIMEFRAME_MAP.get(timeframe, MT5.TIMEFRAME_M1)
        if timeframe not in TIMEFRAME_MAP and isinstance(timeframe, str):
            logger.warning(f"Unknown timeframe string '{timeframe}', defaulting to M1")
        elif isinstance(timeframe, int):
            mt_tf = timeframe

        # Copy rates
        try:
            rates = MT5.copy_rates_from_pos(mt_symbol, mt_tf, 0, limit)
        except Exception as e:
            logger.error(f"Critical MT5 Error for {mt_symbol}: {e}")
            return pd.DataFrame()
        
        if rates is None or len(rates) == 0:
            logger.warning(f"No data received for {mt_symbol}")
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
        """
        mt_symbol = Config.get_mt5_symbol(symbol)
        tick = MT5.symbol_info_tick(mt_symbol)
        if tick is None:
            return None
        return tick
