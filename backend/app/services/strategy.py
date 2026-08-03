import os
import asyncio
import time
from datetime import datetime
import pandas as pd
from typing import Dict, Optional, List, Any
from app.core.config import config
from app.db.session import init_db, SessionLocal
from app.db.models import Trade, Order, Performance
from app.db.repositories import TradeRepository, OrderRepository, PerformanceRepository
from app.services.brokers import CCXTBroker, PaperBroker
from app.services.ema_rsi_strategy import EMARSIStrategy
from app.services.notification import TelegramNotificationService
from app.services.risk import RiskManager
from app.services.portfolio import PortfolioManager
from app.services.indicator import TechnicalIndicators
from loguru import logger

class PaperEngineCompat:
    """Compatibility layer mapping old paper_engine attributes to DB/broker actions."""
    def __init__(self, bot):
        self.bot = bot

    @property
    def active_position(self) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = TradeRepository(db)
            pos = repo.get_active_position(mode="DEMO")
            if pos:
                return {
                    "id": f"PAPER-{pos.id}",
                    "symbol": pos.symbol,
                    "side": pos.side,
                    "entry_price": pos.entry_price,
                    "amount": pos.amount,
                    "cost": pos.cost,
                    "sl_price": pos.exit_price or (pos.entry_price * 0.985),
                    "tp_price": pos.exit_price or (pos.entry_price * 1.03),
                    "opened_at": pos.opened_at.isoformat()
                }
            return None

    def reset(self, new_balance: float = 10000.0):
        with SessionLocal() as db:
            db.query(Trade).filter(Trade.mode == "DEMO").delete()
            db.query(Order).filter(Order.mode == "DEMO").delete()
            db.query(Performance).filter(Performance.mode == "DEMO").delete()
            db.commit()
        logger.info(f"Demo environment reset to virtual balance: ${new_balance:,.2f} USDT")

class TradingBotStrategy:
    """Facade orchestrator class representing the QuantBot Pro Trading Engine.
    Exposes identical public interface to original, but delegates logic internally
    to db layers, decoupled brokers, strategies, portfolio and risk managers.
    """

    def __init__(self):
        # 1. Initialize Database Tables
        init_db()

        self.last_config_mtime = 0.0

        # 2. Assign configuration
        self.config = config
        self.is_running = False

        # 3. Setup Decoupled Services
        self.strategy = EMARSIStrategy()
        self.strategy.initialize(self.config.dict())
        
        self.risk_manager = RiskManager()
        
        self.telegram_service = TelegramNotificationService(
            token=self.config.telegram_bot_token,
            chat_id=self.config.telegram_chat_id
        )

        # CCXT Service placeholder for backward compatibility
        self.ccxt_service = CCXTBroker(
            exchange_id=self.config.exchange_id,
            api_key=self.config.exchange_api_key,
            api_secret=self.config.exchange_api_secret
        )

        # Paper Engine compatibility wrapper
        self.paper_engine = PaperEngineCompat(self)
        
        # Populate initial config mtime
        self._check_and_reload_config()

        # Legacy diagnostic fields
        self.latest_df = None
        self.latest_price = 0.0
        self.log_messages: List[str] = []
        self.daily_starting_balance = 10000.0
        self.max_daily_drawdown_triggered = False
        self.last_reset_date = datetime.now().date()
        
        # Unused legacy handle, kept for schema properties compatibility
        self.live_active_position: Optional[Dict] = None

    def log(self, message: str):
        """Standard log output to console and UI list, plus Loguru file routing."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        # Add to local console list for WebSocket dashboard broadcast
        self.log_messages.insert(0, log_entry)
        if len(self.log_messages) > 100:
            self.log_messages.pop()
            
        logger.info(message)

    def _check_and_reload_config(self):
        """Checks if config.yaml was modified on disk, and if so, hot-reloads it."""
        import os
        from app.core.config import YAML_FILE, load_config
        if not os.path.exists(YAML_FILE):
            return
        try:
            mtime = os.path.getmtime(YAML_FILE)
            if mtime > self.last_config_mtime:
                self.last_config_mtime = mtime
                # Load configuration and re-initialize services
                self.config = load_config()
                self.strategy.initialize(self.config.dict())
                self.telegram_service.update_credentials(
                    self.config.telegram_bot_token,
                    self.config.telegram_chat_id
                )
                self.ccxt_service._init_exchange(
                    self.config.exchange_id,
                    self.config.exchange_api_key,
                    self.config.exchange_api_secret
                )
                logger.info("🤖 Config hot-reload triggered: updated in-memory values from config.yaml")
        except Exception as e:
            logger.error(f"Error reloading config from disk: {e}")

    def update_config(self, new_settings: Dict[str, Any]):
        """Updates Pydantic configuration model and updates sub-services."""
        for key, value in new_settings.items():
            if hasattr(self.config, key):
                if key in ["telegram_bot_token", "telegram_chat_id", "exchange_api_key", "exchange_api_secret"]:
                    if value and ("..." in str(value) or "*" in str(value)):
                        continue
                setattr(self.config, key, value)
        
        self.config.save()
        # Force immediately update last_config_mtime to prevent redundant reload
        from app.core.config import YAML_FILE
        if os.path.exists(YAML_FILE):
            self.last_config_mtime = os.path.getmtime(YAML_FILE)

        # Update Telegram credentials
        self.telegram_service.update_credentials(
            self.config.telegram_bot_token,
            self.config.telegram_chat_id
        )

        # Update ccxt broker instances
        self.ccxt_service._init_exchange(
            self.config.exchange_id,
            self.config.exchange_api_key,
            self.config.exchange_api_secret
        )
        
        # Update strategy parameters
        self.strategy.initialize(self.config.dict())

        self.log(f"Parameter diperbarui: Mode={self.config.trading_mode}, Symbol={self.config.symbol}, SL={self.config.stop_loss_pct}%, TP={self.config.take_profit_pct}%")

    def evaluate_market_tick(self) -> Dict[str, Any]:
        """Runs a single market evaluation cycle. Pulls market data, checks SL/TP thresholds,
        applies indicator rules, calculates position size, and executes entries/exits.
        """
        self._check_and_reload_config()
        start_time = time.perf_counter()
        mode = self.config.trading_mode.upper()

        # 1. Fetch Ticker & OHLCV Real-time
        try:
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
        except Exception as e:
            self.log(f"⚠️ Gagal mengambil data pasar: {e}")
            return {"status": "market_error"}

        # 2. Database transaction scope
        with SessionLocal() as db:
            trade_repo = TradeRepository(db)
            
            # Reset daily starting balance on a new calendar day
            today = datetime.now().date()
            if today != self.last_reset_date:
                self.last_reset_date = today
                if mode == "DEMO":
                    self.daily_starting_balance = 10000.0
                else:
                    self.daily_starting_balance = 0.0
                self.max_daily_drawdown_triggered = False
                logger.info(f"📆 New trading day detected ({today}). Resetting daily starting balance.")
            
            # Setup active broker instance
            if mode == "DEMO":
                if self.daily_starting_balance != 10000.0:
                    self.daily_starting_balance = 10000.0
                broker = PaperBroker(db, initial_balance=self.daily_starting_balance, ccxt_underlying=self.ccxt_service)
            else:
                if self.daily_starting_balance == 10000.0 or self.daily_starting_balance <= 0.0:
                    try:
                        broker_bal = self.ccxt_service.fetch_balance()
                        live_bal = float(broker_bal.get("USDT", {}).get("free", 0.0))
                        if live_bal > 0.0:
                            self.daily_starting_balance = live_bal
                            logger.info(f"💼 Live daily starting balance initialized to actual exchange balance: {self.daily_starting_balance:.2f} USDT")
                    except Exception as e:
                        logger.error(f"Failed to fetch live balance for starting balance initialization: {e}")
                broker = self.ccxt_service
                
            portfolio = PortfolioManager(db, broker, mode=mode, initial_balance=self.daily_starting_balance)

            # Check for active open positions
            active_pos = trade_repo.get_active_position(mode=mode)
            
            if active_pos:
                # Load current parameters and fallback values
                sl_price = active_pos.sl_price or (active_pos.entry_price * (1 - self.config.stop_loss_pct / 100.0))
                tp_price = active_pos.tp_price or (active_pos.entry_price * (1 + self.config.take_profit_pct / 100.0))
                peak_price = active_pos.peak_price or active_pos.entry_price
                partial_closed = active_pos.partial_closed or 0

                # 1. Update peak price for trailing stop calculations
                if active_pos.side == "BUY" and current_price > peak_price:
                    peak_price = current_price
                    active_pos.peak_price = peak_price
                    db.commit()
                elif active_pos.side == "SELL" and current_price < peak_price:
                    peak_price = current_price
                    active_pos.peak_price = peak_price
                    db.commit()

                # 2. Trailing Stop evaluation
                if getattr(self.config, "use_trailing_stop", False):
                    new_sl = self.risk_manager.evaluate_trailing_stop(
                        entry_price=active_pos.entry_price,
                        current_price=peak_price,
                        current_sl=sl_price,
                        side=active_pos.side,
                        trail_pct=getattr(self.config, "trail_pct", 1.0)
                    )
                    if new_sl != sl_price:
                        sl_price = new_sl
                        trade_repo.update_risk_parameters(active_pos.id, sl_price, tp_price, peak_price, partial_closed)
                        self.log(f"Trailing stop updated to ${sl_price:,.2f}")

                # 3. Break Even evaluation
                if getattr(self.config, "use_break_even", False):
                    new_sl = self.risk_manager.evaluate_break_even(
                        entry_price=active_pos.entry_price,
                        current_price=current_price,
                        current_sl=sl_price,
                        side=active_pos.side,
                        trigger_profit_pct=getattr(self.config, "break_even_pct", 1.5)
                    )
                    if new_sl != sl_price:
                        sl_price = new_sl
                        trade_repo.update_risk_parameters(active_pos.id, sl_price, tp_price, peak_price, partial_closed)
                        self.log(f"Stop loss moved to break-even @ ${sl_price:,.2f}")

                # 4. Partial Close evaluation
                if getattr(self.config, "use_partial_close", False) and partial_closed == 0:
                    should_close_partial, close_ratio = self.risk_manager.evaluate_partial_close(
                        entry_price=active_pos.entry_price,
                        current_price=current_price,
                        side=active_pos.side,
                        target_pct=getattr(self.config, "partial_close_pct", 1.5),
                        has_partially_closed=False
                    )
                    if should_close_partial:
                        close_amount = active_pos.amount * close_ratio
                        order_res = broker.execute_order(active_pos.symbol, "SELL", close_amount)
                        if order_res["status"] == "success":
                            realized_pnl = (current_price - active_pos.entry_price) * close_amount
                            realized_pnl_pct = ((current_price - active_pos.entry_price) / active_pos.entry_price) * 100.0
                            
                            # Update active position sizes
                            active_pos.amount -= close_amount
                            active_pos.cost -= active_pos.entry_price * close_amount
                            partial_closed = 1
                            trade_repo.update_risk_parameters(active_pos.id, sl_price, tp_price, peak_price, 1)
                            
                            self.log(f"Partial close executed: 50% position sold @ ${current_price:,.2f} | Realized PnL: ${realized_pnl:.2f}")
                            self.telegram_service.send_message(
                                f"💵 <b>PARTIAL CLOSE EXECUTED</b>\n\nClosed 50% of position ({close_amount:.4f} {active_pos.symbol}) @ ${current_price:,.2f} USDT.\nRealized PnL: ${realized_pnl:.2f} ({realized_pnl_pct:+.2f}%). Remaining position size: {active_pos.amount:.4f}",
                                mode=mode.lower()
                            )

                # 5. Evaluate main strategy exits (SL/TP trigger)
                pos_data = {
                    "id": active_pos.id,
                    "symbol": active_pos.symbol,
                    "side": active_pos.side,
                    "entry_price": active_pos.entry_price,
                    "amount": active_pos.amount,
                    "cost": active_pos.cost,
                    "sl_price": sl_price,
                    "tp_price": tp_price,
                }

                close_reason = self.strategy.manage_trade(pos_data, current_price, df)
                
                if close_reason:
                    # Execute sell/close order
                    order_res = broker.execute_order(active_pos.symbol, "SELL", active_pos.amount)
                    if order_res["status"] == "success":
                        # Calculate profit/loss
                        exit_price = current_price
                        pnl = (exit_price - active_pos.entry_price) * active_pos.amount
                        pnl_pct = ((exit_price - active_pos.entry_price) / active_pos.entry_price) * 100.0
                        
                        # Close position in database
                        trade_repo.close(active_pos.id, exit_price, pnl, pnl_pct, close_reason)
                        
                        # Trigger strategy closed hook
                        self.strategy.on_position_closed({
                            "id": active_pos.id,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct
                        })

                        self.log(f"🎯 POSITION CLOSED [{close_reason}] @ ${exit_price:,.2f} | PnL: ${pnl:.2f} ({pnl_pct:+.2f}%)")
                        self.telegram_service.send_trade_close_alert(
                            mode=mode.lower(),
                            symbol=active_pos.symbol,
                            side=active_pos.side,
                            entry_price=active_pos.entry_price,
                            exit_price=exit_price,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            reason=close_reason
                        )
                    else:
                        error_msg = order_res.get("message", "Gagal mengeksekusi order jual dari exchange")
                        self.log(f"⚠️ GAGAL CLOSE ORDER [{mode}] @ ${current_price:,.2f} | Alasan: {error_msg}")
                        self.telegram_service.send_trade_failure_alert(
                            mode=mode.lower(),
                            symbol=active_pos.symbol,
                            side="SELL",
                            price=current_price,
                            amount=active_pos.amount,
                            reason=error_msg
                        )

            # 3. Check Risk Drawdown Limits
            stats = portfolio.get_stats(current_price)
            active_cost = active_pos.cost if active_pos else 0.0
            equity = stats["balance"] + active_cost + stats["unrealized_pnl"]
            
            drawdown_breached, dd_pct = self.risk_manager.check_daily_drawdown(
                self.daily_starting_balance,
                equity,
                self.config.max_daily_drawdown_pct
            )
            
            if drawdown_breached:
                if not self.max_daily_drawdown_triggered:
                    self.max_daily_drawdown_triggered = True
                    msg = f"Rugi harian telah mencapai {dd_pct:.2f}% (Batas: {self.config.max_daily_drawdown_pct}%). Bot dihentikan demi keamanan modal."
                    self.log(f"⚠️ CIRCUIT BREAKER: {msg}")
                    self.telegram_service.send_risk_alert("Max Daily Drawdown Reached", msg, mode=mode.lower())
                    self.is_running = False
                return {"status": "paused_by_drawdown", "price": current_price}

            # 4. Generate Signal if no active positions
            if self.is_running and not active_pos:
                raw_sig = self.strategy.generate_signal(df)
                if raw_sig == "BUY" and self.strategy.confirm_signal(df, raw_sig):
                    # Calculate dynamic sizing
                    amount = self.risk_manager.calculate_position_size(
                        current_price=current_price,
                        balance=stats["balance"],
                        risk_per_trade_pct=self.config.risk_per_trade_pct,
                        stop_loss_pct=self.config.stop_loss_pct
                    )
                    
                    if amount > 0:
                        order_res = broker.execute_order(self.config.symbol, "BUY", amount)
                        if order_res["status"] == "success":
                            sl_price = self.strategy.calculate_stop_loss(current_price, "BUY", df)
                            tp_price = self.strategy.calculate_take_profit(current_price, "BUY", df)
                            
                            # Save opened trade to DB
                            trade_repo.create(
                                symbol=self.config.symbol,
                                side="BUY",
                                entry_price=current_price,
                                amount=amount,
                                cost=current_price * amount,
                                mode=mode,
                                sl_price=sl_price,
                                tp_price=tp_price
                            )
                            
                            self.log(f"🚀 BUY SIGNAL EXECUTED [{mode}] @ ${current_price:,.2f} | Amount: {amount}")
                            self.telegram_service.send_trade_open_alert(
                                mode=mode.lower(),
                                symbol=self.config.symbol,
                                side="BUY",
                                price=current_price,
                                amount=amount,
                                sl_price=sl_price,
                                tp_price=tp_price
                            )
                        else:
                            error_msg = order_res.get("message", "Gagal mengeksekusi order dari exchange")
                            self.log(f"⚠️ GAGAL BUY ORDER [{mode}] @ ${current_price:,.2f} | Alasan: {error_msg}")
                            self.telegram_service.send_trade_failure_alert(
                                mode=mode.lower(),
                                symbol=self.config.symbol,
                                side="BUY",
                                price=current_price,
                                amount=amount,
                                reason=error_msg
                            )
                    else:
                        error_msg = f"Perhitungan jumlah order bernilai 0. Saldo USDT saat ini: ${stats['balance']:.2f} USDT"
                        self.log(f"⚠️ GAGAL BUY ORDER [{mode}] | {error_msg}")
                        self.telegram_service.send_trade_failure_alert(
                            mode=mode.lower(),
                            symbol=self.config.symbol,
                            side="BUY",
                            price=current_price,
                            amount=0.0,
                            reason=error_msg
                        )

            # Record performance logs every tick
            portfolio.record_performance_snapshot(current_price)

        # Log computation latency
        elapsed = (time.perf_counter() - start_time) * 1000.0
        logger.bind(type="performance").info(f"Market tick evaluation completed in {elapsed:.2f}ms")

        # Technical values for UI candlestick markers
        last_row = df.iloc[-1]
        ema_fast = float(last_row["ema_fast"]) if not pd.isna(last_row["ema_fast"]) else current_price
        ema_slow = float(last_row["ema_slow"]) if not pd.isna(last_row["ema_slow"]) else current_price
        rsi = float(last_row["rsi"]) if not pd.isna(last_row["rsi"]) else 50.0

        return {
            "status": "ok",
            "price": current_price,
            "ema_fast": round(ema_fast, 2),
            "ema_slow": round(ema_slow, 2),
            "rsi": round(rsi, 2)
        }

    def _mask_secret(self, val: str) -> str:
        if not val:
            return ""
        if len(val) <= 8:
            return "********"
        return f"{val[:5]}...{val[-4:]}"

    def get_full_stats(self) -> Dict[str, Any]:
        """Provides full statistics summary to UI WebSocket client."""
        self._check_and_reload_config()
        mode = self.config.trading_mode.upper()
        
        with SessionLocal() as db:
            if mode == "DEMO":
                broker = PaperBroker(db, initial_balance=self.daily_starting_balance, ccxt_underlying=self.ccxt_service)
            else:
                broker = self.ccxt_service
                
            portfolio = PortfolioManager(db, broker, mode=mode, initial_balance=self.daily_starting_balance)
            
            stats = portfolio.get_stats(self.latest_price)
            trade_repo = TradeRepository(db)
            active_pos = trade_repo.get_active_position(mode=mode)
            active_cost = active_pos.cost if active_pos else 0.0
            total_equity = stats["balance"] + active_cost + stats["unrealized_pnl"]
            all_trades = [t for t in trade_repo.get_all(mode=mode, limit=50) if t.closed_at is not None]
            
            # Map DB trades to UI JSON format
            trade_history_mapped = []
            for t in all_trades:
                trade_history_mapped.append({
                    "id": f"PAPER-{t.id}" if mode == "DEMO" else f"LIVE-{t.id}",
                    "symbol": t.symbol,
                    "side": t.side,
                    "entry_price": t.entry_price or 0.0,
                    "exit_price": t.exit_price or 0.0,
                    "amount": t.amount or 0.0,
                    "cost": t.cost or 0.0,
                    "pnl": t.pnl or 0.0,
                    "pnl_pct": t.pnl_pct or 0.0,
                    "opened_at": t.opened_at.isoformat() if t.opened_at else None,
                    "closed_at": t.closed_at.isoformat() if t.closed_at else None,
                    "close_reason": t.close_reason,
                    "mode": t.mode
                })

        safe_config = self.config.dict()
        safe_config["telegram_bot_token"] = self._mask_secret(safe_config.get("telegram_bot_token", ""))
        safe_config["telegram_chat_id"] = self._mask_secret(safe_config.get("telegram_chat_id", ""))
        safe_config["exchange_api_key"] = self._mask_secret(safe_config.get("exchange_api_key", ""))
        safe_config["exchange_api_secret"] = self._mask_secret(safe_config.get("exchange_api_secret", ""))

        return {
            "balance": stats["balance"],
            "initial_balance": stats["initial_balance"],
            "total_pnl": stats["total_pnl"],
            "total_pnl_pct": stats["total_pnl_pct"],
            "unrealized_pnl": stats["unrealized_pnl"],
            "unrealized_pnl_pct": stats["unrealized_pnl_pct"],
            "win_rate": stats["win_rate"],
            "total_trades": stats["total_trades"],
            "winning_trades": stats["winning_trades"],
            "losing_trades": stats["losing_trades"],
            "active_position": stats["active_position"],
            "total_equity": round(total_equity, 2),
            "is_running": self.is_running,
            "trading_mode": self.config.trading_mode,
            "symbol": self.config.symbol,
            "timeframe": self.config.timeframe,
            "current_price": round(self.latest_price, 2),
            "config": safe_config,
            "trade_history": trade_history_mapped,
            "logs": self.log_messages[:30],
            "telegram_configured": self.telegram_service.is_configured()
        }
