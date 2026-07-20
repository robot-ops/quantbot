# 🚀 01. Panduan Instalasi & Setup Dasar

Dokumen ini berisi langkah-langkah penyiapan lingkungan (*environment*) dan cara menjalankan aplikasi **QuantBot Pro** dari awal.

---

## 💻 Prasyarat Sistem
Sebelum memulai, pastikan perangkat Anda telah terinstall software berikut:
- **Python**: v3.10 atau versi yang lebih baru ([Download Python](https://www.python.org/downloads/))
- **Node.js**: v18.0 atau versi yang lebih baru ([Download Node.js](https://nodejs.org/))
- **Git**: (Opsional) untuk mengelola repositori kode

---

## ⚙️ Langkah 1: Jalankan Server Backend (Python FastAPI)

Server backend menangani pengolahan data harga, eksekusi indikator, kalkulasi risiko, dan koneksi WebSocket.

1. Buka Terminal / PowerShell.
2. Masuk ke direktori backend:
   ```bash
   cd d:\Personal\Project\trading-bot\backend
   ```
3. Install seluruh paket dependensi Python:
   ```bash
   pip install -r requirements.txt
   ```
4. Jalankan server backend:
   ```bash
   python run.py
   ```
5. Jika berhasil, terminal akan menampilkan pesan:
   `🚀 Launching Trading Bot Backend on http://0.0.0.0:8000`

---

## 🖥️ Langkah 2: Jalankan Web Dashboard (React + Vite)

Web Dashboard menyediakan antarmuka visual interaktif untuk mengontrol dan memantau bot secara *real-time*.

1. Buka Terminal kedua (buka window/tab baru).
2. Masuk ke direktori frontend:
   ```bash
   cd d:\Personal\Project\trading-bot\frontend
   ```
3. Install dependensi modul Node.js:
   ```bash
   npm install
   ```
4. Jalankan dev server Vite:
   ```bash
   npm run dev
   ```
5. Buka alamat berikut pada browser Anda:
   `http://localhost:5173`

---

## 🔍 Verifikasi Instalasi
- Pastikan indikator status di Header Dashboard menampilkan **BOT PAUSED** atau **BOT ACTIVE**.
- Pastikan grafik candlestick muncul di bagian tengah layar.
- Jika terdapat pesan koneksi gagal, pastikan terminal `python run.py` tetap berjalan.
