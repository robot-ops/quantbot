import os
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class BotConfig(BaseModel):
    trading_mode: str = os.getenv("TRADING_MODE", "demo")  # demo or live
    symbol: str = os.getenv("SYMBOL", "BTC/USDT")
    timeframe: str = os.getenv("TIMEFRAME", "15m")  # 15-minute timeframe for clean signals
    
    # Strategy Parameters (Optimal Conservative Quant Settings)
    ema_fast: int = int(os.getenv("EMA_FAST", "9"))
    ema_slow: int = int(os.getenv("EMA_SLOW", "21"))
    rsi_period: int = int(os.getenv("RSI_PERIOD", "14"))
    rsi_oversold: float = float(os.getenv("RSI_OVERSOLD", "35.0"))
    rsi_overbought: float = float(os.getenv("RSI_OVERBOUGHT", "65.0"))
    stop_loss_pct: float = float(os.getenv("STOP_LOSS_PCT", "1.5"))
    take_profit_pct: float = float(os.getenv("TAKE_PROFIT_PCT", "3.0"))
    risk_per_trade_pct: float = float(os.getenv("RISK_PER_TRADE_PCT", "1.0"))  # 1% equity risk per trade
    max_daily_drawdown_pct: float = float(os.getenv("MAX_DAILY_DRAWDOWN_PCT", "3.0"))  # 3% max daily loss limit

    # Telegram Credentials
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "8715791209:AAF0amWtezJBHDaGtaI-rEp1t8CLijqeGlQ")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "2135434795")

    # Live Exchange API Credentials (Tokocrypto)
    exchange_id: str = os.getenv("EXCHANGE_ID", "tokocrypto")
    exchange_api_key: str = os.getenv("EXCHANGE_API_KEY", "349dC55f76799ccA8DC41c2c637C7b82zyLVgVrXWR6FreG2dlrQK8jHpH9bTl9e")
    exchange_api_secret: str = os.getenv("EXCHANGE_API_SECRET", "0516EB8ec0C8fB49B344Ef8F316e1c06EPhqNcSVY8PHvr9Jcf9utONSQvgCVAJA")

config = BotConfig()
