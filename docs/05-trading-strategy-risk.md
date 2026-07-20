# 📊 05. Strategi Indikator (EMA + RSI) & Manajemen Risiko

Dokumen ini menjelaskan logika algoritma trading, konfigurasi sinyal indikator, dan fitur pengaman *Circuit Breaker*.

---

## 📈 Logika Strategi Sinyal Trading

Bot menggunakan strategi gabungan **EMA (Exponential Moving Average)** dan **RSI (Relative Strength Index)**:

1. **EMA Fast & EMA Slow**:
   - Secara *default*, bot menggunakan **EMA 9 (Cepat)** dan **EMA 21 (Lambat)**.
   - **Golden Cross (Bullish Signal)** terjadi ketika garis EMA Fast memotong ke atas garis EMA Slow, menandakan awal trend naik.
   - **Death Cross (Bearish Signal)** terjadi ketika garis EMA Fast memotong ke bawah garis EMA Slow, menandakan trend turun.

2. **RSI Filter (Konfirmasi Trend)**:
   - RSI (14) digunakan sebagai konfirmasi momentum.
   - Posisi **BUY** hanya dibuka jika Golden Cross terjadi DAN nilai RSI berada di bawah ambang batas *Overbought* (misal RSI < 65).

---

## 🛡️ Manajemen Risiko Terukur (Risk Management)

1. **Position Sizing Otomatis (% Risk Capital)**:
   Bot tidak mempertaruhkan seluruh saldo dalam 1 kali transaksi. Ukuran lot/size dihitung berdasarkan parameter `Risk Per Trade %` (misal 2% modal disiap-risikokan).

2. **Bracket Stop-Loss (SL) & Take-Profit (TP)**:
   Setiap kali order dibuka, SL dan TP langsung dipasang secara otomatis:
   - **Stop-Loss (SL)**: Misal 1.5% di bawah harga beli.
   - **Take-Profit (TP)**: Misal 3.0% di atas harga beli (menjamin *Risk-to-Reward Ratio / RRR* terukur 1:2).

3. **Circuit Breaker (Max Daily Drawdown Protection)**:
   Jika akumulasi rugi harian mencapai batas kerugian maksimal (misal 5%), bot akan memicu *Circuit Breaker*:
   - Bot otomatis berhenti secara instan (`is_running = False`).
   - Bot mengirimkan notifikasi bahaya `⚠️ CIRCUIT BREAKER: Max Daily Drawdown Reached` ke Telegram Anda demi menyelamatkan sisa modal.

---

## ⚙️ Cara Mengubah Parameter Strategi

1. Di Web Dashboard, klik **SETTINGS** -> Tab **Parameter Strategi**.
2. Anda dapat mengkustomisasi:
   - `Symbol`: Pasangan koin (misal `BTC/USDT`, `ETH/USDT`, `SOL/USDT`).
   - `Timeframe`: Interval lilin (`1m`, `5m`, `15m`, `1h`).
   - `EMA Fast / Slow`: Periode moving average (misal 9 & 21, atau 50 & 200).
   - `RSI Period & Thresholds`: Batas oversold/overbought (misal 35 & 65).
   - `Stop Loss % & Take Profit %`: Persentase jarak SL dan TP.
   - `Risk Per Trade % & Max Daily Drawdown %`: Batas risiko modal per transaksi dan batas rugi harian.
3. Klik **Simpan Pengaturan**.
