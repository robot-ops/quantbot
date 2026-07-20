import asyncio
import time
import pandas as pd
from typing import Dict, Optional, List
from app.core.config import config
from app.services.indicator import TechnicalIndicators
from app.services.paper_trading import PaperTradingEngine
from app.services.ccxt_service import CCXTService
from app.services.telegram_service import TelegramService

class TradingBotStrategy:
    def __init__(self):
        self.config = config
        self.is_running = False
        self.paper_engine = PaperTradingEngine(initial_balance=10000.0)
        self.ccxt_service = CCXTService(
            exchange_id=config.exchange_id,
            api_key=config.exchange_api_key,
            api_secret=config.exchange_api_secret
        )
        self.telegram_service = TelegramService(
            token=config.telegram_bot_token,
            chat_id=config.telegram_chat_id
        )
        self.latest_df = None
        self.latest_price = 0.0
        self.log_messages: List[str] = []
        self.daily_starting_balance = 10000.0
        self.max_daily_drawdown_triggered = False
        self.live_active_position: Optional[Dict] = None

    def log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        self.log_messages.insert(0, log_entry)
        if len(self.log_messages) > 100:
            self.log_messages.pop()

    def update_config(self, new_settings: Dict):
        for key, value in new_settings.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        
        # Update sub-services
        self.telegram_service.update_credentials(
            self.config.telegram_bot_token,
            self.config.telegram_chat_id
        )
        self.ccxt_service._init_exchange(
            self.config.exchange_id,
            self.config.exchange_api_key,
            self.config.exchange_api_secret
        )
        self.log(f"Parameter diperbarui: Mode={self.config.trading_mode}, Symbol={self.config.symbol}, SL={self.config.stop_loss_pct}%, TP={self.config.take_profit_pct}%")

    def calculate_position_size(self, current_price: float, balance: float) -> float:
        """Kalkulasi ukuran posisi proporsional berdasarkan Risk Per Trade %"""
        risk_pct = self.config.risk_per_trade_pct / 100.0
        sl_pct = self.config.stop_loss_pct / 100.0
        
        capital_to_risk = balance * risk_pct
        position_value = capital_to_risk / sl_pct if sl_pct > 0 else balance * 0.1
        
        # Alokasikan maksimal 25% dari saldo per transaksi (bukan 90%)
        max_cost = balance * 0.25
        actual_cost = min(position_value, max_cost)
        
        amount = actual_cost / current_price
        return round(amount, 4)

    def get_total_equity(self) -> float:
        """Kalkulasi Total Equity"""
        if self.config.trading_mode == "demo":
            paper_stats = self.paper_engine.get_stats(self.latest_price)
            cash = paper_stats["balance"]
            active_pos = paper_stats.get("active_position")
            cost = active_pos["cost"] if active_pos else 0.0
            unrealized = paper_stats.get("unrealized_pnl", 0.0)
            return cash + cost + unrealized
        else:
            # Mode Live
            try:
                if self.ccxt_service.exchange and self.ccxt_service.exchange.apiKey:
                    bal = self.ccxt_service.exchange.fetch_balance()
                    usdt = float(bal.get('USDT', {}).get('free', 1000.0))
                    return usdt
            except Exception:
                pass
            return 1000.0

    def check_daily_drawdown(self, total_equity: float) -> bool:
        """Periksa apakah total kerugian equity harian melebihi batas Max Daily Drawdown"""
        if self.daily_starting_balance <= 0:
            return False
        
        drawdown_pct = ((self.daily_starting_balance - total_equity) / self.daily_starting_balance) * 100.0
        if drawdown_pct >= self.config.max_daily_drawdown_pct:
            if not self.max_daily_drawdown_triggered:
                self.max_daily_drawdown_triggered = True
                msg = f"Rugi harian telah mencapai {drawdown_pct:.2f}% (Batas: {self.config.max_daily_drawdown_pct}%). Bot dihentikan secara otomatis demi keamanan modal."
                self.log(f"⚠️ CIRCUIT BREAKER: {msg}")
                self.telegram_service.send_risk_alert("Max Daily Drawdown Reached", msg, mode=self.config.trading_mode)
                self.is_running = False
            return True
        return False

    def evaluate_market_tick(self) -> Dict:
        """Satu siklus evaluasi harga & indikator"""
        # 1. Fetch Price & OHLCV Real-time
        df = self.ccxt_service.fetch_ohlcv(symbol=self.config.symbol, timeframe=self.config.timeframe, limit=50)
        df = TechnicalIndicators.apply_all(
            df,
            ema_fast=self.config.ema_fast,
            ema_slow=self.config.ema_slow,
            rsi_period=self.config.rsi_period
        )
        self.latest_df = df
        
        current_price = self.ccxt_service.fetch_ticker(symbol=self.config.symbol)
        self.latest_price = current_price

        # 2. Check Active Position SL/TP
        if self.config.trading_mode == "demo":
            closed_event = self.paper_engine.update_and_check_sl_tp(current_price)
            if closed_event and closed_event.get("status") == "success":
                trade = closed_event["closed_trade"]
                self.log(f"🎯 POSITION CLOSED [{trade['close_reason']}]: PnL ${trade['pnl']:.2f} ({trade['pnl_pct']:+.2f}%)")
                self.telegram_service.send_trade_close_alert(
                    mode="demo",
                    symbol=trade["symbol"],
                    side=trade["side"],
                    entry_price=trade["entry_price"],
                    exit_price=trade["exit_price"],
                    pnl=trade["pnl"],
                    pnl_pct=trade["pnl_pct"],
                    reason=trade["close_reason"]
                )
        else:
            # Mode Live SL/TP check
            if self.live_active_position:
                pos = self.live_active_position
                close_reason = None
                if pos["side"] == "BUY":
                    if current_price <= pos["sl_price"]:
                        close_reason = "STOP_LOSS"
                    elif current_price >= pos["tp_price"]:
                        close_reason = "TAKE_PROFIT"
                
                if close_reason:
                    # Eksekusi sell live order di Tokocrypto / Exchange
                    order_res = self.ccxt_service.execute_live_order(pos["symbol"], "SELL", pos["amount"])
                    if order_res["status"] == "success":
                        pnl = (current_price - pos["entry_price"]) * pos["amount"]
                        pnl_pct = ((current_price - pos["entry_price"]) / pos["entry_price"]) * 100.0
                        self.log(f"🔴 LIVE POSITION CLOSED [{close_reason}]: PnL ${pnl:.2f} ({pnl_pct:+.2f}%)")
                        self.telegram_service.send_trade_close_alert(
                            mode="live",
                            symbol=pos["symbol"],
                            side=pos["side"],
                            entry_price=pos["entry_price"],
                            exit_price=current_price,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            reason=close_reason
                        )
                        self.live_active_position = None

        # 3. Check Risk Limits on Total Equity
        equity = self.get_total_equity()
        if self.check_daily_drawdown(equity):
            return {"status": "paused_by_drawdown", "price": current_price}

        # 4. Generate Signal if no position active
        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        ema_fast = float(last_row["ema_fast"]) if not pd.isna(last_row["ema_fast"]) else current_price
        ema_slow = float(last_row["ema_slow"]) if not pd.isna(last_row["ema_slow"]) else current_price
        rsi = float(last_row["rsi"]) if not pd.isna(last_row["rsi"]) else 50.0

        prev_ema_fast = float(prev_row["ema_fast"]) if not pd.isna(prev_row["ema_fast"]) else current_price
        prev_ema_slow = float(prev_row["ema_slow"]) if not pd.isna(prev_row["ema_slow"]) else current_price

        # Signal Logic: Golden Cross (Bullish) or Death Cross (Bearish) + RSI Confirmation
        is_golden_cross = (prev_ema_fast <= prev_ema_slow) and (ema_fast > ema_slow)
        
        active_pos = self.paper_engine.active_position if self.config.trading_mode == "demo" else self.live_active_position

        if self.is_running and not active_pos:
            # Bullish Entry Condition
            if (is_golden_cross or rsi <= self.config.rsi_oversold) and rsi < self.config.rsi_overbought:
                amount = self.calculate_position_size(current_price, equity)
                if amount > 0:
                    if self.config.trading_mode == "demo":
                        res = self.paper_engine.open_position(
                            symbol=self.config.symbol,
                            side="BUY",
                            price=current_price,
                            amount=amount,
                            sl_pct=self.config.stop_loss_pct,
                            tp_pct=self.config.take_profit_pct
                        )
                        if res["status"] == "success":
                            pos = res["position"]
                            self.log(f"🚀 BUY SIGNAL EXECUTED [DEMO] @ ${current_price:,.2f} | Amount: {amount}")
                            self.telegram_service.send_trade_open_alert(
                                mode="demo",
                                symbol=pos["symbol"],
                                side="BUY",
                                price=pos["entry_price"],
                                amount=pos["amount"],
                                sl_price=pos["sl_price"],
                                tp_price=pos["tp_price"]
                            )
                    else:
                        # Mode Live Trading Eksekusi ke Tokocrypto / Bursa
                        order_res = self.ccxt_service.execute_live_order(self.config.symbol, "BUY", amount)
                        if order_res["status"] == "success":
                            sl_price = current_price * (1 - self.config.stop_loss_pct / 100.0)
                            tp_price = current_price * (1 + self.config.take_profit_pct / 100.0)
                            self.live_active_position = {
                                "symbol": self.config.symbol,
                                "side": "BUY",
                                "entry_price": current_price,
                                "amount": amount,
                                "sl_price": sl_price,
                                "tp_price": tp_price,
                                "opened_at": time.strftime("%H:%M:%S")
                            }
                            self.log(f"🔴 LIVE BUY ORDER EXECUTED @ ${current_price:,.2f} | Amount: {amount}")
                            self.telegram_service.send_trade_open_alert(
                                mode="live",
                                symbol=self.config.symbol,
                                side="BUY",
                                price=current_price,
                                amount=amount,
                                sl_price=sl_price,
                                tp_price=tp_price
                            )

        return {
            "status": "ok",
            "price": current_price,
            "ema_fast": round(ema_fast, 2),
            "ema_slow": round(ema_slow, 2),
            "rsi": round(rsi, 2)
        }

    def get_full_stats(self) -> Dict:
        paper_stats = self.paper_engine.get_stats(self.latest_price)
        total_equity = self.get_total_equity()
        active_pos = self.paper_engine.active_position if self.config.trading_mode == "demo" else self.live_active_position
        return {
            **paper_stats,
            "active_position": active_pos,
            "total_equity": round(total_equity, 2),
            "is_running": self.is_running,
            "trading_mode": self.config.trading_mode,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
            "current_price": round(self.latest_price, 2),
            "config": self.config.dict(),
            "trade_history": self.paper_engine.trade_history,
            "logs": self.log_messages[:30],
            "telegram_configured": self.telegram_service.is_configured()
        }
