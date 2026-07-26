import uvicorn
import os
from dotenv import load_dotenv
from app.core.logging_setup import setup_logging
from loguru import logger

load_dotenv()

if __name__ == "__main__":
    setup_logging()
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info("=======================================================")
    logger.info("🤖 QUANTBOT PRO — STARTUP DIAGNOSTIC HEALTH CHECK")
    logger.info("=======================================================")
    
    # 1. Check .env file
    env_exists = os.path.exists(".env")
    if env_exists:
        logger.info("Environment (.env): Loaded successfully")
    else:
        logger.warning("Environment (.env): File .env not found, using defaults")
    
    # 2. Check Telegram Credentials
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    telegram_ready = bool(token and chat_id)
    if telegram_ready:
        logger.info("Telegram Bot API: Configured")
    else:
        logger.warning("Telegram Bot API: Not configured")
    
    # 3. Check Live Exchange API Key
    ex_id = os.getenv("EXCHANGE_ID", "tokocrypto")
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    ex_ready = bool(api_key)
    if ex_ready:
        logger.info(f"Live Exchange ({ex_id.upper()}): API Key & Secret Ready")
    else:
        logger.info(f"Live Exchange ({ex_id.upper()}): Demo Mode active")
    
    logger.info("=======================================================")
    logger.info(f"🚀 Server listening on http://{host}:{port}")
    logger.info("=======================================================")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
