import pandas as pd
from typing import Dict, Optional, List, Any
from abc import ABC, abstractmethod

class BaseBroker(ABC):
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> float:
        """Fetch the current spot price for a given symbol."""
        pass

    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> pd.DataFrame:
        """Fetch historical candle data (OHLCV)."""
        pass

    @abstractmethod
    def execute_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Execute a market or limit order on the broker."""
        pass

    @abstractmethod
    def fetch_balance(self) -> Dict[str, Any]:
        """Fetch current asset balances, focusing on the quote asset (e.g. USDT)."""
        pass

class BaseStrategy(ABC):
    @abstractmethod
    def initialize(self, parameters: Dict[str, Any]):
        """Initialize strategy-specific parameters."""
        pass

    @abstractmethod
    def generate_signal(self, df: pd.DataFrame) -> str:
        """Generate a raw signal (BUY, SELL, or NEUTRAL) based on market data."""
        pass

    @abstractmethod
    def confirm_signal(self, df: pd.DataFrame, signal: str) -> bool:
        """Perform secondary filters/checks to validate and confirm the raw signal."""
        pass

    @abstractmethod
    def calculate_stop_loss(self, entry_price: float, side: str, df: Optional[pd.DataFrame] = None) -> float:
        """Calculate the stop-loss price level."""
        pass

    @abstractmethod
    def calculate_take_profit(self, entry_price: float, side: str, df: Optional[pd.DataFrame] = None) -> float:
        """Calculate the take-profit price level."""
        pass

    @abstractmethod
    def manage_trade(self, position: Dict[str, Any], current_price: float, df: Optional[pd.DataFrame] = None) -> Optional[str]:
        """Evaluate open position for dynamic trade management (e.g. trailing stops, break-even updates).
        Returns close reason (e.g. STOP_LOSS, TAKE_PROFIT, TRAILING_STOP) if a close is triggered, else None.
        """
        pass

    @abstractmethod
    def on_position_closed(self, trade: Dict[str, Any]):
        """Callback hook triggered when a position is successfully closed."""
        pass

class NotificationService(ABC):
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if notification credentials are set."""
        pass

    @abstractmethod
    def send_message(self, message: str, mode: str = "demo") -> bool:
        """Send a basic status alert."""
        pass

    @abstractmethod
    def send_trade_open_alert(self, mode: str, symbol: str, side: str, price: float, amount: float, sl_price: float, tp_price: float):
        """Send a formatted notification when a new position opens."""
        pass

    @abstractmethod
    def send_trade_close_alert(self, mode: str, symbol: str, side: str, entry_price: float, exit_price: float, pnl: float, pnl_pct: float, reason: str):
        """Send a formatted notification when a position closes."""
        pass

    @abstractmethod
    def send_risk_alert(self, title: str, description: str, mode: str = "demo"):
        """Send a high-priority risk violation warning."""
        pass
