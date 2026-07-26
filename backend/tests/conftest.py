import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend folder is in path for test imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import Base
from app.core.config import BotConfig

@pytest.fixture(scope="function")
def test_db():
    """Create a clean in-memory database for each test case."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    db = SessionTesting()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_config():
    """Returns a test bot configuration instance."""
    return BotConfig(
        trading_mode="demo",
        symbol="BTC/USDT",
        timeframe="1m",
        ema_fast=9,
        ema_slow=21,
        rsi_period=14,
        rsi_oversold=30.0,
        rsi_overbought=70.0,
        stop_loss_pct=1.0,
        take_profit_pct=2.0,
        risk_per_trade_pct=1.0,
        max_daily_drawdown_pct=5.0,
        telegram_bot_token="test_token",
        telegram_chat_id="test_chat",
        exchange_id="binance",
        exchange_api_key="test_key",
        exchange_api_secret="test_secret"
    )
