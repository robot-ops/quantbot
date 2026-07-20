# 🔴 03. Mode Live Trading & Keamanan API Key

Dokumen ini menjelaskan tata cara pengaktifan **Mode Live Trading** menggunakan modal uang asli serta **prinsip keamanan API Key**.

---

## 🔒 Panduan Keamanan API Key (Standar Industri)

Saat Anda menghubungkan bot ke akun bursa Kripto Anda (Binance, Tokocrypto, Bybit, KuCoin, OKX, dll.), bursa akan meminta Anda membuat **API Key** dan **API Secret**.

### ⚠️ PERINGATAN HAK AKSES (PERMISSIONS):
Saat membuat API Key di website bursa:
1. ✅ **Enable Reading (Membaca Data)**: Wajib dicentang agar bot bisa membaca saldo & data harga.
2. ✅ **Enable Spot / Futures Trading**: Wajib dicentang agar bot bisa mengeksekusi order *Buy* & *Sell*.
3. ❌ **ENABLE WITHDRAWAL (MENARIK UANG): JANGAN DICENTANG / UNCHECK**.

### 💡 Mengapa Izin Withdrawal Harus Dimatikan?
- Dengan menonaktifkan izin *Withdrawal*, **secara teknis Bot tidak memiliki kemampuan untuk mentransfer uang Anda keluar dari akun bursa**.
- Uang Anda tetap **100% aman tersimpan di akun bursa Anda sendiri**.
- Anda sebagai pemilik akun tetap bisa menarik uang (withdraw) kapan saja secara manual melalui aplikasi bursa di HP Anda.

---

## ⚙️ Cara Menghubungkan API Key & Mengaktifkan Mode Live

1. Buka Web Dashboard `http://localhost:5173`.
2. Klik tombol **SETTINGS** di kanan atas -> Pilih tab **Live Exchange API**.
3. Pilih nama bursa Anda (misal Binance / Tokocrypto / Bybit).
4. Masukkan `API Key` dan `API Secret` yang sudah dibuat di bursa Anda.
5. Klik **Simpan Pengaturan**.
6. Untuk beralih ke Mode Live, klik tombol badge di Header Dashboard dari `🟡 DEMO (PAPER TRADING)` menjadi `🔴 LIVE TRADING ACTIVE`.
7. Konfirmasi dialog peringatan keamanan yang muncul.
