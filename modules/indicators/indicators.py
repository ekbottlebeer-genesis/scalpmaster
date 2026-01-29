import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def _validate_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validates input DataFrame and returns a copy to ensure purity.
        """
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Ensure sufficient data for calculation
        if len(df) < 2:
            return df.copy()
            
        return df.copy()

    @staticmethod
    def add_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies ALL standard indicators to the DataFrame.
        """
        df = Indicators._validate_df(df)
        if df.empty:
            return df
            
        df = Indicators.add_emas(df)
        df = Indicators.add_rsi(df)
        df = Indicators.add_atr(df)
        df = Indicators.add_adx(df)
        df = Indicators.add_vwap(df)
        df = Indicators.add_candle_metrics(df)
        return df

    @staticmethod
    def add_emas(df: pd.DataFrame) -> pd.DataFrame:
        """Adds EMA 20, 50, 200."""
        df = df.copy()
        if 'close' not in df.columns:
            return df

        try:
            df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
            df['EMA_200'] = df['close'].ewm(span=200, adjust=False).mean()
        except Exception:
            pass
        return df

    @staticmethod
    def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Adds RSI 14."""
        df = df.copy()
        if 'close' not in df.columns:
            return df
            
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).fillna(0)
            loss = (-delta.where(delta < 0, 0)).fillna(0)

            avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

            rs = avg_gain / avg_loss
            df[f'RSI_{period}'] = 100 - (100 / (1 + rs))
            
            # fill initial NaNs with 50 or 0? better leave NaN.
        except Exception:
            pass
        return df

    @staticmethod
    def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Adds ATR 14."""
        df = df.copy()
        cols = ['high', 'low', 'close']
        if not all(col in df.columns for col in cols):
            return df

        try:
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            
            # Initialize with SMA, then use Wilder's Smoothing? 
            # Standard EWM with alpha=1/period is Wilder's smoothing approximation
            df[f'ATR_{period}'] = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        except Exception:
            pass
        return df

    @staticmethod
    def add_adx(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Adds ADX 14."""
        df = df.copy()
        cols = ['high', 'low', 'close']
        if not all(col in df.columns for col in cols):
            return df
            
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            
            # TR Calculation
            prev_close = close.shift(1)
            tr1 = high - low
            tr2 = (high - prev_close).abs()
            tr3 = (low - prev_close).abs()
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Directional Movement
            up_move = high.diff()
            down_move = -low.diff()

            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
            
            plus_dm = pd.Series(plus_dm, index=df.index)
            minus_dm = pd.Series(minus_dm, index=df.index)

            # Smoothed TR and DM (Wilder's)
            atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            plus_di = 100 * (plus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr)
            minus_di = 100 * (minus_dm.ewm(alpha=1/period, min_periods=period, adjust=False).mean() / atr)

            # DX
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            
            # ADX
            df[f'ADX_{period}'] = dx.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            # Optional: Return DI+ DI-
            # df['DMP_14'] = plus_di
            # df['DMN_14'] = minus_di
            
        except Exception:
            pass
        return df

    @staticmethod
    def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
        """Adds VWAP (Cumulative). index-based."""
        df = df.copy()
        cols = ['high', 'low', 'close', 'tick_volume']
        if not all(col in df.columns for col in cols):
            return df
            
        try:
            v = df['tick_volume']
            tp = (df['high'] + df['low'] + df['close']) / 3
            df['VWAP'] = (tp * v).cumsum() / v.cumsum()
        except Exception:
            pass
        return df

    @staticmethod
    def add_candle_metrics(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates:
        - range: High - Low
        - body: abs(Close - Open)
        - compression: Body / Range
        """
        df = df.copy()
        cols = ['open', 'high', 'low', 'close']
        if not all(col in df.columns for col in cols):
            return df
            
        try:
            df['range'] = df['high'] - df['low']
            df['body'] = (df['close'] - df['open']).abs()

            # Handle division by zero safely
            # Replace 0 range with NaN or handle
            df['compression'] = np.where(df['range'] > 0, df['body'] / df['range'], 1.0)
        except Exception:
            pass
        return df
