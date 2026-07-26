from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, UniqueConstraint
from app.db.session import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    broker_trade_id = Column(String, index=True, nullable=True)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    sl_price = Column(Float, nullable=True)
    tp_price = Column(Float, nullable=True)
    peak_price = Column(Float, nullable=True)
    partial_closed = Column(Integer, default=0, nullable=False) # 0 = no, 1 = 50% closed
    amount = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)
    close_reason = Column(String, nullable=True)  # STOP_LOSS, TAKE_PROFIT, MANUAL
    opened_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    mode = Column(String, index=True, default="DEMO", nullable=False)  # DEMO, LIVE

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    broker_order_id = Column(String, index=True, nullable=True)
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    type = Column(String, default="market", nullable=False)  # market, limit
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=True)
    status = Column(String, index=True, nullable=False)  # open, closed, canceled, rejected
    filled_amount = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    mode = Column(String, index=True, default="DEMO", nullable=False)  # DEMO, LIVE

class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, nullable=False)
    type = Column(String, nullable=False)  # BUY, SELL, NEUTRAL
    indicator_values = Column(JSON, nullable=True)  # Store EMA, RSI values, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    balance = Column(Float, nullable=False)
    total_equity = Column(Float, nullable=False)
    drawdown_pct = Column(Float, default=0.0, nullable=False)
    win_rate = Column(Float, default=0.0, nullable=False)
    total_trades = Column(Integer, default=0, nullable=False)
    winning_trades = Column(Integer, default=0, nullable=False)
    losing_trades = Column(Integer, default=0, nullable=False)
    mode = Column(String, index=True, default="DEMO", nullable=False)

class LogEntry(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    level = Column(String, nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(String, nullable=False)

class MarketDataCache(Base):
    __tablename__ = "market_data_cache"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("symbol", "timeframe", "timestamp", name="uq_market_data_candle"),
    )
