import pandas as pd
from typing import Dict, Any, Optional
from app.services.interfaces import BaseStrategy
from loguru import logger

class EMARSIStrategy(BaseStrategy):
    """EMA Crossover Strategy with RSI confirmation filters."""

    def __init__(self):
        self.params: Dict[str, Any] = {}

    def initialize(self, parameters: Dict[str, Any]):
        """Sets the parameters for indicator computation and signal generation."""
        self.params = {
            "ema_fast": int(parameters.get("ema_fast", 9)),
            "ema_slow": int(parameters.get("ema_slow", 21)),
            "rsi_period": int(parameters.get("rsi_period", 14)),
            "rsi_oversold": float(parameters.get("rsi_oversold", 35.0)),
            "rsi_overbought": float(parameters.get("rsi_overbought", 65.0)),
            "stop_loss_pct": float(parameters.get("stop_loss_pct", 1.5)),
            "take_profit_pct": float(parameters.get("take_profit_pct", 3.0)),
            "use_atr": bool(parameters.get("use_atr", False)),
            "atr_multiplier_sl": float(parameters.get("atr_multiplier_sl", 2.0)),
            "atr_multiplier_tp": float(parameters.get("atr_multiplier_tp", 4.0)),
            "use_adx_filter": bool(parameters.get("use_adx_filter", True)),
            "adx_threshold": float(parameters.get("adx_threshold", 20.0)),
            "adx_period": int(parameters.get("adx_period", 14))
        }
        logger.info(f"EMARSIStrategy initialized with params: {self.params}")

    def generate_signal(self, df: pd.DataFrame) -> str:
        """Evaluates Golden Cross crossover and RSI thresholds.

        Returns:
            str: 'BUY' for bullish golden cross, 'SELL' for death cross, or 'NEUTRAL'.
        """
        if len(df) < 2:
            return "NEUTRAL"

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Extract values
        ema_fast = float(last_row["ema_fast"]) if not pd.isna(last_row["ema_fast"]) else last_row["close"]
        ema_slow = float(last_row["ema_slow"]) if not pd.isna(last_row["ema_slow"]) else last_row["close"]
        prev_ema_fast = float(prev_row["ema_fast"]) if not pd.isna(prev_row["ema_fast"]) else prev_row["close"]
        prev_ema_slow = float(prev_row["ema_slow"]) if not pd.isna(prev_row["ema_slow"]) else prev_row["close"]
        rsi = float(last_row["rsi"]) if not pd.isna(last_row["rsi"]) else 50.0

        # Golden Cross check
        is_golden_cross = (prev_ema_fast <= prev_ema_slow) and (ema_fast > ema_slow)
        # Death Cross check
        is_death_cross = (prev_ema_fast >= prev_ema_slow) and (ema_fast < ema_slow)

        if is_golden_cross or rsi <= self.params["rsi_oversold"]:
            return "BUY"
        elif is_death_cross or rsi >= self.params["rsi_overbought"]:
            return "SELL"

        return "NEUTRAL"

    def confirm_signal(self, df: pd.DataFrame, signal: str) -> bool:
        """Confirms the signal using RSI and ADX trend strength filters."""
        if len(df) == 0:
            return False

        last_row = df.iloc[-1]
        rsi = float(last_row["rsi"]) if not pd.isna(last_row["rsi"]) else 50.0

        # ADX Trend Strength Filter Check
        if self.params.get("use_adx_filter", True) and "adx" in df.columns:
            adx = float(last_row["adx"]) if not pd.isna(last_row["adx"]) else 20.0
            if adx < self.params.get("adx_threshold", 20.0):
                logger.info(f"Signal {signal} REJECTED: ADX Trend Strength ({adx:.2f}) is below threshold ({self.params.get('adx_threshold')})")
                return False

        if signal == "BUY":
            # For buy, confirm only if not overbought
            return rsi < self.params["rsi_overbought"]
        elif signal == "SELL":
            # For sell, confirm only if not oversold
            return rsi > self.params["rsi_oversold"]

        return False

    def calculate_stop_loss(self, entry_price: float, side: str, df: Optional[pd.DataFrame] = None) -> float:
        """Calculates stop loss using percentage or ATR.

        Returns:
            float: Target stop loss price.
        """
        # If ATR is enabled and df is provided, use ATR-based SL
        if self.params["use_atr"] and df is not None and len(df) > 0 and "atr" in df.columns:
            atr = float(df.iloc[-1]["atr"])
            atr_sl = self.params["atr_multiplier_sl"] * atr
            if side == "BUY":
                return entry_price - atr_sl
            else:
                return entry_price + atr_sl

        # Fallback to percentage-based stop loss
        sl_pct = self.params["stop_loss_pct"] / 100.0
        if side == "BUY":
            return entry_price * (1 - sl_pct)
        else:
            return entry_price * (1 + sl_pct)

    def calculate_take_profit(self, entry_price: float, side: str, df: Optional[pd.DataFrame] = None) -> float:
        """Calculates take profit using percentage or ATR.

        Returns:
            float: Target take profit price.
        """
        # If ATR is enabled and df is provided, use ATR-based TP
        if self.params["use_atr"] and df is not None and len(df) > 0 and "atr" in df.columns:
            atr = float(df.iloc[-1]["atr"])
            atr_tp = self.params["atr_multiplier_tp"] * atr
            if side == "BUY":
                return entry_price + atr_tp
            else:
                return entry_price - atr_tp

        # Fallback to percentage-based take profit
        tp_pct = self.params["take_profit_pct"] / 100.0
        if side == "BUY":
            return entry_price * (1 + tp_pct)
        else:
            return entry_price * (1 - tp_pct)

    def manage_trade(self, position: Dict[str, Any], current_price: float, df: Optional[pd.DataFrame] = None) -> Optional[str]:
        """Provides default check for hard SL/TP triggers.

        Returns:
            str: Close reason ('STOP_LOSS' or 'TAKE_PROFIT') if triggered, else None.
        """
        side = position["side"]
        sl_price = position["sl_price"]
        tp_price = position["tp_price"]

        if side == "BUY":
            if current_price <= sl_price:
                return "STOP_LOSS"
            elif current_price >= tp_price:
                return "TAKE_PROFIT"
        elif side == "SELL":
            if current_price >= sl_price:
                return "STOP_LOSS"
            elif current_price <= tp_price:
                return "TAKE_PROFIT"

        return None

    def on_position_closed(self, trade: Dict[str, Any]):
        logger.info(f"Strategy callback: Position closed for trade {trade.get('id')} with PnL ${trade.get('pnl')}")
