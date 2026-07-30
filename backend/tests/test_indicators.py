import pandas as pd
import numpy as np
from app.services.indicator import TechnicalIndicators

def test_calculate_ema():
    # Make a series of close prices
    data = {"close": [10.0, 11.0, 12.0, 13.0, 14.0, 15.0]}
    df = pd.DataFrame(data)
    
    # Calculate EMA
    ema = TechnicalIndicators.calculate_ema(df, period=3)
    assert len(ema) == 6
    assert pd.isna(ema[0]) is False # Since length > period

def test_calculate_rsi():
    # Make a steady upward close series
    data = {"close": [100.0, 101.0, 102.0, 103.0, 104.0, 105.0, 106.0, 107.0]}
    df = pd.DataFrame(data)
    
    rsi = TechnicalIndicators.calculate_rsi(df, period=4)
    assert len(rsi) == 8
    # With steady gains, RSI should be high
    assert rsi.iloc[-1] > 50

def test_calculate_atr():
    # Constant range bar series
    data = {
        "open":  [100, 100, 100, 100, 100],
        "high":  [105, 105, 105, 105, 105],
        "low":   [95, 95, 95, 95, 95],
        "close": [100, 100, 100, 100, 100]
    }
    df = pd.DataFrame(data)
    
    atr = TechnicalIndicators.calculate_atr(df, period=3)
    assert len(atr) == 5
    # TR = 10, so ATR should settle around 10
    assert atr.iloc[-1] > 0

def test_calculate_adx():
    # Trending price series (steady upward trend)
    data = {
        "high":  [100 + i for i in range(40)],
        "low":   [98 + i for i in range(40)],
        "close": [99 + i for i in range(40)]
    }
    df = pd.DataFrame(data)
    
    adx = TechnicalIndicators.calculate_adx(df, period=10)
    assert len(adx) == 40
    assert adx.iloc[-1] > 20.0
