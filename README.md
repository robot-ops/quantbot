# 🤖 Professional Crypto Trading Bot & Web Dashboard

Bot Otomasi Trading Kripto berbasis Python & React dengan arsitektur **Trader Kuantitatif (Quant Trading)**. Dilengkapi dengan **Dual-Engine (Demo/Paper Trading vs Live Real Trading)**, **Web Dashboard Interaktif (TradingView Chart)**, **Indikator EMA & RSI**, **Manajemen Risiko Terukur (Stop-Loss, Take-Profit, Max Daily Drawdown)**, serta **Integrasi Telegram Bot**.

---

## 📚 Dokumentasi Terpisah Per Fitur (`/docs`)

Dokumentasi penyiapan dan panduan aplikasi telah dibagi secara modular per fitur di dalam folder **[`/docs`](file:///d:/Personal/Project/trading-bot/docs/README.md)**:

1. 🚀 **[01. Panduan Instalasi & Setup Dasar](file:///d:/Personal/Project/trading-bot/docs/01-installation-guide.md)**
2. 🟡 **[02. Mode Demo (Paper Trading Simulator)](file:///d:/Personal/Project/trading-bot/docs/02-demo-paper-trading.md)**
3. 🔴 **[03. Mode Live Trading & Keamanan API Key](file:///d:/Personal/Project/trading-bot/docs/03-live-trading-security.md)**
4. 📱 **[04. Integrasi Telegram Bot & Remote Control](file:///d:/Personal/Project/trading-bot/docs/04-telegram-bot-integration.md)**
5. 📊 **[05. Strategi Indikator (EMA + RSI) & Manajemen Risiko](file:///d:/Personal/Project/trading-bot/docs/05-trading-strategy-risk.md)**
6. 🖥️ **[06. Web Dashboard & Visualisasi Charting](file:///d:/Personal/Project/trading-bot/docs/06-web-dashboard-charting.md)**
7. ❓ **[07. Panduan Troubleshooting & FAQ](file:///d:/Personal/Project/trading-bot/docs/07-troubleshooting-faq.md)**

---

## 🚀 Cara Menjalankan Cepat

### 1. Jalankan Backend Python Engine
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Jalankan server FastAPI backend (Port 8000)
python run.py
```

### 2. Jalankan Frontend Web Dashboard
```bash
cd frontend

# Install dependencies (jika belum)
npm install

# Jalankan dev server Vite (Port 5173)
npm run dev
```

Buka browser Anda di `http://localhost:5173`.

---

## 🔒 Catatan Keamanan API Key
Saat membuat API Key di bursa Kripto Anda (Binance/Tokocrypto/Bybit), **CUKUP CENTANG "ENABLE TRADING"**. **JANGAN CENTANG "ENABLE WITHDRAWAL"**. Dengan demikian, dana Anda tetap 100% aman tersimpan di bursa Anda sendiri.
