import requests
import asyncio
from typing import Optional

class TelegramService:
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token
        self.chat_id = chat_id

    def update_credentials(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    async def poll_updates(self, bot_strategy):
        """Membaca pesan masuk dari Telegram untuk remote control secara berkala"""
        offset = 0
        while True:
            if not self.is_configured():
                await asyncio.sleep(5)
                continue
                
            try:
                url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                params = {"timeout": 10, "allowed_updates": ["message"]}
                if offset:
                    params["offset"] = offset
                
                # Gunakan executor agar requests tidak memblokir loop utama
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: requests.get(url, params=params, timeout=15)
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("ok") and data.get("result"):
                        for update in data["result"]:
                            update_id = update["update_id"]
                            offset = update_id + 1
                            
                            message = update.get("message")
                            if not message:
                                continue
                                
                            chat = message.get("chat")
                            if not chat or str(chat.get("id")) != str(self.chat_id):
                                continue
                                
                            text = message.get("text", "").strip()
                            if not text:
                                continue
                                
                            await self._process_command(text, bot_strategy)
                            
            except Exception as e:
                # Hindari log spam jika hanya timeout jaringan biasa
                if "timeout" not in str(e).lower():
                    print(f"[TelegramService Polling Error] {e}")
                
            await asyncio.sleep(2)

    async def _process_command(self, text: str, bot_strategy):
        cmd = text.lower()
        mode = bot_strategy.config.trading_mode
        
        if cmd == "/status":
            stats = bot_strategy.get_full_stats()
            running_text = "▶️ RUNNING (AKTIF)" if stats["is_running"] else "⏸️ PAUSED (BERHENTI)"
            mode_text = "🔴 LIVE REAL TRADING" if stats["trading_mode"] == "live" else "🟡 DEMO PAPER TRADING"
            
            pnl = stats.get("total_pnl", 0.0)
            pnl_pct = stats.get("total_pnl_pct", 0.0)
            win_rate = stats.get("win_rate", 0.0)
            trades_count = stats.get("total_trades", 0)
            
            msg = f"""📊 <b>QuantBot Status Terkini</b>

<b>Mode:</b> {mode_text}
<b>Engine Status:</b> {running_text}
<b>Current Price:</b> \${stats['current_price']:,.2f} USDT
<b>Symbol:</b> {stats['symbol']} ({stats['timeframe']})

📈 <b>Kinerja Trading:</b>
• Total PnL: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)
• Win Rate: {win_rate:.1f}% ({trades_count} Trades)
• Total Equity: \${stats['total_equity']:,.2f} USDT"""
            self.send_message(msg, mode=mode)
            
        elif cmd == "/summary":
            stats = bot_strategy.get_full_stats()
            msg = f"""📝 <b>QuantBot Laporan Trading</b>

• Total Trades: {stats.get("total_trades", 0)}
• Winning Trades: {stats.get("winning_trades", 0)} 🟢
• Losing Trades: {stats.get("losing_trades", 0)} 🔴
• Win Rate: {stats.get('win_rate', 0.0):.1f}%
• Net Profit: \${stats.get('total_pnl', 0.0):,.2f} USDT
• Current Balance: \${stats.get('balance', 0.0):,.2f} USDT"""
            self.send_message(msg, mode=mode)
            
        elif cmd == "/pause":
            bot_strategy.is_running = False
            bot_strategy.log("⏸️ Bot Trading Dihentikan via Telegram Remote")
            self.send_message("⏸️ <b>Bot Trading Dihentikan</b> via Telegram Remote Control.", mode=mode)
            
        elif cmd == "/resume":
            bot_strategy.is_running = True
            bot_strategy.max_daily_drawdown_triggered = False
            bot_strategy.log("▶️ Bot Trading Dijalankan via Telegram Remote")
            self.send_message("▶️ <b>Bot Trading Dijalankan</b> via Telegram Remote Control.", mode=mode)

    def send_message(self, message: str, mode: str = "demo") -> bool:
        """Kirim pesan sync ke Telegram Chat ID dengan Tag Mode (DEMO / LIVE)"""
        if not self.is_configured():
            return False
            
        badge = "🟡 <b>[DEMO MODE]</b>" if mode == "demo" else "🔴 <b>[LIVE TRADING]</b>"
        formatted_message = f"{badge}\n{message}"

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": formatted_message,
            "parse_mode": "HTML"
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            return res.status_code == 200
        except Exception as e:
            print(f"[TelegramService] Error sending message: {e}")
            return False

    def send_trade_open_alert(self, mode: str, symbol: str, side: str, price: float, amount: float, sl_price: float, tp_price: float):
        badge = "🟡 <b>[DEMO PAPER TRADING]</b>" if mode == "demo" else "🔴 <b>[LIVE REAL TRADING]</b>"
        emoji = "🟢 🚀 BUY ORDER" if side == "BUY" else "🔴 📉 SELL ORDER"
        
        msg = f"""{badge}
{emoji}

<b>Symbol:</b> {symbol}
<b>Entry Price:</b> ${price:,.2f} USDT
<b>Amount:</b> {amount:.4f}
<b>Total Cost:</b> ${(price * amount):,.2f} USDT

<b>Stop Loss (SL):</b> ${sl_price:,.2f} USDT
<b>Take Profit (TP):</b> ${tp_price:,.2f} USDT
<b>Waktu:</b> <i>Just now</i>"""
        
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": msg, "parse_mode": "HTML"}
        try: requests.post(url, json=payload, timeout=5)
        except Exception: pass

    def send_trade_close_alert(self, mode: str, symbol: str, side: str, entry_price: float, exit_price: float, pnl: float, pnl_pct: float, reason: str):
        badge = "🟡 <b>[DEMO PAPER TRADING]</b>" if mode == "demo" else "🔴 <b>[LIVE REAL TRADING]</b>"
        reason_emoji = "🎯 TAKE PROFIT" if reason == "TAKE_PROFIT" else ("🛑 STOP LOSS" if reason == "STOP_LOSS" else "✋ MANUAL CLOSE")
        pnl_emoji = "💵 PROFIT" if pnl >= 0 else "🔻 LOSS"

        msg = f"""{badge}
<b>CLOSE POSITION — {reason_emoji}</b>

<b>Symbol:</b> {symbol} ({side})
<b>Entry Price:</b> ${entry_price:,.2f} USDT
<b>Exit Price:</b> ${exit_price:,.2f} USDT
<b>Result PnL:</b> {pnl_emoji} ${pnl:,.2f} ({pnl_pct:+.2f}%)"""

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": msg, "parse_mode": "HTML"}
        try: requests.post(url, json=payload, timeout=5)
        except Exception: pass

    def send_risk_alert(self, title: str, description: str, mode: str = "demo"):
        badge = "🟡 <b>[DEMO PAPER TRADING]</b>" if mode == "demo" else "🔴 <b>[LIVE REAL TRADING]</b>"
        msg = f"""{badge}
⚠️ <b>RISK ALERT & PROTECTION</b>

<b>Event:</b> {title}
<b>Detail:</b> {description}"""

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": msg, "parse_mode": "HTML"}
        try: requests.post(url, json=payload, timeout=5)
        except Exception: pass
