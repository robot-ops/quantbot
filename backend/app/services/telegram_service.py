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
