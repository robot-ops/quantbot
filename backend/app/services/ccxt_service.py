import ccxt
import pandas as pd
import random
import time
from typing import List, Dict, Tuple

class CCXTService:
    def __init__(self, exchange_id: str = "binance", api_key: str = "", api_secret: str = ""):
        self.exchange_id = exchange_id
        self.exchange = None
        self._init_exchange(exchange_id, api_key, api_secret)
        self._mock_last_price = 65000.0

    def _init_exchange(self, exchange_id: str, api_key: str = "", api_secret: str = ""):
        try:
            exchange_class = getattr(ccxt, exchange_id.lower(), ccxt.binance)
            config = {
                "enableRateLimit": True,
                "timeout": 10000,
            }
            if api_key and api_secret:
                config["apiKey"] = api_key
                config["secret"] = api_secret
            self.exchange = exchange_class(config)
        except Exception as e:
            print(f"[CCXTService] Error initializing exchange {exchange_id}: {e}")
            self.exchange = ccxt.binance({"enableRateLimit": True})

    def fetch_ticker(self, symbol: str = "BTC/USDT") -> float:
        """Ambil harga terkini"""
        try:
            if self.exchange and hasattr(self.exchange, "fetch_ticker"):
                ticker = self.exchange.fetch_ticker(symbol)
                price = float(ticker["last"])
                self._mock_last_price = price
                return price
        except Exception as e:
            pass
        
        # Fallback simulator pergerakan harga acak jika jaringan bermasalah
        change = random.uniform(-0.15, 0.15) / 100.0
        self._mock_last_price *= (1 + change)
        return round(self._mock_last_price, 2)

    def fetch_ohlcv(self, symbol: str = "BTC/USDT", timeframe: str = "1m", limit: int = 50) -> pd.DataFrame:
        """Ambil data Candlestick (OHLCV)"""
        try:
            if self.exchange and hasattr(self.exchange, "fetch_ohlcv"):
                ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
                df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df["time"] = pd.to_datetime(df["timestamp"], unit="ms")
                return df
        except Exception as e:
            pass

        # Fallback data OHLCV sintetis untuk offline mode/testing
        now_ts = int(time.time() * 1000)
        candles = []
        base_price = self._mock_last_price
        for i in range(limit, 0, -1):
            ts = now_ts - (i * 60 * 1000)
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

    def execute_live_order(self, symbol: str, side: str, amount: float, price: float = None) -> Dict:
        """Eksekusi order di bursa riil via API key"""
        if not self.exchange or not self.exchange.apiKey:
            return {"status": "error", "message": "Live Trading API Key & Secret belum dikonfigurasi"}
        
        try:
            order_type = "market" if price is None else "limit"
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side.lower(),
                amount=amount,
                price=price
            )
            return {"status": "success", "order": order}
        except Exception as e:
            return {"status": "error", "message": str(e)}
