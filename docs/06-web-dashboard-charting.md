# 🖥️ 06. Web Dashboard & Visualisasi Charting

Dokumen ini menjelaskan komponen antarmuka (*UI*) dan visualisasi grafik pada **QuantBot Pro Web Dashboard**.

---

## 🎨 Desain Aesthetic: Dark Mode Glassmorphism

Dashboard dirancang dengan estetika modern menggunakan tema **Dark Mode Glassmorphism**:
- Transparansi blur kaca (*glass panels*) dengan aksen warna neon.
- Tipografi dari Google Fonts (`Outfit` untuk teks utama dan `JetBrains Mono` untuk angka harga/keuangan).
- Animasi transisi halus dan responsif di berbagai ukuran layar.

---

## 🧭 Panduan Komponen Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│ HEADER: Logo | Symbol/Price | Mode Badge | Telegram Status | Controls   │
├─────────────────────────────────────────────────────────────────────────┤
│ METRICS CARDS: Saldo | Total PnL ($ / %) | Win Rate % | Total Trades    │
├─────────────────────────────────────────────────────────────────────────┤
│ CHART: Live Candlestick TradingView (Up/Down Color + Buy/Sell Markers)  │
├───────────────────────────────────────────┬─────────────────────────────┤
│ TABEL RIWAYAT TRANSAKSI (Filter Win/Loss) │ LIVE SYSTEM LOGS TERMINAL   │
└───────────────────────────────────────────┴─────────────────────────────┘
```

1. **Header Bar**:
   - Menampilkan status running bot (**BOT ACTIVE** / **BOT PAUSED**).
   - Penunjuk **Mode Switcher** (`🟡 DEMO (PAPER TRADING)` / `🔴 LIVE TRADING ACTIVE`).
   - Tombol utama **START BOT**, **STOP BOT**, dan **SETTINGS**.

2. **Metrics Cards**:
   - **Saldo**: Menampilkan saldo USDT terkini.
   - **Total Profit / Loss**: Persentase & nominal keuntungan/kerugian bersih.
   - **Win Rate**: Persentase tingkat kemenangan dari total transaksi.
   - **Total Transaksi**: Jumlah order yang telah diselesaikan.

3. **TradingView Lightweight Candlestick Chart**:
   - Menggunakan library resmi **TradingView Lightweight Charts v5**.
   - Menampilkan pergerakan grafik harga realtime.
   - Menandai titik eksekusi dengan panah **BUY** (Panah Hijau) atau **SELL** (Panah Merah) di harga masuk.

4. **Tabel Riwayat Transaksi**:
   - Mencatat detail order yang telah ditutup (Entry Price, Exit Price, Amount, PnL, dan Alasan Penutupan `TAKE_PROFIT` / `STOP_LOSS`).
   - Filter cepat `ALL`, `WIN`, dan `LOSS`.

5. **Live System Logs Console**:
   - Menampilkan terminal log aktivitas bot secara langsung (fetch data harga, kalkulasi sinyal indikator, eksekusi order).
