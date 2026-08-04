import ccxt
import random
import time
import pandas as pd
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.services.interfaces import BaseBroker
from app.db.repositories import TradeRepository, OrderRepository
from loguru import logger

class CCXTBroker(BaseBroker):
    def __init__(self, exchange_id: str = "binance", api_key: str = "", api_secret: str = ""):
        self.exchange_id = exchange_id.lower()
        self.exchange = None
        self._init_exchange(self.exchange_id, api_key, api_secret)
        self._mock_last_price = 65000.0

    def _init_exchange(self, exchange_id: str, api_key: str = "", api_secret: str = ""):
        try:
            exchange_class = getattr(ccxt, exchange_id, ccxt.binance)
            config = {
                "enableRateLimit": True,
                "timeout": 15000,
                "options": {
                    "adjustForTimeDifference": True,
                    "recvWindow": 10000,
                }
            }
            if api_key and api_secret:
                config["apiKey"] = api_key
                config["secret"] = api_secret
            self.exchange = exchange_class(config)
            if api_key and api_secret:
                try:
                    self.exchange.load_markets()
                except Exception as lm_err:
                    logger.warning(f"Could not load markets for {exchange_id} during init: {lm_err}")
            logger.info(f"CCXT Exchange {exchange_id.upper()} initialized.")
        except Exception as e:
            logger.error(f"Error initializing exchange {exchange_id}: {e}")
            self.exchange = ccxt.binance({"enableRateLimit": True})

    def fetch_ticker(self, symbol: str) -> float:
        try:
            if self.exchange and hasattr(self.exchange, "fetch_ticker"):
                ticker = self.exchange.fetch_ticker(symbol)
                price = float(ticker["last"])
                self._mock_last_price = price
                return price
        except Exception as e:
            logger.warning(f"Failed to fetch ticker for {symbol} via CCXT: {e}. Using synthetic fallback.")
            
        # Fallback simulator pergerakan harga acak jika jaringan bermasalah
        change = random.uniform(-0.15, 0.15) / 100.0
        self._mock_last_price *= (1 + change)
        return round(self._mock_last_price, 2)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> pd.DataFrame:
        try:
            if self.exchange and hasattr(self.exchange, "fetch_ohlcv"):
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
        except Exception as e:
            logger.warning(f"Failed to fetch OHLCV for {symbol} via CCXT: {e}. Using synthetic fallback.")

        # Fallback data OHLCV sintetis jika offline/testing
        now_ts = int(time.time() * 1000)
        tf_ms = 60 * 1000
        try:
            if timeframe.endswith("m"):
                tf_ms = int(timeframe[:-1]) * 60 * 1000
            elif timeframe.endswith("h"):
                tf_ms = int(timeframe[:-1]) * 60 * 60 * 1000
            elif timeframe.endswith("d"):
                tf_ms = int(timeframe[:-1]) * 24 * 60 * 60 * 1000
        except Exception:
            pass

        candles = []
        base_price = self._mock_last_price
        for i in range(limit, 0, -1):
            ts = now_ts - (i * tf_ms)
            high = base_price * (1 + random.uniform(0.0005, 0.002))
            low = base_price * (1 - random.uniform(0.0005, 0.002))
            close = random.uniform(low, high)
            open_p = random.uniform(low, high)
            volume = random.uniform(1.0, 15.0)
            candles.append([ts, open_p, high, low, close, volume])
            base_price = close

        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df

    def execute_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        if not self.exchange or not self.exchange.apiKey or not self.exchange.secret:
            return {"status": "error", "message": "Live Trading API Key & Secret belum dikonfigurasi"}
        
        try:
            if hasattr(self.exchange, "markets") and not self.exchange.markets:
                try:
                    self.exchange.load_markets()
                except Exception as lm_err:
                    logger.warning(f"Warning loading markets before order: {lm_err}")

            formatted_amount = amount
            if hasattr(self.exchange, "amount_to_precision"):
                try:
                    formatted_amount = float(self.exchange.amount_to_precision(symbol, amount))
                except Exception as prec_err:
                    logger.warning(f"Could not apply amount_to_precision: {prec_err}")

            if formatted_amount <= 0:
                return {"status": "error", "message": f"Jumlah order ({amount}) setelah presisi exchange bernilai 0"}

            order_type = "market" if price is None else "limit"
            exec_price = price
            if order_type == "market" and side.lower() == "buy":
                exec_price = self.fetch_ticker(symbol)

            if exec_price and hasattr(self.exchange, "price_to_precision"):
                try:
                    exec_price = float(self.exchange.price_to_precision(symbol, exec_price))
                except Exception:
                    pass

            target_price = exec_price if (order_type == "limit" or (order_type == "market" and side.lower() == "buy")) else None

            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side.lower(),
                amount=formatted_amount,
                price=target_price
            )
            logger.bind(type="trade").info(f"Executed live order on {self.exchange_id}: {side.upper()} {formatted_amount} {symbol}")
            return {"status": "success", "order": order}
        except Exception as e:
            logger.error(f"CCXT execution failed: {e}")
            return {"status": "error", "message": str(e)}

    def fetch_balance(self) -> Dict[str, Any]:
        if not self.exchange or not self.exchange.apiKey:
            return {"USDT": {"free": 1000.0, "used": 0.0, "total": 1000.0}}
        try:
            bal = self.exchange.fetch_balance()
            return bal
        except Exception as e:
            logger.error(f"Failed to fetch balance from exchange: {e}")
            return {"USDT": {"free": 0.0, "used": 0.0, "total": 0.0}}


class PaperBroker(BaseBroker):
    """A virtual broker that simulates order executions and holds virtual balances in SQLite/PostgreSQL."""
    def __init__(self, db: Session, initial_balance: float = 10000.0, fee_pct: float = 0.1, ccxt_underlying: Optional[BaseBroker] = None):
        self.db = db
        self.trade_repo = TradeRepository(db)
        self.order_repo = OrderRepository(db)
        self.fee_pct = fee_pct
        self.initial_balance = initial_balance
        self.ccxt_underlying = ccxt_underlying or CCXTBroker(exchange_id="binance")
        self._load_or_init_balance()

    def _load_or_init_balance(self):
        # We start with initial_balance, but look at performance database or past trades
        # For simplicity, virtual balance is simulated in memory/database
        # Let's check total closed trade revenue to build current balance
        trades = self.trade_repo.get_all(mode="DEMO", limit=1000)
        net_pnl = sum(t.pnl for t in trades if t.pnl is not None)
        active_pos = self.trade_repo.get_active_position(mode="DEMO")
        active_cost = active_pos.cost if active_pos else 0.0
        
        # Calculate current cash balance
        self.balance = self.initial_balance + net_pnl - active_cost

    def fetch_ticker(self, symbol: str) -> float:
        return self.ccxt_underlying.fetch_ticker(symbol)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 50) -> pd.DataFrame:
        return self.ccxt_underlying.fetch_ohlcv(symbol, timeframe, limit)

    def execute_order(self, symbol: str, side: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Simulate order execution instantly."""
        exec_price = price if price is not None else self.fetch_ticker(symbol)
        cost = exec_price * amount
        fee = cost * (self.fee_pct / 100.0)
        total_cost = cost + fee

        if side.upper() == "BUY":
            if total_cost > self.balance:
                return {"status": "error", "message": f"Insufficient virtual balance ({self.balance:.2f} USDT)"}
            
            # Update virtual balance (deduct cost)
            self.balance -= total_cost
            
            # Save order to DB
            db_order = self.order_repo.create(
                symbol=symbol,
                side="BUY",
                amount=amount,
                price=exec_price,
                status="closed",
                mode="DEMO"
            )
            logger.bind(type="trade").info(f"Executed virtual BUY order for {amount} {symbol} @ ${exec_price:,.2f} USDT")
            return {
                "status": "success",
                "order": {
                    "id": f"PAPER-ORD-{db_order.id}",
                    "symbol": symbol,
                    "side": "buy",
                    "price": exec_price,
                    "amount": amount,
                    "cost": cost,
                    "fee": fee
                }
            }
        
        else: # SELL order
            # Sell execution logic is triggered when active position is closed
            # Revenue calculation
            revenue = cost - fee
            self.balance += revenue

            db_order = self.order_repo.create(
                symbol=symbol,
                side="SELL",
                amount=amount,
                price=exec_price,
                status="closed",
                mode="DEMO"
            )
            logger.bind(type="trade").info(f"Executed virtual SELL order for {amount} {symbol} @ ${exec_price:,.2f} USDT")
            return {
                "status": "success",
                "order": {
                    "id": f"PAPER-ORD-{db_order.id}",
                    "symbol": symbol,
                    "side": "sell",
                    "price": exec_price,
                    "amount": amount,
                    "cost": cost,
                    "fee": fee
                }
            }

    def fetch_balance(self) -> Dict[str, Any]:
        return {
            "USDT": {
                "free": self.balance,
                "used": 0.0,
                "total": self.balance
            }
        }
