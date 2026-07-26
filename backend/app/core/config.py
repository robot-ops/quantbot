import os
import json
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
YAML_FILE = os.path.join(BASE_DIR, "config.yaml")

class AccountConfig(BaseModel):
    id: str
    broker: str
    mode: str
    api_key: str = ""
    api_secret: str = ""

class StrategyConfig(BaseModel):
    name: str
    enabled: bool = True
    symbols: List[str] = []
    parameters: Dict[str, Any] = {}

class BotConfig(BaseModel):
    trading_mode: str = "demo"
    symbol: str = "BTC/USDT"
    timeframe: str = "15m"
    
    # Strategy Parameters
    ema_fast: int = 9
    ema_slow: int = 21
    rsi_period: int = 14
    rsi_oversold: float = 35.0
    rsi_overbought: float = 65.0
    stop_loss_pct: float = 1.5
    take_profit_pct: float = 3.0
    risk_per_trade_pct: float = 1.0
    max_daily_drawdown_pct: float = 3.0

    # Risk Control Switches
    use_trailing_stop: bool = False
    trail_pct: float = 1.0
    use_break_even: bool = False
    break_even_pct: float = 1.5
    use_partial_close: bool = False
    partial_close_pct: float = 1.5

    # Telegram Credentials
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    # Live Exchange API Credentials
    exchange_id: str = "tokocrypto"
    exchange_api_key: str = ""
    exchange_api_secret: str = ""

    # Extended/New parameters for enterprise scalability
    database_url: str = "sqlite:///quantbot.db"
    accounts: List[AccountConfig] = []
    symbols: List[str] = ["BTC/USDT", "ETH/USDT"]
    strategies: List[StrategyConfig] = []

    def save(self) -> bool:
        """Saves configuration to both config.yaml and legacy settings.json for compatibility."""
        try:
            # Save to config.yaml
            with open(YAML_FILE, "w", encoding="utf-8") as f:
                yaml.safe_dump(self.dict(), f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved configuration to {YAML_FILE}")
            
            # Save to settings.json for backward compatibility with existing components
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.dict(), f, indent=2)
            logger.info(f"Saved configuration legacy state to {SETTINGS_FILE}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False

def load_config() -> BotConfig:
    """Loads configuration by merging config.yaml, legacy settings.json, and environment variables."""
    merged_data: Dict[str, Any] = {}

    # 1. Load from config.yaml if it exists
    if os.path.exists(YAML_FILE):
        try:
            with open(YAML_FILE, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
                if isinstance(yaml_data, dict):
                    merged_data.update(yaml_data)
                    logger.info(f"Loaded config from YAML: {YAML_FILE}")
        except Exception as e:
            logger.error(f"Failed to parse config.yaml: {e}")

    # 2. Fallback to settings.json if YAML load didn't provide everything (or as secondary merge)
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                if isinstance(json_data, dict):
                    for k, v in json_data.items():
                        if k not in merged_data or not merged_data[k]:
                            merged_data[k] = v
                    logger.info(f"Merged legacy config from JSON: {SETTINGS_FILE}")
        except Exception as e:
            logger.error(f"Failed to parse settings.json: {e}")

    # 3. Override/Fallback with Environment Variables (with prefix or match case)
    env_mappings = {
        "TRADING_MODE": "trading_mode",
        "SYMBOL": "symbol",
        "TIMEFRAME": "timeframe",
        "EMA_FAST": "ema_fast",
        "EMA_SLOW": "ema_slow",
        "RSI_PERIOD": "rsi_period",
        "RSI_OVERSOLD": "rsi_oversold",
        "RSI_OVERBOUGHT": "rsi_overbought",
        "STOP_LOSS_PCT": "stop_loss_pct",
        "TAKE_PROFIT_PCT": "take_profit_pct",
        "RISK_PER_TRADE_PCT": "risk_per_trade_pct",
        "MAX_DAILY_DRAWDOWN_PCT": "max_daily_drawdown_pct",
        "TELEGRAM_BOT_TOKEN": "telegram_bot_token",
        "TELEGRAM_CHAT_ID": "telegram_chat_id",
        "EXCHANGE_ID": "exchange_id",
        "EXCHANGE_API_KEY": "exchange_api_key",
        "EXCHANGE_API_SECRET": "exchange_api_secret",
        "DATABASE_URL": "database_url",
        "USE_TRAILING_STOP": "use_trailing_stop",
        "TRAIL_PCT": "trail_pct",
        "USE_BREAK_EVEN": "use_break_even",
        "BREAK_EVEN_PCT": "break_even_pct",
        "USE_PARTIAL_CLOSE": "use_partial_close",
        "PARTIAL_CLOSE_PCT": "partial_close_pct",
    }
    
    for env_key, config_key in env_mappings.items():
        val = os.getenv(env_key)
        if val is not None:
            # Convert type based on defaults
            default_val = getattr(BotConfig, config_key, None)
            if isinstance(default_val, bool):
                merged_data[config_key] = val.lower() in ("true", "1", "yes")
            elif isinstance(default_val, int):
                merged_data[config_key] = int(val)
            elif isinstance(default_val, float):
                merged_data[config_key] = float(val)
            else:
                merged_data[config_key] = val

    # Build Pydantic model
    return BotConfig(**merged_data)

config = load_config()
