# 📱 04. Integrasi Telegram Bot & Remote Control

Dokumen ini menjelaskan tata cara pembuatan Bot Telegram, menghubungkan notifikasi real-time, dan menggunakan perintah *remote control*.

---

## 🛠️ Langkah 1: Buat Telegram Bot & Token

1. Buka aplikasi Telegram di HP/Desktop.
2. Cari pengguna **`@BotFather`** (akun resmi Telegram bercentang biru).
3. Kirim pesan `/newbot`.
4. Ikuti instruksi: beri nama bot Anda (misal `MyQuantBot`) dan username bot yang diakhiri dengan `bot` (misal `my_quant_trading_bot`).
5. `@BotFather` akan memberikan **HTTP API Token** (contoh: `7123456789:AAEdefGhIJKlmNoPQRsTUVwxyZ`). Simpan token ini.

---

## 🆔 Langkah 2: Dapatkan Telegram Chat ID Anda

1. Cari pengguna **`@userinfobot`** di Telegram.
2. Kirim pesan apa saja (misal `hello`).
3. Bot akan membalas dengan info akun Anda. Catat nomor pada baris **Id** (contoh: `987654321`).

---

## 🔗 Langkah 3: Hubungkan ke Web Dashboard

1. Buka Web Dashboard `http://localhost:5173`.
2. Klik **SETTINGS** -> Pilih tab **Telegram Bot**.
3. Masukkan **Telegram Bot Token** dan **Telegram Chat ID**.
4. Klik tombol **"Test Send Telegram Notification"**.
5. Jika konfigurasi benar, HP Anda akan langsung menerima pesan dari Bot Telegram Anda:
   `⚡ Tes Koneksi Telegram Trading Bot - Selamat! Bot Telegram Anda berhasil terhubung.`
6. Klik **Simpan Pengaturan**.

---

## 📲 Perintah Remote Chat Telegram

Anda dapat mengirim perintah teks ini kapan saja di ruang chat Bot Telegram Anda:

- `/status` — Memeriksa saldo terkini, mode aktif (Demo/Live), Win Rate, PnL, dan posisi aktif.
- `/summary` — Meminta ringkasan laporan statistik trading.
- `/pause` — Menghentikan aktivitas trading bot secara instan dari jarak jauh.
- `/resume` — Menjalankan kembali bot trading.
