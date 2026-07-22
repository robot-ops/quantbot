import requests
import asyncio
import json
from typing import Optional

class TelegramService:
    def __init__(self, token: str = "", chat_id: str = ""):
        self.token = token
        self.chat_id = chat_id
        self.state = "NORMAL"  # NORMAL, AWAITING_API_KEY, AWAITING_API_SECRET
        self.temp_api_key = None
        if self.is_configured():
            self.register_commands()

    def update_credentials(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        if self.is_configured():
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.run_in_executor(None, self.register_commands)
                else:
                    self.register_commands()
            except Exception:
                # Fallback run sync jika loop belum aktif
                self.register_commands()

    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)

    def register_commands(self) -> bool:
        """Daftarkan daftar command resmi ke Telegram Menu Button"""
        if not self.is_configured():
            return False
            
        url = f"https://api.telegram.org/bot{self.token}/setMyCommands"
        payload = {
            "commands": [
                {"command": "status", "description": "Cek status bot, harga, PnL, & posisi aktif"},
                {"command": "summary", "description": "Laporan performa trading & win rate"},
                {"command": "pause", "description": "Menghentikan eksekusi trading bot"},
                {"command": "resume", "description": "Menjalankan kembali trading bot"},
                {"command": "config", "description": "Tampilkan parameter strategi & kredensial"},
                {"command": "set", "description": "Ubah setting (e.g. /set timeframe 5m)"},
                {"command": "mode", "description": "Ubah mode trading (e.g. /mode live)"},
                {"command": "help", "description": "Tampilkan bantuan & daftar perintah"}
            ]
        }
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                print("[TelegramService] Registered command menu successfully.")
                return True
            else:
                print(f"[TelegramService] Failed to register commands: {res.text}")
                return False
        except Exception as e:
            print(f"[TelegramService] Error registering commands: {e}")
            return False

    def get_default_keyboard(self) -> dict:
        return {
            "keyboard": [
                [{"text": "📊 Status"}, {"text": "📝 Laporan"}],
                [{"text": "⏸️ Pause"}, {"text": "▶️ Resume"}],
                [{"text": "⚙️ Pengaturan"}, {"text": "🔄 Ganti Mode"}]
            ],
            "resize_keyboard": True
        }

    def get_cancel_keyboard(self) -> dict:
        return {
            "keyboard": [
                [{"text": "/cancel"}]
            ],
            "resize_keyboard": True
        }

    def _delete_message(self, message_id: int):
        if not self.is_configured() or not message_id:
            return
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage"
        payload = {"chat_id": self.chat_id, "message_id": message_id}
        try:
            requests.post(url, json=payload, timeout=5)
        except Exception:
            pass

    def _mask_secret(self, val: str) -> str:
        if not val:
            return ""
        if len(val) <= 8:
            return "********"
        return f"{val[:5]}...{val[-4:]}"

    async def poll_updates(self, bot_strategy):
        """Membaca pesan masuk dari Telegram untuk remote control secara berkala"""
        self.register_commands()
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
                                
                            message_id = message.get("message_id")
                            await self._process_command(text, bot_strategy, message_id)
                            
            except Exception as e:
                # Hindari log spam jika hanya timeout jaringan biasa
                if "timeout" not in str(e).lower():
                    print(f"[TelegramService Polling Error] {e}")
                
            await asyncio.sleep(2)

    async def _process_command(self, text: str, bot_strategy, message_id: Optional[int] = None):
        text_clean = text.strip()
        cmd_mapped = text_clean
        
        # Map friendly button text to commands
        if text_clean == "📊 Status":
            cmd_mapped = "/status"
        elif text_clean == "📝 Laporan":
            cmd_mapped = "/summary"
        elif text_clean == "⏸️ Pause":
            cmd_mapped = "/pause"
        elif text_clean == "▶️ Resume":
            cmd_mapped = "/resume"
        elif text_clean == "⚙️ Pengaturan":
            cmd_mapped = "/config"
        elif text_clean == "🔄 Ganti Mode":
            cmd_mapped = "/mode"

        cmd_lower = cmd_mapped.lower()
        mode = bot_strategy.config.trading_mode

        # ----------------------------------------------------
        # STATE MACHINE FOR IN-CHAT CREDENTIAL INPUT
        # ----------------------------------------------------
        if self.state == "AWAITING_API_KEY":
            # Hapus pesan key demi keamanan
            if message_id:
                self._delete_message(message_id)

            if cmd_lower == "/cancel":
                self.state = "NORMAL"
                self.send_message("❌ Konfigurasi Live Mode dibatalkan. Kembali ke mode normal.", mode=mode)
                return
            
            self.temp_api_key = text_clean
            self.state = "AWAITING_API_SECRET"
            
            # Send message asking for secret and supply cancel keyboard
            url = f"https://api.telegram.org/bot{self.token}/sendMessage"
            payload = {
                "chat_id": self.chat_id,
                "text": "🔑 <b>API Key Diterima.</b>\n\nSekarang silakan kirimkan <b>Exchange API Secret Tokocrypto</b> Anda:\n\n⚠️ <i>Pesan ini berisi informasi sensitif. Pesan akan dihapus otomatis dari chat setelah Anda mengirimkannya demi keamanan.</i>",
                "parse_mode": "HTML",
                "reply_markup": self.get_cancel_keyboard()
            }
            try: requests.post(url, json=payload, timeout=5)
            except Exception: pass
            return

        if self.state == "AWAITING_API_SECRET":
            # Hapus pesan secret demi keamanan
            if message_id:
                self._delete_message(message_id)

            if cmd_lower == "/cancel":
                self.state = "NORMAL"
                self.temp_api_key = None
                self.send_message("❌ Konfigurasi Live Mode dibatalkan. Kembali ke mode normal.", mode=mode)
                return
            
            api_secret = text_clean
            
            # Update strategy configuration
            settings_update = {
                "exchange_api_key": self.temp_api_key,
                "exchange_api_secret": api_secret,
                "trading_mode": "live"
            }
            bot_strategy.update_config(settings_update)
            
            self.state = "NORMAL"
            self.temp_api_key = None
            self.send_message("🔴 <b>Berhasil Beralih ke LIVE TRADING MODE!</b>\n\nExchange API Key & Secret Tokocrypto berhasil dikonfigurasi dan disimpan secara persisten. Bot siap mengeksekusi order asli.", mode="live")
            return

        # ----------------------------------------------------
        # NORMAL COMMANDS HANDLING
        # ----------------------------------------------------
        if cmd_lower in ["/start", "/help"]:
            help_text = """⚡ <b>QuantBot Professional Remote Control</b>

Selamat datang di menu kendali jarak jauh QuantBot! Gunakan tombol cepat di bawah atau kirim perintah berikut:

📊 <b>Monitoring & Kontrol:</b>
• /status - Cek status bot, harga, PnL, & posisi aktif.
• /summary - Laporan performa trading & win rate.
• /pause - Menghentikan eksekusi trading bot.
• /resume - Menjalankan kembali trading bot.

⚙️ <b>Konfigurasi & Pengaturan:</b>
• /config - Tampilkan parameter strategi & kredensial.
• /set [param] [nilai] - Ubah setting secara instan.
  <i>Contoh: /set timeframe 5m</i>
  <i>Contoh: /set symbol ETH/USDT</i>
• /mode [demo/live] - Ubah mode trading (Demo/Live).

❌ <b>Umum:</b>
• /cancel - Batalkan input data kredensial.

💡 <i>Gunakan menu tombol di bawah keyboard Anda untuk akses cepat!</i>"""
            self.send_message(help_text, mode=mode)

        elif cmd_lower == "/status":
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
<b>Current Price:</b> ${stats['current_price']:,.2f} USDT
<b>Symbol:</b> {stats['symbol']} ({stats['timeframe']})

📈 <b>Kinerja Trading:</b>
• Total PnL: {pnl:+.2f} USDT ({pnl_pct:+.2f}%)
• Win Rate: {win_rate:.1f}% ({trades_count} Trades)
• Total Equity: ${stats['total_equity']:,.2f} USDT"""
            self.send_message(msg, mode=mode)
            
        elif cmd_lower == "/summary":
            stats = bot_strategy.get_full_stats()
            msg = f"""📝 <b>QuantBot Laporan Trading</b>

• Total Trades: {stats.get("total_trades", 0)}
• Winning Trades: {stats.get("winning_trades", 0)} 🟢
• Losing Trades: {stats.get("losing_trades", 0)} 🔴
• Win Rate: {stats.get('win_rate', 0.0):.1f}%
• Net Profit: ${stats.get('total_pnl', 0.0):,.2f} USDT
• Current Balance: ${stats.get('balance', 0.0):,.2f} USDT"""
            self.send_message(msg, mode=mode)
            
        elif cmd_lower == "/pause":
            bot_strategy.is_running = False
            bot_strategy.log("⏸️ Bot Trading Dihentikan via Telegram Remote")
            self.send_message("⏸️ <b>Bot Trading Dihentikan</b> via Telegram Remote Control.", mode=mode)
            
        elif cmd_lower == "/resume":
            bot_strategy.is_running = True
            bot_strategy.max_daily_drawdown_triggered = False
            bot_strategy.log("▶️ Bot Trading Dijalankan via Telegram Remote")
            self.send_message("▶️ <b>Bot Trading Dijalankan</b> via Telegram Remote Control.", mode=mode)

        elif cmd_lower == "/config":
            cfg = bot_strategy.config
            masked_token = self._mask_secret(cfg.telegram_bot_token)
            masked_chat = self._mask_secret(cfg.telegram_chat_id)
            masked_key = self._mask_secret(cfg.exchange_api_key)
            masked_secret = self._mask_secret(cfg.exchange_api_secret)
            
            config_text = f"""⚙️ <b>QuantBot Konfigurasi Saat Ini</b>

• <b>Mode:</b> {"🔴 LIVE TRADING" if cfg.trading_mode == "live" else "🟡 DEMO PAPER"}
• <b>Symbol:</b> {cfg.symbol}
• <b>Timeframe:</b> {cfg.timeframe}

🛡️ <b>Manajemen Risiko:</b>
• Stop Loss: {cfg.stop_loss_pct}%
• Take Profit: {cfg.take_profit_pct}%
• Risk Per Trade: {cfg.risk_per_trade_pct}%
• Max Daily Drawdown: {cfg.max_daily_drawdown_pct}%

📉 <b>Parameter Indikator:</b>
• EMA Fast: {cfg.ema_fast}
• EMA Slow: {cfg.ema_slow}
• RSI Period: {cfg.rsi_period} (OS: {cfg.rsi_oversold} | OB: {cfg.rsi_overbought})

🔌 <b>Integrasi & Kredensial:</b>
• Telegram Bot Token: <code>{masked_token}</code>
• Telegram Chat ID: <code>{masked_chat}</code>
• Exchange API Key: <code>{masked_key}</code>
• Exchange API Secret: <code>{masked_secret}</code>

💡 <i>Gunakan perintah /set [param] [nilai] untuk mengubah konfigurasi secara instan dari Telegram.</i>"""
            self.send_message(config_text, mode=mode)

        elif cmd_lower.startswith("/set "):
            parts = text_clean.split(maxsplit=2)
            if len(parts) < 3:
                self.send_message("⚠️ Format salah. Gunakan: <code>/set [nama_parameter] [nilai]</code>\nContoh: <code>/set timeframe 5m</code>", mode=mode)
                return
            
            param_name = parts[1].lower()
            param_value = parts[2]
            
            param_map = {
                "timeframe": "timeframe",
                "symbol": "symbol",
                "pair": "symbol",
                "stop_loss": "stop_loss_pct",
                "sl": "stop_loss_pct",
                "take_profit": "take_profit_pct",
                "tp": "take_profit_pct",
                "risk": "risk_per_trade_pct",
                "risk_per_trade": "risk_per_trade_pct",
                "max_drawdown": "max_daily_drawdown_pct",
                "drawdown": "max_daily_drawdown_pct",
                "ema_fast": "ema_fast",
                "ema_slow": "ema_slow",
                "rsi_period": "rsi_period",
                "rsi_oversold": "rsi_oversold",
                "rsi_overbought": "rsi_overbought"
            }
            
            actual_key = param_map.get(param_name)
            if not actual_key:
                self.send_message(f"❌ Parameter <code>{param_name}</code> tidak dikenali.", mode=mode)
                return
                
            try:
                current_val = getattr(bot_strategy.config, actual_key)
                if isinstance(current_val, int):
                    typed_val = int(param_value)
                elif isinstance(current_val, float):
                    typed_val = float(param_value)
                else:
                    typed_val = str(param_value)
                
                bot_strategy.update_config({actual_key: typed_val})
                self.send_message(f"✅ <b>Konfigurasi Berhasil Diperbarui!</b>\n\nParameter <code>{actual_key}</code> diubah menjadi <b>{typed_val}</b>.", mode=bot_strategy.config.trading_mode)
            except Exception as e:
                self.send_message(f"❌ Gagal memformat nilai <code>{param_value}</code> untuk parameter <code>{actual_key}</code>.\nDetail: {e}", mode=mode)

        elif cmd_lower.startswith("/mode"):
            parts = text_clean.split()
            target_mode = parts[1].lower() if len(parts) > 1 else None
            
            if not target_mode:
                self.send_message("❓ Pilih mode trading:\n\nKetik <code>/mode demo</code> untuk Paper Trading\nKetik <code>/mode live</code> untuk Live Real Trading", mode=mode)
                return
                
            if target_mode == "demo":
                bot_strategy.update_config({"trading_mode": "demo"})
                self.send_message("🟡 <b>Beralih ke DEMO PAPER TRADING MODE</b>\n\nBot berjalan dengan saldo virtual aman.", mode="demo")
            elif target_mode == "live":
                cfg = bot_strategy.config
                has_key = cfg.exchange_api_key and "..." not in cfg.exchange_api_key and "*" not in cfg.exchange_api_key
                has_secret = cfg.exchange_api_secret and "..." not in cfg.exchange_api_secret and "*" not in cfg.exchange_api_secret
                
                if has_key and has_secret:
                    bot_strategy.update_config({"trading_mode": "live"})
                    self.send_message("🔴 <b>Beralih ke LIVE REAL TRADING MODE</b>\n\nKredensial Tokocrypto terdeteksi dan bot akan mengeksekusi order riil di bursa.", mode="live")
                else:
                    self.state = "AWAITING_API_KEY"
                    url = f"https://api.telegram.org/bot{self.token}/sendMessage"
                    payload = {
                        "chat_id": self.chat_id,
                        "text": "🔑 <b>Memulai Konfigurasi Live Trading</b>\n\nKredensial exchange belum diisi atau tidak valid.\n\nSilakan kirimkan <b>Exchange API Key Tokocrypto</b> Anda:\n*(Atau ketik /cancel untuk membatalkan)*",
                        "parse_mode": "HTML",
                        "reply_markup": self.get_cancel_keyboard()
                    }
                    try: requests.post(url, json=payload, timeout=5)
                    except Exception: pass
            else:
                self.send_message("❌ Mode tidak valid. Pilih <code>demo</code> atau <code>live</code>.", mode=mode)

        elif cmd_lower == "/cancel":
            self.send_message("ℹ️ Tidak ada proses input kredensial aktif.", mode=mode)

    def send_message(self, message: str, mode: str = "demo", keyboard: bool = True) -> bool:
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
        if keyboard:
            payload["reply_markup"] = self.get_default_keyboard()
            
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
        payload = {
            "chat_id": self.chat_id, 
            "text": msg, 
            "parse_mode": "HTML",
            "reply_markup": self.get_default_keyboard()
        }
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
        payload = {
            "chat_id": self.chat_id, 
            "text": msg, 
            "parse_mode": "HTML",
            "reply_markup": self.get_default_keyboard()
        }
        try: requests.post(url, json=payload, timeout=5)
        except Exception: pass

    def send_risk_alert(self, title: str, description: str, mode: str = "demo"):
        badge = "🟡 <b>[DEMO PAPER TRADING]</b>" if mode == "demo" else "🔴 <b>[LIVE REAL TRADING]</b>"
        msg = f"""{badge}
⚠️ <b>RISK ALERT & PROTECTION</b>

<b>Event:</b> {title}
<b>Detail:</b> {description}"""

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id, 
            "text": msg, 
            "parse_mode": "HTML",
            "reply_markup": self.get_default_keyboard()
        }
        try: requests.post(url, json=payload, timeout=5)
        except Exception: pass
