# ❓ 07. Panduan Troubleshooting & FAQ

Dokumen ini memuat solusi dari masalah umum (*frequently asked questions*) dan langkah penyelesaian kendala teknis.

---

## ❓ FAQ & Troubleshooting

### 1. Web Dashboard menampilkan pesan "Menghubungkan ke Backend Engine..." atau gagal fetching data
- **Penyebab**: Server backend Python (`run.py`) belum dijalankan atau mati.
- **Solusi**: 
  1. Buka terminal, masuk ke `d:\Personal\Project\trading-bot\backend`.
  2. Jalankan `python run.py`.
  3. Pastikan output terminal menampilkan: `🚀 Launching Trading Bot Backend on http://0.0.0.0:8000`.

---

### 2. Pesan Tes Telegram gagal dikirim (Error 400 / 500)
- **Penyebab**: 
  - Token Bot atau Chat ID yang dimasukkan salah/kurang karakter.
  - Anda belum pernah menekan tombol `/start` pada Bot Telegram Anda.
- **Solusi**:
  1. Buka aplikasi Telegram, cari username bot Anda.
  2. Klik tombol **START** / kirim `/start` ke bot Anda terlebih dahulu.
  3. Pastikan nomor Chat ID diambil dari `@userinfobot`.
  4. Coba kembali klik tombol **"Test Send Telegram Notification"** di Web Dashboard.

---

### 3. Apakah bot bisa dijalankan 24 jam non-stop (24/7)?
- **Jawab**: Ya! Untuk menjalankan 24/7:
  - Anda dapat membiarkan komputer Anda tetap menyala dan menjalankan `python run.py`.
  - Atau mengunggah folder `backend` ke cloud server (seperti VPS Linux Ubuntu di DigitalOcean, AWS, Linode, atau Hetzner) dan mengaktifkan service menggunakan `pm2` atau `systemd`.

---

### 4. Bagaimana jika jaringan internet terputus di tengah jalan?
- **Jawab**: Bot memiliki fitur pemulihan koneksi WebSocket otomatis (*auto-reconnect*). Begitu jaringan terhubung kembali, Dashboard dan Backend akan menyinkronkan data secara otomatis.

---

### 5. Bagaimana cara mengganti koin Kripto yang diperdagangkan?
- **Jawab**: Buka Web Dashboard -> **SETTINGS** -> Ubah kolom `Trading Symbol` dari `BTC/USDT` menjadi koin lain seperti `ETH/USDT`, `SOL/USDT`, atau `BNB/USDT`, lalu klik **Simpan Pengaturan**.
