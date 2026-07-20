# 🔑 08. Panduan Mendapatkan API Key Bursa Kripto (Live Exchange)

Dokumen ini berisi langkah-langkah pembuatan **API Key & API Secret** pada bursa Kripto terpopuler (Tokocrypto, Binance, Bybit, KuCoin, OKX) lengkap dengan instruksi keamanan.

---

## 🔒 Peringatan Keamanan Penting (Harus Dibaca)

Saat membuat API Key di bursa Kripto mana pun:
- ✅ **Centang "Membaca / Read"**: Untuk melihat saldo dan harga.
- ✅ **Centang "Spot / Futures Trading"**: Untuk melakukan order Buy/Sell otomatis.
- ❌ **JANGAN CENTANG (UNCHECK) "WITHDRAWAL / PENARIKAN"**: 
  > **Mengapa?** Jika izin penarikan dimatikan, **Secara teknis Bot TIDAK MEMILIKI AKSES untuk mentransfer atau mengambil uang Anda keluar dari bursa**. Uang Anda 100% tetap aman di akun bursa Anda sendiri.

---

## 🇮🇩 1. Tokocrypto (Indonesia)

1. Login ke akun [Tokocrypto.com](https://www.tokocrypto.com/).
2. Klik ikon **Profil** di kanan atas -> Pilih **Manajemen API**.
3. Masukkan Nama Label API (misal: `QuantBot`).
4. Klik **Buat API** -> Masukkan kode verifikasi Email / Google Authenticator.
5. Klik **Edit Izin**:
   - ✅ Centang **Membaca**
   - ✅ Centang **Memungkinkan Perdagangan (Trading)**
   - ❌ **JANGAN CENTANG "Penarikan" (Withdrawal)**
6. Catat **API Key** dan **Secret Key** (Secret Key hanya muncul 1 kali).

---

## 🟡 2. Binance

1. Login ke akun [Binance.com](https://www.binance.com/).
2. Klik ikon **Profil** -> Pilih **API Management**.
3. Klik **Create API** -> Pilih **System generated** -> Klik **Next**.
4. Beri label nama (misal: `QuantBot`).
5. Verifikasi keamanan (Email & 2FA).
6. Pada API Key yang baru dibuat, klik **Edit Restrictions**:
   - ✅ Centang **Enable Reading**
   - ✅ Centang **Enable Spot & Margin Trading**
   - ❌ **JANGAN CENTANG "Enable Withdrawals"**
7. Copy **API Key** dan **Secret Key**.

---

## 🟠 3. Bybit

1. Login ke akun [Bybit.com](https://www.bybit.com/).
2. Hover ikon **Profil** -> Pilih **API**.
3. Klik **Create New Key** -> Pilih **System-generated API Keys**.
4. Pilih opsi **API Transaction** dengan akses **Read-Write**.
5. Centang **Orders** & **Positions** pada Spot / Derivatives.
6. ❌ **JANGAN CENTANG izin "Withdraw"**.
7. Simpan **API Key** dan **Secret Key**.

---

## 📲 Cara Menginputkan API Key ke QuantBot Pro

1. Buka Web Dashboard QuantBot Pro (`http://localhost:5173`).
2. Klik tombol **SETTINGS** di kanan atas.
3. Pilih tab **Live Exchange API**.
4. Pilih Bursa Kripto Anda (misal Tokocrypto / Binance / Bybit).
5. Tempelkan (*Paste*) **API Key** dan **API Secret** Anda pada kolom yang tersedia.
6. Klik **Simpan Pengaturan**.
7. Beralih dari mode `🟡 DEMO (PAPER TRADING)` ke `🔴 LIVE TRADING ACTIVE` di Header Dashboard.
