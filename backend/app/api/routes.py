from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.services.strategy import TradingBotStrategy

router = APIRouter()
bot_instance = TradingBotStrategy()

@router.get("/status")
def get_status():
    return bot_instance.get_full_stats()

@router.post("/control/start")
def start_bot():
    bot_instance.is_running = True
    bot_instance.max_daily_drawdown_triggered = False
    bot_instance.log("▶️ Bot Trading Dijalankan")
    if bot_instance.telegram_service.is_configured():
        bot_instance.telegram_service.send_message("▶️ <b>Bot Trading Dijalankan</b> dari Web Dashboard.")
    return {"status": "success", "is_running": True}

@router.post("/control/stop")
def stop_bot():
    bot_instance.is_running = False
    bot_instance.log("⏸️ Bot Trading Dihentikan")
    if bot_instance.telegram_service.is_configured():
        bot_instance.telegram_service.send_message("⏸️ <b>Bot Trading Dihentikan</b> dari Web Dashboard.")
    return {"status": "success", "is_running": False}

@router.post("/settings/update")
def update_settings(settings: Dict[str, Any]):
    bot_instance.update_config(settings)
    return {"status": "success", "config": bot_instance.config.dict()}

@router.post("/control/reset-demo")
def reset_demo_balance():
    bot_instance.paper_engine.reset(10000.0)
    bot_instance.daily_starting_balance = 10000.0
    bot_instance.max_daily_drawdown_triggered = False
    bot_instance.log("🔄 Saldo Paper Trading Direset ke $10,000.00 USDT")
    return {"status": "success", "message": "Demo balance reset to $10,000"}

@router.post("/telegram/test")
def test_telegram_notification():
    if not bot_instance.telegram_service.is_configured():
        raise HTTPException(status_code=400, detail="Telegram Bot Token & Chat ID belum diisi")
    
    success = bot_instance.telegram_service.send_message("⚡ <b>Tes Koneksi Telegram Trading Bot</b>\n\nSelamat! Bot Telegram Anda berhasil terhubung dengan Web Dashboard.")
    if success:
        return {"status": "success", "message": "Pesan tes berhasil dikirim ke Telegram!"}
    else:
        raise HTTPException(status_code=500, detail="Gagal mengirim pesan. Periksa kembali Bot Token dan Chat ID Anda.")

@router.get("/chart/candles")
def get_chart_candles():
    df = bot_instance.ccxt_service.fetch_ohlcv(
        symbol=bot_instance.config.symbol,
        timeframe=bot_instance.config.timeframe,
        limit=100
    )
    df = bot_instance.ccxt_service.fetch_ohlcv(
        symbol=bot_instance.config.symbol,
        timeframe=bot_instance.config.timeframe,
        limit=100
    )
    # Convert to lightweight-charts format
    candles = []
    for _, row in df.iterrows():
        candles.append({
            "time": int(row["timestamp"] / 1000),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": float(row["volume"])
        })
    return {"status": "success", "candles": candles}
