import os
import sys
from loguru import logger

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

APP_LOG = os.path.join(LOG_DIR, "app.json.log")
TRADE_LOG = os.path.join(LOG_DIR, "trades.json.log")
PERF_LOG = os.path.join(LOG_DIR, "performance.json.log")

def filter_trade(record):
    return record["extra"].get("type") == "trade"

def filter_performance(record):
    return record["extra"].get("type") == "performance"

def filter_app(record):
    # App log contains everything except specific trade/performance markers, or can contain everything for debugging
    return record["extra"].get("type") not in ("trade", "performance")

def setup_logging():
    """Initializes Loguru with multiple handlers: Console, App JSON, Trades JSON, and Performance JSON."""
    # Clear existing handlers to prevent double logs
    logger.remove()

    # 1. Console Output (formatted and colored)
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True
    )

    # 2. Main App Log (Structured JSON, Rotating)
    logger.add(
        APP_LOG,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
        level="DEBUG",
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        serialize=True, # Structured JSON output
        filter=filter_app
    )

    # 3. Trade Log (Structured JSON, Rotating, filter for trade events)
    logger.add(
        TRADE_LOG,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO",
        rotation="5 MB",
        retention="90 days",
        compression="zip",
        serialize=True,
        filter=filter_trade
    )

    # 4. Performance & Latency Log (Structured JSON, Rotating, filter for latency profiles)
    logger.add(
        PERF_LOG,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
        level="INFO",
        rotation="5 MB",
        retention="90 days",
        compression="zip",
        serialize=True,
        filter=filter_performance
    )

    logger.info("Structured Logging System Configured.")
