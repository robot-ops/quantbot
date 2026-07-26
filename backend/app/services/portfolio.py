import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.repositories import TradeRepository, PerformanceRepository
from app.services.interfaces import BaseBroker
from loguru import logger

class PortfolioManager:
    """Manages trading balances, tracks performance, and logs equity curves."""

    def __init__(self, db: Session, broker: BaseBroker, mode: str = "DEMO", initial_balance: float = 10000.0):
        self.db = db
        self.broker = broker
        self.mode = mode.upper()
        self.initial_balance = initial_balance
        self.trade_repo = TradeRepository(db)
        self.perf_repo = PerformanceRepository(db)

    def get_stats(self, current_price: float = 0.0) -> Dict[str, Any]:
        """Calculates closed trades stats, win rates, and unrealized PnL of open positions."""
        # Query closed trades
        trades = self.trade_repo.get_all(mode=self.mode, limit=1000)
        closed_trades = [t for t in trades if t.closed_at is not None]
        
        total_trades = len(closed_trades)
        winning_trades = sum(1 for t in closed_trades if t.pnl and t.pnl > 0)
        losing_trades = sum(1 for t in closed_trades if t.pnl and t.pnl < 0)
        win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
        total_pnl = sum(t.pnl for t in closed_trades if t.pnl is not None)

        # Get current balance from broker
        broker_bal = self.broker.fetch_balance()
        balance = float(broker_bal.get("USDT", {}).get("free", 0.0))
        if balance == 0.0 and self.mode == "DEMO":
            # Fallback if paper broker has not been initialized fully
            balance = self.initial_balance + total_pnl

        # Calculate PnL percent based on initial capital
        total_pnl_pct = ((balance - self.initial_balance) / self.initial_balance) * 100.0

        # Calculate unrealized PnL
        active_pos = self.trade_repo.get_active_position(mode=self.mode)
        unrealized_pnl = 0.0
        unrealized_pnl_pct = 0.0
        
        active_pos_dict = None
        if active_pos:
            cost = active_pos.cost
            if current_price > 0:
                if active_pos.side == "BUY":
                    unrealized_pnl = (current_price - active_pos.entry_price) * active_pos.amount
                else:
                    unrealized_pnl = (active_pos.entry_price - current_price) * active_pos.amount
                unrealized_pnl_pct = (unrealized_pnl / cost) * 100.0 if cost > 0 else 0.0

            active_pos_dict = {
                "id": f"DB-POS-{active_pos.id}",
                "symbol": active_pos.symbol,
                "side": active_pos.side,
                "entry_price": active_pos.entry_price,
                "amount": active_pos.amount,
                "cost": active_pos.cost,
                "sl_price": active_pos.exit_price or (active_pos.entry_price * 0.985), # default SL placeholder
                "tp_price": active_pos.exit_price or (active_pos.entry_price * 1.03), # default TP placeholder
                "opened_at": active_pos.opened_at.isoformat(),
                "mode": active_pos.mode
            }

        return {
            "balance": round(balance, 2),
            "initial_balance": round(self.initial_balance, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
            "win_rate": round(win_rate, 1),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "active_position": active_pos_dict
        }

    def record_performance_snapshot(self, current_price: float):
        """Records current equity and trade stats snapshot in the performance database."""
        stats = self.get_stats(current_price)
        total_equity = stats["balance"] + stats["unrealized_pnl"]
        drawdown_pct = 0.0
        
        # Calculate drawdown against initial balance or historical peak
        latest_perf = self.perf_repo.get_latest(mode=self.mode)
        peak_equity = max(latest_perf.total_equity if latest_perf else self.initial_balance, total_equity)
        if peak_equity > 0:
            drawdown_pct = ((peak_equity - total_equity) / peak_equity) * 100.0

        self.perf_repo.create(
            balance=stats["balance"],
            total_equity=total_equity,
            drawdown_pct=drawdown_pct,
            win_rate=stats["win_rate"],
            total_trades=stats["total_trades"],
            winning_trades=stats["winning_trades"],
            losing_trades=stats["losing_trades"],
            mode=self.mode
        )
        logger.debug(f"Performance snapshot recorded. Mode: {self.mode}, Equity: ${total_equity:.2f}")
