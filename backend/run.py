import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    print("\n=======================================================")
    print("🤖 QUANTBOT PRO — STARTUP DIAGNOSTIC HEALTH CHECK")
    print("=======================================================")
    
    # 1. Check .env file
    env_exists = os.path.exists(".env")
    print(f"[{'✅' if env_exists else '⚠️'}] Environment (.env): {'Loaded successfully' if env_exists else 'File .env not found, using defaults'}")
    
    # 2. Check Telegram Credentials
    token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    telegram_ready = bool(token and chat_id)
    print(f"[{'✅' if telegram_ready else '⚠️'}] Telegram Bot API: {'Configured (@prinxx_trade_bot)' if telegram_ready else 'Not configured'}")
    
    # 3. Check Live Exchange API Key
    ex_id = os.getenv("EXCHANGE_ID", "tokocrypto")
    api_key = os.getenv("EXCHANGE_API_KEY", "")
    ex_ready = bool(api_key)
    print(f"[{'✅' if ex_ready else 'ℹ️'}] Live Exchange ({ex_id.upper()}): {'API Key & Secret Ready' if ex_ready else 'Demo Mode active'}")
    
    print("=======================================================")
    print(f"🚀 Server listening on http://{host}:{port}")
    print("=======================================================\n")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
