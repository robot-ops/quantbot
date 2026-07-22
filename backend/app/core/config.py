import os
import json
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "settings.json")

def load_persisted_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                print(f"[BotConfig] Loaded persistent settings from {SETTINGS_FILE}")
                return data
        except Exception as e:
            print(f"[BotConfig] Error loading settings.json: {e}")
    return {}

persisted_settings = load_persisted_settings()

class BotConfig(BaseModel):
    trading_mode: str = persisted_settings.get("trading_mode") or os.getenv("TRADING_MODE", "demo")  # demo or live
    symbol: str = persisted_settings.get("symbol") or os.getenv("SYMBOL", "BTC/USDT")
    timeframe: str = persisted_settings.get("timeframe") or os.getenv("TIMEFRAME", "15m")  # 15-minute timeframe for clean signals
    
    # Strategy Parameters (Optimal Conservative Quant Settings)
    ema_fast: int = int(persisted_settings.get("ema_fast") if persisted_settings.get("ema_fast") is not None else os.getenv("EMA_FAST", "9"))
    ema_slow: int = int(persisted_settings.get("ema_slow") if persisted_settings.get("ema_slow") is not None else os.getenv("EMA_SLOW", "21"))
    rsi_period: int = int(persisted_settings.get("rsi_period") if persisted_settings.get("rsi_period") is not None else os.getenv("RSI_PERIOD", "14"))
    rsi_oversold: float = float(persisted_settings.get("rsi_oversold") if persisted_settings.get("rsi_oversold") is not None else os.getenv("RSI_OVERSOLD", "35.0"))
    rsi_overbought: float = float(persisted_settings.get("rsi_overbought") if persisted_settings.get("rsi_overbought") is not None else os.getenv("RSI_OVERBOUGHT", "65.0"))
    stop_loss_pct: float = float(persisted_settings.get("stop_loss_pct") if persisted_settings.get("stop_loss_pct") is not None else os.getenv("STOP_LOSS_PCT", "1.5"))
    take_profit_pct: float = float(persisted_settings.get("take_profit_pct") if persisted_settings.get("take_profit_pct") is not None else os.getenv("TAKE_PROFIT_PCT", "3.0"))
    risk_per_trade_pct: float = float(persisted_settings.get("risk_per_trade_pct") if persisted_settings.get("risk_per_trade_pct") is not None else os.getenv("RISK_PER_TRADE_PCT", "1.0"))  # 1% equity risk per trade
    max_daily_drawdown_pct: float = float(persisted_settings.get("max_daily_drawdown_pct") if persisted_settings.get("max_daily_drawdown_pct") is not None else os.getenv("MAX_DAILY_DRAWDOWN_PCT", "3.0"))  # 3% max daily loss limit

    # Telegram Credentials
    telegram_bot_token: str = persisted_settings.get("telegram_bot_token") or os.getenv("TELEGRAM_BOT_TOKEN", "8715791209:AAF0amWtezJBHDaGtaI-rEp1t8CLijqeGlQ")
    telegram_chat_id: str = persisted_settings.get("telegram_chat_id") or os.getenv("TELEGRAM_CHAT_ID", "2135434795")

    # Live Exchange API Credentials (Tokocrypto)
    exchange_id: str = persisted_settings.get("exchange_id") or os.getenv("EXCHANGE_ID", "tokocrypto")
    exchange_api_key: str = persisted_settings.get("exchange_api_key") or os.getenv("EXCHANGE_API_KEY", "349dC55f76799ccA8DC41c2c637C7b82zyLVgVrXWR6FreG2dlrQK8jHpH9bTl9e")
    exchange_api_secret: str = persisted_settings.get("exchange_api_secret") or os.getenv("EXCHANGE_API_SECRET", "0516EB8ec0C8fB49B344Ef8F316e1c06EPhqNcSVY8PHvr9Jcf9utONSQvgCVAJA")

    def save(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2)
            print(f"[BotConfig] Saved configuration to {SETTINGS_FILE}")
            return True
        except Exception as e:
            print(f"[BotConfig] Error saving config: {e}")
            return False

config = BotConfig()
