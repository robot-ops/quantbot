from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.models import Trade, Order, Signal, Performance, LogEntry, MarketDataCache
from typing import List, Optional, Dict, Any
from datetime import datetime

class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

class TradeRepository(BaseRepository):
    def get_all(self, mode: str = "DEMO", limit: int = 100) -> List[Trade]:
        return self.db.query(Trade).filter(
            Trade.mode == mode.upper()
        ).order_by(desc(Trade.opened_at)).limit(limit).all()

    def get_by_id(self, trade_id: int) -> Optional[Trade]:
        return self.db.query(Trade).filter(Trade.id == trade_id).first()

    def get_active_position(self, mode: str = "DEMO") -> Optional[Trade]:
        return self.db.query(Trade).filter(
            Trade.mode == mode.upper(),
            Trade.closed_at.is_(None)
        ).first()

    def create(self, symbol: str, side: str, entry_price: float, amount: float, cost: float, mode: str = "DEMO", broker_trade_id: str = None, sl_price: float = None, tp_price: float = None) -> Trade:
        trade = Trade(
            symbol=symbol,
            side=side.upper(),
            entry_price=entry_price,
            amount=amount,
            cost=cost,
            mode=mode.upper(),
            broker_trade_id=broker_trade_id,
            sl_price=sl_price,
            tp_price=tp_price,
            peak_price=entry_price,  # Initial peak price is entry price
            partial_closed=0,
            opened_at=datetime.utcnow()
        )
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)
        return trade

    def update_risk_parameters(self, trade_id: int, sl_price: float, tp_price: float, peak_price: float, partial_closed: int) -> Optional[Trade]:
        trade = self.get_by_id(trade_id)
        if trade:
            trade.sl_price = sl_price
            trade.tp_price = tp_price
            trade.peak_price = peak_price
            trade.partial_closed = partial_closed
            self.db.commit()
            self.db.refresh(trade)
        return trade

    def close(self, trade_id: int, exit_price: float, pnl: float, pnl_pct: float, reason: str) -> Optional[Trade]:
        trade = self.get_by_id(trade_id)
        if trade:
            trade.exit_price = exit_price
            trade.pnl = pnl
            trade.pnl_pct = pnl_pct
            trade.close_reason = reason
            trade.closed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(trade)
        return trade

    def get_stats(self, mode: str = "DEMO") -> Dict[str, Any]:
        trades = self.db.query(Trade).filter(Trade.mode == mode.upper(), Trade.closed_at.is_not(None)).all()
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
        losing_trades = sum(1 for t in trades if t.pnl and t.pnl < 0)
        win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": round(win_rate, 1),
            "total_pnl": round(total_pnl, 4)
        }

class OrderRepository(BaseRepository):
    def get_all(self, mode: str = "DEMO", limit: int = 100) -> List[Order]:
        return self.db.query(Order).filter(Order.mode == mode.upper()).order_by(desc(Order.created_at)).limit(limit).all()

    def get_by_broker_id(self, broker_order_id: str) -> Optional[Order]:
        return self.db.query(Order).filter(Order.broker_order_id == broker_order_id).first()

    def create(self, symbol: str, side: str, amount: float, price: Optional[float], status: str, mode: str = "DEMO", broker_order_id: Optional[str] = None, order_type: str = "market") -> Order:
        order = Order(
            broker_order_id=broker_order_id,
            symbol=symbol,
            side=side.upper(),
            type=order_type,
            amount=amount,
            price=price,
            status=status.lower(),
            filled_amount=amount if status.lower() == "closed" else 0.0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            mode=mode.upper()
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order

    def update_status(self, order_id: int, status: str, filled_amount: float = 0.0) -> Optional[Order]:
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = status.lower()
            order.filled_amount = filled_amount
            order.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(order)
        return order

class SignalRepository(BaseRepository):
    def create(self, symbol: str, timeframe: str, signal_type: str, indicator_values: Dict[str, Any]) -> Signal:
        sig = Signal(
            symbol=symbol,
            timeframe=timeframe,
            type=signal_type.upper(),
            indicator_values=indicator_values,
            created_at=datetime.utcnow()
        )
        self.db.add(sig)
        self.db.commit()
        self.db.refresh(sig)
        return sig

class PerformanceRepository(BaseRepository):
    def create(self, balance: float, total_equity: float, drawdown_pct: float, win_rate: float, total_trades: int, winning_trades: int, losing_trades: int, mode: str = "DEMO") -> Performance:
        perf = Performance(
            balance=balance,
            total_equity=total_equity,
            drawdown_pct=drawdown_pct,
            win_rate=win_rate,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            mode=mode.upper(),
            timestamp=datetime.utcnow()
        )
        self.db.add(perf)
        self.db.commit()
        self.db.refresh(perf)
        return perf

    def get_latest(self, mode: str = "DEMO") -> Optional[Performance]:
        return self.db.query(Performance).filter(Performance.mode == mode.upper()).order_by(desc(Performance.timestamp)).first()

class LogRepository(BaseRepository):
    def create(self, level: str, message: str) -> LogEntry:
        log_entry = LogEntry(
            level=level.upper(),
            message=message,
            timestamp=datetime.utcnow()
        )
        self.db.add(log_entry)
        self.db.commit()
        self.db.refresh(log_entry)
        return log_entry

    def get_latest(self, limit: int = 100) -> List[LogEntry]:
        return self.db.query(LogEntry).order_by(desc(LogEntry.timestamp)).limit(limit).all()

class MarketDataCacheRepository(BaseRepository):
    def save_candles(self, symbol: str, timeframe: str, candles: List[List[Any]]):
        """Saves a list of candles [[timestamp, open, high, low, close, volume], ...] directly to cache."""
        for c in candles:
            ts_dt = datetime.utcfromtimestamp(c[0] / 1000)
            existing = self.db.query(MarketDataCache).filter(
                MarketDataCache.symbol == symbol,
                MarketDataCache.timeframe == timeframe,
                MarketDataCache.timestamp == ts_dt
            ).first()
            if not existing:
                cached = MarketDataCache(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=ts_dt,
                    open=float(c[1]),
                    high=float(c[2]),
                    low=float(c[3]),
                    close=float(c[4]),
                    volume=float(c[5])
                )
                self.db.add(cached)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()

    def get_candles(self, symbol: str, timeframe: str, limit: int = 100) -> List[MarketDataCache]:
        return self.db.query(MarketDataCache).filter(
            MarketDataCache.symbol == symbol,
            MarketDataCache.timeframe == timeframe
        ).order_by(desc(MarketDataCache.timestamp)).limit(limit).all()
