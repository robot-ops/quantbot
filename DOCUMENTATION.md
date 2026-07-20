# 📘 DOKUMENTASI LENGKAP SETUP & FITUR QUANTBOT PRO

Dokumen ini berisi panduan penyiapan (*setup guide*) dan penjelasan detail cara kerja aplikasi **QuantBot Pro (Crypto Trading Bot & Web Dashboard)** yang dibagi per fitur utama.

---

## 📋 Daftar Isi

1. [Prasyarat & Instalasi Dasar](#1-prasyarat--instalasi-dasar)
2. [Fitur 1: Mode Demo (Paper Trading Simulator)](#fitur-1-mode-demo-paper-trading-simulator)
3. [Fitur 2: Mode Live Trading & Keamanan API Key](#fitur-2-mode-live-trading--keamanan-api-key)
4. [Fitur 3: Integrasi Telegram Bot (Alerts & Remote Control)](#fitur-3-integrasi-telegram-bot-alerts--remote-control)
5. [Fitur 4: Strategi Indikator (EMA + RSI) & Manajemen Risiko](#fitur-4-strategi-indikator-ema--rsi--manajemen-risiko)
6. [Fitur 5: Web Dashboard & Visualisasi TradingView Chart](#fitur-5-web-dashboard--visualisasi-tradingview-chart)
7. [Panduan Troubleshooting & FAQ](#7-panduan-troubleshooting--faq)

---

## 1. Prasyarat & Instalasi Dasar

### Prasyarat Sistem
- **Python**: v3.10 atau lebih baru
- **Node.js**: v18.0 atau lebih baru (npm v9+)
- **OS**: Windows, macOS, atau Linux

### Panduan Jalankan Aplikasi

#### Step A: Server Backend (Python FastAPI)
1. Buka Terminal / PowerShell:
   ```bash
   cd d:\Personal\Project\trading-bot\backend
   ```
2. Install dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan server backend:
   ```bash
   python run.py
   ```
   *(Backend akan aktif di `http://localhost:8000`)*

#### Step B: Web Dashboard (React + Vite)
1. Buka Terminal baru:
   ```bash
   cd d:\Personal\Project\trading-bot\frontend
   ```
2. Install dependensi Node.js (jika belum):
   ```bash
   npm install
   ```
3. Jalankan server pengembang Web Dashboard:
   ```bash
   npm run dev
   ```
4. Buka browser di alamat: `http://localhost:5173`

---

## Fitur 1: Mode Demo (Paper Trading Simulator)

### 💡 Deskripsi
Mode Demo memungkinkan Anda menguji algoritma bot dan indikator teknikal menggunakan modal simulasi **$10,000 USD virtual** secara **100% bebas risiko tanpa membutuhkan API Key bursa**.

### ⚙️ Cara Setup & Penggunaan
1. Secara *default*, bot beroperasi dalam **Mode Demo** (Badge Kuning `🟡 DEMO (PAPER TRADING)` di Header).
2. Bot mengambil pergerakan harga Kripto asli secara *real-time* dari bursa (misal BTC/USDT).
3. Saat sinyal **Buy/Sell** terpicu, bot mensimulasikan pembelian/penjualan dengan menghitung *trading fee* (0.1%) dan mengeksekusi Stop-Loss/Take-Profit otomatis.
4. **Reset Saldo Simulasi**: Untuk mengembalikan saldo ke $10,000 USD, klik tombol **"Reset Saldo Demo"** pada card Saldo di Dashboard.

---

## Fitur 2: Mode Live Trading & Keamanan API Key

### 💡 Deskripsi
Mode Live digunakan saat Anda sudah yakin dengan statistik strategi di Mode Demo dan ingin menyerahkan eksekusi transaksi otomatis menggunakan modal asli di bursa Kripto Anda (misal Binance, Tokocrypto, Bybit, KuCoin, OKX).

### 🛡️ Panduan Keamanan Penting (Pengaturan Izin API Key)
Saat membuat API Key di website/aplikasi bursa Kripto Anda:
1. ✅ Centang **Enable Reading** (Membaca harga & saldo).
2. ✅ Centang **Enable Spot Trading** atau **Futures Trading** (Membeli & menjual koin).
3. ❌ **JANGAN CENTANG (UNCHECK) "ENABLE WITHDRAWAL"**.
   > **Kenapa?** Dengan mematikan izin Withdrawal, **secara teknis Bot tidak memiliki akses atau kemampuan untuk mentransfer uang keluar dari bursa**. Uang Anda 100% tetap aman tersimpan di bursa Anda sendiri. Anda tetap dapat menarik uang secara manual dari HP Anda kapan saja.

### ⚙️ Cara Setup Mode Live
1. Buka Web Dashboard `http://localhost:5173`, klik **SETTINGS** di kanan atas.
2. Pilih tab **Live Exchange API**.
3. Pilih nama bursa Anda (misal Binance, Tokocrypto, Bybit).
4. Masukkan `API Key` dan `API Secret` Anda, lalu klik **Simpan Pengaturan**.
5. Di Header Dashboard, klik badge **🟡 DEMO (PAPER TRADING)** untuk beralih ke **🔴 LIVE TRADING ACTIVE**.

---

## Fitur 3: Integrasi Telegram Bot (Alerts & Remote Control)

### 💡 Deskripsi
Menerima notifikasi pesan instan di HP Anda setiap kali bot membuka/menutup posisi, serta melakukan kontrol bot jarak jauh melalui pesan Telegram Chat.

### ⚙️ Cara Setup Telegram Bot

#### Step 1: Buat Telegram Bot & Token
1. Buka aplikasi Telegram di HP/Desktop Anda, cari pengguna `@BotFather`.
2. Kirim pesan `/newbot`, lalu ikuti petunjuk pembuatan nama bot.
3. `@BotFather` akan memberikan **Bot Token** (contoh: `7123456789:AAE...xyz`). Simpan token ini.

#### Step 2: Dapatkan Chat ID Anda
1. Cari pengguna `@userinfobot` di Telegram.
2. Kirim pesan apa saja (misal `hello`).
3. `@userinfobot` akan membalas dengan **Id** Anda (contoh: `987654321`). Simpan nomor ID ini.

#### Step 3: Hubungkan ke Dashboard
1. Di Web Dashboard, klik **SETTINGS** -> Tab **Telegram Bot**.
2. Masukkan **Bot Token** dan **Chat ID** Anda.
3. Klik tombol **"Test Send Telegram Notification"**. Jika berhasil, HP Anda akan langsung menerima pesan tes dari Bot Telegram Anda!
4. Klik **Simpan Pengaturan**.

### 📲 Perintah Remote Chat Telegram
Anda dapat mengirim perintah teks ini langsung ke chat Bot Telegram Anda:
- `/status` — Memeriksa saldo terkini, mode aktif, Win Rate, dan posisi yang sedang terbuka.
- `/summary` — Meminta ringkasan laporan statistik trading harian.
- `/pause` — Menghentikan aktivitas bot secara instan dari jarak jauh.
- `/resume` — Menjalankan kembali bot trading.

---

## Fitur 4: Strategi Indikator (EMA + RSI) & Manajemen Risiko

### 💡 Deskripsi
Bot menggunakan kombinasi algoritma teknikal **EMA Crossover** dan filter **RSI (Relative Strength Index)** untuk mengonfirmasi arah trend pasar sebelum membuka posisi.

### 📊 Logika Sinyal Trading
- **Sinyal Beli (Buy / Long)**:
  - Terjadi **Golden Cross**: Garis EMA Cepat (misal EMA 9) memotong ke atas Garis EMA Lambat (misal EMA 21).
  - Dan **RSI** berada di bawah ambang batas Overbought (misal RSI < 65), menandakan trend naik masih memiliki ruang pertumbuhan.
- **Stop-Loss (SL) & Take-Profit (TP)**:
  - Otomatis terpasang begitu posisi dibuka (misal SL = 1.5%, TP = 3.0%).
  - Memastikan *Risk-to-Reward Ratio (RRR)* terukur 1:2.

### 🛡️ Institutional Risk Manager & Circuit Breaker
- **Dynamic Position Sizing**: Bot menghitung besaran lot/size berdasarkan % maksimal alokasi modal per trade (misal max risk 2% dari saldo equity).
- **Max Daily Drawdown Protection**: Jika akumulasi rugi harian mencapai batas toleransi (misal 5%), bot akan memicu *Circuit Breaker* secara otomatis, menghentikan bot, dan mengirim peringatan bahaya ke Telegram Anda demi menyelamatkan modal tersisa.

### ⚙️ Cara Mengubah Parameter Strategi
Buka Dashboard -> **SETTINGS** -> Tab **Parameter Strategi**:
- Ubah simbol (misal `ETH/USDT`, `SOL/USDT`).
- Ubah Timeframe (`1m`, `5m`, `15m`, `1h`).
- Ubah periode EMA, threshold RSI, % SL/TP, serta Risk per Trade.

---

## Fitur 5: Web Dashboard & Visualisasi TradingView Chart

### 💡 Deskripsi
Antarmuka pengguna grafis (GUI) berbasis Web dengan tema **Dark Mode Glassmorphism** yang menyediakan pemantauan visual lengkap.

### 🖥️ Elemen Antarmuka
1. **Header Bar**: 
   - Logo & Nama App.
   - Penunjuk harga terkini & Timeframe.
   - Badge mode aktif (`DEMO` / `LIVE`).
   - Tombol **START BOT**, **STOP BOT**, dan **SETTINGS**.
2. **Cards Statistik (Metrics)**:
   - **Saldo**: Menampilkan saldo USDT terkini.
   - **Total Profit / Loss**: Persentase & nominal keuntungan/kerugian bersih.
   - **Win Rate**: Persentase tingkat kemenangan dari total transaksi.
   - **Total Transaksi**: Jumlah order yang telah diselesaikan.
3. **Live Candlestick Chart**:
   - Grafik candlestick interaktif berbasis **TradingView Lightweight Charts**.
   - Menampilkan marker panah visual **BUY** (Panah Hijau) atau **SELL** (Panah Merah) langsung di titik harga eksekusi.
4. **Tabel Riwayat Transaksi**:
   - Menyimpan daftar order lengkap dengan ID, harga entry/exit, nominal PnL, dan alasan penutupan order (`STOP_LOSS` / `TAKE_PROFIT` / `MANUAL`).
5. **Live System Logs Console**:
   - Terminal log real-time yang menampilkan aktivitas internal bot detik demi detik.

---

## 7. Panduan Troubleshooting & FAQ

### ❓ FAQ 1: Web Dashboard menampilkan pesan "Menghubungkan ke Backend Engine..."
**Penyebab**: Server backend Python (`run.py`) belum dijalankan.
**Solusi**: Buka terminal baru, masuk ke folder `backend`, lalu jalankan `python run.py`.

### ❓ FAQ 2: Kenapa pesan Tes Telegram gagal dikirim?
**Penyebab**: Bot Token atau Chat ID yang diinputkan salah, atau Anda belum pernah menekan tombol `/start` pada bot Telegram Anda.
**Solusi**: Buka Telegram, cari username bot Anda, klik `/start` terlebih dahulu. Pastikan Bot Token diambil secara utuh dari `@BotFather` tanpa spasi tambahan.

### ❓ FAQ 3: Apakah saya bisa membiarkan bot berjalan 24 jam non-stop?
**Jawab**: Ya! Untuk menjalankan 24/7, Anda dapat membiarkan terminal Python berjalan di komputer Anda, atau mengunggah folder `backend` ke cloud server (seperti VPS Linux, AWS, atau DigitalOcean).

---

*QuantBot Pro — Built with Python, FastAPI, CCXT, React, and TradingView Lightweight Charts.*
