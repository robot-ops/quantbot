import pandas as pd
import numpy as np
from loguru import logger

class TechnicalIndicators:
    """Provides technical analysis indicator calculations on Pandas DataFrames."""

    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
        """Calculates the Exponential Moving Average (EMA) for a given column.

        Args:
            df (pd.DataFrame): The input DataFrame containing market data.
            period (int): The period length for the EMA calculation.
            column (str): The column name to apply calculation on. Defaults to 'close'.

        Returns:
            pd.Series: A Pandas Series representing the calculated EMA.
        """
        if len(df) < period:
            logger.warning(f"DataFrame size ({len(df)}) is smaller than period ({period}). Returning NaN series.")
            return pd.Series([np.nan] * len(df), index=df.index)
        return df[column].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
        """Calculates the Relative Strength Index (RSI) for a given column.

        Args:
            df (pd.DataFrame): The input DataFrame containing market data.
            period (int): The period length for the RSI calculation. Defaults to 14.
            column (str): The column name to apply calculation on. Defaults to 'close'.

        Returns:
            pd.Series: A Pandas Series representing the calculated RSI.
        """
        if len(df) <= period:
            return pd.Series([50.0] * len(df), index=df.index)
            
        delta = df[column].diff()
        gain = (delta.where(delta > 0, 0)).fillna(0)
        loss = (-delta.where(delta < 0, 0)).fillna(0)

        avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculates the Average True Range (ATR).

        Args:
            df (pd.DataFrame): OHLCV DataFrame. Must have open, high, low, close.
            period (int): The period length for ATR calculation. Defaults to 14.

        Returns:
            pd.Series: A Pandas Series representing the ATR.
        """
        if len(df) <= period:
            return pd.Series([0.0] * len(df), index=df.index)
            
        high_low = df["high"] - df["low"]
        high_close_prev = (df["high"] - df["close"].shift(1)).abs()
        low_close_prev = (df["low"] - df["close"].shift(1)).abs()
        
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        return atr.fillna(0.0)

    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculates the Average Directional Index (ADX) representing trend strength.

        Args:
            df (pd.DataFrame): OHLCV DataFrame. Must have high, low, close.
            period (int): Period length for ADX calculation. Defaults to 14.

        Returns:
            pd.Series: A Pandas Series representing the ADX.
        """
        if len(df) <= period * 2:
            return pd.Series([20.0] * len(df), index=df.index)

        up_move = df["high"].diff()
        down_move = df["low"].shift(1) - df["low"]

        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)

        # TR calculation
        high_low = df["high"] - df["low"]
        high_close_prev = (df["high"] - df["close"].shift(1)).abs()
        low_close_prev = (df["low"] - df["close"].shift(1)).abs()
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

        # Wilders Smoothing
        tr_smoothed = tr.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        plus_dm_smoothed = pd.Series(plus_dm, index=df.index).ewm(alpha=1/period, min_periods=period, adjust=False).mean()
        minus_dm_smoothed = pd.Series(minus_dm, index=df.index).ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        plus_di = 100 * (plus_dm_smoothed / tr_smoothed.replace(0, 1e-9))
        minus_di = 100 * (minus_dm_smoothed / tr_smoothed.replace(0, 1e-9))

        dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, 1e-9)
        adx = dx.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

        return adx.fillna(20.0)

    @classmethod
    def apply_all(cls, df: pd.DataFrame, ema_fast: int = 9, ema_slow: int = 21, rsi_period: int = 14) -> pd.DataFrame:
        """Applies EMA fast, EMA slow, RSI, ATR, and ADX indicators to the OHLCV DataFrame.

        Args:
            df (pd.DataFrame): The input OHLCV DataFrame.
            ema_fast (int): The fast EMA period. Defaults to 9.
            ema_slow (int): The slow EMA period. Defaults to 21.
            rsi_period (int): The RSI period. Defaults to 14.

        Returns:
            pd.DataFrame: A copy of the input DataFrame with new indicator columns appended.
        """
        df = df.copy()
        df["ema_fast"] = cls.calculate_ema(df, period=ema_fast)
        df["ema_slow"] = cls.calculate_ema(df, period=ema_slow)
        df["rsi"] = cls.calculate_rsi(df, period=rsi_period)
        df["atr"] = cls.calculate_atr(df, period=rsi_period)
        df["adx"] = cls.calculate_adx(df, period=rsi_period)
        return df
