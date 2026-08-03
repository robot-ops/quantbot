import pandas as pd
from typing import Dict, Any, Optional, Tuple
from loguru import logger

class RiskManager:
    """Handles quant risk management, sizing, drawdowns, and dynamic exits."""

    def __init__(self):
        pass

    def calculate_position_size(
        self, 
        current_price: float, 
        balance: float, 
        risk_per_trade_pct: float, 
        stop_loss_pct: float,
        max_allocation_pct: float = 25.0,
        min_order_value: float = 1.0
    ) -> float:
        """Calculates position size dynamically based on equity risk and maximum allocation.
        Supports micro-balances and precision for BTC and other crypto assets.

        Args:
            current_price (float): The current spot price of the asset.
            balance (float): The current cash balance or total equity.
            risk_per_trade_pct (float): Percentage of equity to risk per trade.
            stop_loss_pct (float): The stop loss distance in percentage.
            max_allocation_pct (float): Maximum portion of equity to allocate to the position. Defaults to 25.0%.
            min_order_value (float): Minimum order value in USDT. Defaults to 1.0.

        Returns:
            float: Amount of asset to trade.
        """
        if current_price <= 0 or balance <= 0:
            return 0.0

        risk_pct = risk_per_trade_pct / 100.0
        sl_pct = stop_loss_pct / 100.0
        
        capital_to_risk = balance * risk_pct
        position_value = capital_to_risk / sl_pct if sl_pct > 0 else balance * 0.1
        
        # Risk control constraint: Allocate max percentage of balance
        max_cost = balance * (max_allocation_pct / 100.0)
        actual_cost = min(position_value, max_cost)
        
        # Micro-balance adjustment: If balance is sufficient to cover min_order_value (e.g., $10 USDT)
        # but the standard risk allocation yields less than min_order_value, adjust actual_cost.
        if balance >= min_order_value and actual_cost < min_order_value:
            micro_cost = balance * 0.95  # Allocate up to 95% of balance (leaving 5% for fees/buffer)
            if micro_cost >= min_order_value:
                actual_cost = micro_cost
                logger.info(f"Micro-balance detected (${balance:.2f} USDT). Adjusted order cost to ${actual_cost:.2f} USDT to meet minimum order value (${min_order_value:.2f} USDT).")

        amount = actual_cost / current_price
        
        # Dynamic precision rounding up to 8 decimal places (Satoshi level for BTC)
        if amount < 0.01:
            return round(amount, 8)
        elif amount < 1.0:
            return round(amount, 6)
        else:
            return round(amount, 4)

    def check_daily_drawdown(
        self, 
        starting_balance: float, 
        current_equity: float, 
        max_daily_drawdown_pct: float
    ) -> Tuple[bool, float]:
        """Checks if the daily loss limit has been breached.

        Args:
            starting_balance (float): The balance at the start of the day.
            current_equity (float): The current total equity (cash + open positions).
            max_daily_drawdown_pct (float): The maximum allowed percentage loss.

        Returns:
            Tuple[bool, float]: (is_breached, drawdown_percentage)
        """
        if starting_balance <= 0:
            return False, 0.0
        
        drawdown_pct = ((starting_balance - current_equity) / starting_balance) * 100.0
        is_breached = drawdown_pct >= max_daily_drawdown_pct
        return is_breached, drawdown_pct

    def evaluate_trailing_stop(
        self, 
        entry_price: float, 
        current_price: float, 
        current_sl: float, 
        side: str, 
        trail_pct: float = 1.0
    ) -> float:
        """Dynamically calculates trailing stop updates based on peak prices.

        Args:
            entry_price (float): The initial entry price.
            current_price (float): The current asset price.
            current_sl (float): The current stop loss price.
            side (str): 'BUY' or 'SELL'.
            trail_pct (float): Percentage to trail the price by.

        Returns:
            float: The updated (or unchanged) stop loss price.
        """
        trail_dist = current_price * (trail_pct / 100.0)
        
        if side.upper() == "BUY":
            # For buy, trail upwards. SL can only move up.
            new_sl = current_price - trail_dist
            if new_sl > current_sl:
                logger.debug(f"Trailing stop adjusted up from {current_sl:.2f} to {new_sl:.2f}")
                return new_sl
        else:
            # For sell, trail downwards. SL can only move down.
            new_sl = current_price + trail_dist
            if current_sl == 0.0 or new_sl < current_sl:
                logger.debug(f"Trailing stop adjusted down from {current_sl:.2f} to {new_sl:.2f}")
                return new_sl
                
        return current_sl

    def evaluate_break_even(
        self, 
        entry_price: float, 
        current_price: float, 
        current_sl: float, 
        side: str, 
        trigger_profit_pct: float = 1.5
    ) -> float:
        """Moves stop loss to entry price (break-even) once trade reaches target profit.

        Args:
            entry_price (float): Entry price of the position.
            current_price (float): Current price.
            current_sl (float): Current stop loss price.
            side (str): 'BUY' or 'SELL'.
            trigger_profit_pct (float): Percentage profit required to trigger break-even.

        Returns:
            float: The updated stop-loss price (equal to entry_price if triggered).
        """
        if side.upper() == "BUY":
            # Check if profit threshold reached
            profit_pct = ((current_price - entry_price) / entry_price) * 100.0
            if profit_pct >= trigger_profit_pct and current_sl < entry_price:
                logger.info(f"Break-even triggered: moving SL to entry price {entry_price}")
                return entry_price
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100.0
            if profit_pct >= trigger_profit_pct and (current_sl > entry_price or current_sl == 0.0):
                logger.info(f"Break-even triggered: moving SL to entry price {entry_price}")
                return entry_price
                
        return current_sl

    def evaluate_partial_close(
        self, 
        entry_price: float, 
        current_price: float, 
        side: str, 
        target_pct: float = 1.5, 
        has_partially_closed: bool = False
    ) -> Tuple[bool, float]:
        """Triggers a 50% partial close once a profit target is hit.

        Args:
            entry_price (float): Entry price of the position.
            current_price (float): Current price.
            side (str): 'BUY' or 'SELL'.
            target_pct (float): Profit target percentage to trigger partial close.
            has_partially_closed (bool): Whether the position has already been partially closed.

        Returns:
            Tuple[bool, float]: (should_close_partial, close_ratio)
        """
        if has_partially_closed:
            return False, 0.0

        if side.upper() == "BUY":
            profit_pct = ((current_price - entry_price) / entry_price) * 100.0
        else:
            profit_pct = ((entry_price - current_price) / entry_price) * 100.0

        if profit_pct >= target_pct:
            logger.info(f"Partial close target reached at {profit_pct:.2f}% profit. Closing 50% of position.")
            return True, 0.5

        return False, 0.0
