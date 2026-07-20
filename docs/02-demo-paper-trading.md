# 🟡 02. Mode Demo (Paper Trading Simulator)

Dokumen ini menjelaskan cara kerja dan pengujian bot pada **Mode Demo (Paper Trading)** tanpa risiko finansial.

---

## 💡 Apa itu Paper Trading?
Paper Trading adalah simulasi perdagangan di mana bot mengeksekusi order *Buy* dan *Sell* secara otomatis di pasar riil, tetapi menggunakan **saldo virtual**. 

Fitur ini berguna untuk:
- Menguji efektivitas sinyal indikator EMA & RSI pada kondisi pasar terkini.
- Mengamati reaksi otomatis Stop-Loss (SL) dan Take-Profit (TP).
- Menilai kecocokan parameter strategi sebelum menghubungkan modal uang asli.

---

## 🛠️ Fitur Utama Mode Demo

1. **Saldo Virtual Initial $10,000 USD**:
   Setiap pengguna mendapatkan modal awal $10,000 USD virtual untuk melakukan uji coba transaksi.

2. **Simulasi Slippage & Fee Bursa**:
   Order simulasi menghitung potong biaya transaksi (*spot trading fee* 0.1%) agar estimasi profit/loss bersih mendekati transaksi bursa asli.

3. **Indikator Visual Badge**:
   Saat berada dalam Mode Demo, Header Dashboard akan menampilkan badge bertuliskan `🟡 DEMO (PAPER TRADING)`.

---

## 🔄 Cara Reset Saldo Demo
Jika saldo simulasi Anda habis atau Anda ingin memulai pengujian strategi dari awal:
1. Buka Web Dashboard di `http://localhost:5173`.
2. Pada Card **SALDO PAPER TRADING**, klik tombol kecil bertuliskan **"Reset Saldo Demo"** di pojok kiri bawah card.
3. Konfirmasi tindakan. Saldo virtual akan langsung kembali ke **$10,000.00 USDT**.

---

## 📊 Langkah Pengujian Strategi di Mode Demo
1. Klik tombol **START BOT** pada Header Dashboard.
2. Amati **LIVE SYSTEM LOGS** di pojok kanan bawah. Bot akan mulai membaca candlestick per menit.
3. Begitu kondisi indikator terpenuhi (Golden Cross EMA + RSI oversold), bot akan secara otomatis membuka posisi **BUY** simulasi.
4. Notifikasi simulasi akan dikirimkan ke Telegram (jika Telegram terhubung) dengan label `[DEMO]`.
