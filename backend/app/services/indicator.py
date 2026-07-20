import pandas as pd
import numpy as np

class TechnicalIndicators:
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int, column: str = "close") -> pd.Series:
        """Kalkulasi Exponential Moving Average (EMA)"""
        if len(df) < period:
            return pd.Series([np.nan] * len(df), index=df.index)
        return df[column].ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
        """Kalkulasi Relative Strength Index (RSI)"""
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

    @classmethod
    def apply_all(cls, df: pd.DataFrame, ema_fast: int = 9, ema_slow: int = 21, rsi_period: int = 14) -> pd.DataFrame:
        """Tambahkan kolom indikator ke dataframe OHLCV"""
        df = df.copy()
        df["ema_fast"] = cls.calculate_ema(df, period=ema_fast)
        df["ema_slow"] = cls.calculate_ema(df, period=ema_slow)
        df["rsi"] = cls.calculate_rsi(df, period=rsi_period)
        return df
