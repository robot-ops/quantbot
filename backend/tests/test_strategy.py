import pandas as pd
from unittest.mock import MagicMock, patch
from app.services.strategy import TradingBotStrategy
from app.db.repositories import TradeRepository

@patch("app.services.strategy.TechnicalIndicators.apply_all")
@patch("app.services.strategy.SessionLocal")
def test_evaluate_market_tick_buy(mock_session_local, mock_apply_all, test_db, test_config):
    # Setup database mocks
    mock_session_local.return_value.__enter__.return_value = test_db
    
    # Setup indicator calculation mock to bypass recalculating the custom crossover
    mock_apply_all.side_effect = lambda df, **kwargs: df
    
    # Create the bot orchestrator instance
    bot = TradingBotStrategy()
    bot.config = test_config
    bot.strategy.initialize(test_config.dict())
    
    # Setup mock data frame for EMA Golden Cross confirmation
    # We need fast EMA to cross slow EMA upwards, and RSI below overbought
    # index order: 0 to 49
    prices = [10.0] * 48 + [9.5, 11.0] # Golden cross on the last step
    ema_fast = [10.0] * 48 + [9.8, 10.5]
    ema_slow = [10.0] * 48 + [10.0, 10.2]
    rsi = [50.0] * 50
    atr = [0.5] * 50
    
    mock_df = pd.DataFrame({
        "timestamp": range(50),
        "open": prices,
        "high": prices,
        "low": prices,
        "close": prices,
        "volume": [1.0] * 50,
        "ema_fast": ema_fast,
        "ema_slow": ema_slow,
        "rsi": rsi,
        "atr": atr
    })
    
    # Mock CCXTBroker calls
    bot.ccxt_service.fetch_ohlcv = MagicMock(return_value=mock_df)
    bot.ccxt_service.fetch_ticker = MagicMock(return_value=11.0)
    bot.telegram_service.send_trade_open_alert = MagicMock()
    
    # Enable running to allow buy signal evaluation
    bot.is_running = True
    bot.daily_starting_balance = 10000.0
    
    # Execute tick
    res = bot.evaluate_market_tick()
    
    assert res["status"] == "ok"
    assert res["price"] == 11.0
    
    # Verify that a trade was opened in the database
    trade_repo = TradeRepository(test_db)
    pos = trade_repo.get_active_position(mode="DEMO")
    assert pos is not None
    assert pos.symbol == "BTC/USDT"
    assert pos.side == "BUY"
    assert pos.entry_price == 11.0
