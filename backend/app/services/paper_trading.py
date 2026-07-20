import os
import json
from datetime import datetime
from typing import List, Dict, Optional

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "paper_trading_state.json")

class PaperTradingEngine:
    def __init__(self, initial_balance: float = 10000.0, fee_pct: float = 0.1):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.fee_pct = fee_pct  # 0.1% spot fee
        self.active_position: Optional[Dict] = None
        self.trade_history: List[Dict] = []
        self.trade_counter = 0
        self._load_state()

    def _load_state(self):
        """Memuat state saldo & riwayat dari file JSON lokal jika ada"""
        try:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.initial_balance = data.get("initial_balance", 10000.0)
                    self.balance = data.get("balance", 10000.0)
                    self.active_position = data.get("active_position")
                    self.trade_history = data.get("trade_history", [])
                    self.trade_counter = data.get("trade_counter", 0)
                print(f"[PaperTradingEngine] Restored paper trading state: Balance=${self.balance:,.2f}, Trades={len(self.trade_history)}")
        except Exception as e:
            print(f"[PaperTradingEngine] Error loading state: {e}")

    def _save_state(self):
        """Menyimpan state saldo & riwayat ke file JSON lokal agar persisten"""
        try:
            data = {
                "initial_balance": self.initial_balance,
                "balance": self.balance,
                "active_position": self.active_position,
                "trade_history": self.trade_history,
                "trade_counter": self.trade_counter,
                "last_updated": datetime.now().isoformat()
            }
            with open(STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[PaperTradingEngine] Error saving state: {e}")

    def reset(self, new_balance: float = 10000.0):
        self.initial_balance = new_balance
        self.balance = new_balance
        self.active_position = None
        self.trade_history = []
        self.trade_counter = 0
        self._save_state()

    def open_position(self, symbol: str, side: str, price: float, amount: float, sl_pct: float, tp_pct: float) -> Dict:
        if self.active_position is not None:
            return {"status": "error", "message": "Position already open"}

        cost = price * amount
        fee = cost * (self.fee_pct / 100.0)
        total_cost = cost + fee

        if total_cost > self.balance:
            return {"status": "error", "message": f"Insufficient balance ({self.balance:.2f} USDT)"}

        self.balance -= total_cost
        sl_price = price * (1 - sl_pct / 100.0) if side == "BUY" else price * (1 + sl_pct / 100.0)
        tp_price = price * (1 + tp_pct / 100.0) if side == "BUY" else price * (1 - tp_pct / 100.0)

        self.trade_counter += 1
        self.active_position = {
            "id": f"PAPER-{self.trade_counter}",
            "symbol": symbol,
            "side": side,
            "entry_price": price,
            "amount": amount,
            "cost": cost,
            "fee": fee,
            "sl_price": sl_price,
            "tp_price": tp_price,
            "sl_pct": sl_pct,
            "tp_pct": tp_pct,
            "opened_at": datetime.now().isoformat(),
            "mode": "DEMO"
        }
        self._save_state()
        return {"status": "success", "position": self.active_position}

    def update_and_check_sl_tp(self, current_price: float) -> Optional[Dict]:
        """Periksa apakah harga saat ini menyentuh SL atau TP"""
        if not self.active_position:
            return None

        pos = self.active_position
        side = pos["side"]
        entry = pos["entry_price"]

        close_reason = None
        if side == "BUY":
            if current_price <= pos["sl_price"]:
                close_reason = "STOP_LOSS"
            elif current_price >= pos["tp_price"]:
                close_reason = "TAKE_PROFIT"
        elif side == "SELL":
            if current_price >= pos["sl_price"]:
                close_reason = "STOP_LOSS"
            elif current_price <= pos["tp_price"]:
                close_reason = "TAKE_PROFIT"

        if close_reason:
            return self.close_position(current_price, reason=close_reason)

        return None

    def close_position(self, exit_price: float, reason: str = "MANUAL") -> Dict:
        if not self.active_position:
            return {"status": "error", "message": "No active position to close"}

        pos = self.active_position
        side = pos["side"]
        entry = pos["entry_price"]
        amount = pos["amount"]

        raw_revenue = exit_price * amount
        exit_fee = raw_revenue * (self.fee_pct / 100.0)
        net_revenue = raw_revenue - exit_fee

        if side == "BUY":
            pnl = (exit_price - entry) * amount - (pos["fee"] + exit_fee)
        else:
            pnl = (entry - exit_price) * amount - (pos["fee"] + exit_fee)

        pnl_pct = (pnl / pos["cost"]) * 100.0
        self.balance += net_revenue

        closed_trade = {
            **pos,
            "exit_price": exit_price,
            "closed_at": datetime.now().isoformat(),
            "pnl": round(pnl, 4),
            "pnl_pct": round(pnl_pct, 2),
            "close_reason": reason,
            "exit_fee": exit_fee
        }

        self.trade_history.insert(0, closed_trade)
        self.active_position = None
        self. _save_state()

        return {"status": "success", "closed_trade": closed_trade}

    def get_stats(self, current_price: float = 0.0) -> Dict:
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for t in self.trade_history if t["pnl"] > 0)
        losing_trades = sum(1 for t in self.trade_history if t["pnl"] < 0)
        win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0
        total_pnl = sum(t["pnl"] for t in self.trade_history)
        total_pnl_pct = ((self.balance - self.initial_balance) / self.initial_balance) * 100.0

        unrealized_pnl = 0.0
        unrealized_pnl_pct = 0.0
        if self.active_position and current_price > 0:
            pos = self.active_position
            if pos["side"] == "BUY":
                unrealized_pnl = (current_price - pos["entry_price"]) * pos["amount"]
            else:
                unrealized_pnl = (pos["entry_price"] - current_price) * pos["amount"]
            unrealized_pnl_pct = (unrealized_pnl / pos["cost"]) * 100.0

        return {
            "balance": round(self.balance, 2),
            "initial_balance": round(self.initial_balance, 2),
            "total_pnl": round(total_pnl, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_pnl_pct": round(unrealized_pnl_pct, 2),
            "win_rate": round(win_rate, 1),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "active_position": self.active_position
        }
