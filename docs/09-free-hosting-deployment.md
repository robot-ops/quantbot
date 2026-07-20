# ☁️ 09. Panduan Deploy Free Hosting 24/7 (Vercel, Netlify, Render & VPS)

Dokumen ini berisi panduan mengunggah (*deploy*) aplikasi **QuantBot Pro** ke platform hosting **100% GRATIS** (termasuk Vercel, Netlify, Render.com, dan Oracle VPS) agar bot dapat berjalan **24 jam non-stop 24/7 tanpa perlu laptop Anda menyala**.

---

## 🏗️ Pembagian Peran Hosting (Frontend vs Backend)

Proyek ini terbagi menjadi 2 komponen utama:

| Komponen | Peran | Platform Gratis Terbaik | Keterangan |
| :--- | :--- | :--- | :--- |
| **Frontend Web Dashboard** | Menampilkan Grafik & UI | **Netlify** atau **Vercel** | SSL/HTTPS gratis, CDN sangat cepat, gratis selamanya |
| **Backend Python Engine** | Mengolah Indikator & Trading | **Render.com** atau **Oracle VPS** | Menjalankan Python 3.10+, CCXT, & WebSocket 24/7 |

---

## ⚡ Deploy Frontend ke Netlify (100% Gratis)

Netlify adalah salah satu platform terpopuler untuk meng-host Web Dashboard React/Vite.

### Langkah-Langkah Deploy ke Netlify:
1. Buat akun gratis di [Netlify.com](https://www.netlify.com/).
2. Klik tombol **Add new site** -> Pilih **Import an existing project**.
3. Hubungkan akun GitHub Anda dan pilih repositori `trading-bot`.
4. Konfigurasikan Build Settings:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
5. Klik **Deploy frontend**.
6. Dalam waktu kurang dari 1 menit, Web Dashboard Anda akan aktif dengan domain SSL gratis (contoh: `https://quantbot-pro.netlify.app`).

---

## 🚀 Deploy Backend Python ke Render.com (Gratis + KeepAlive)

Karena Netlify dikhususkan untuk Frontend, backend Python FastAPI akan di-host di Render.com:

1. Buat akun di [Render.com](https://render.com/).
2. Klik **New +** -> Pilih **Web Service**.
3. Hubungkan repositori GitHub Anda.
4. Pengaturan Web Service:
   - Name: `quantbot-backend`
   - Root Directory: `backend`
   - Environment: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python run.py`
5. Klik **Create Web Service**.

### Trik UptimeRobot (Menjaga Backend 24/7 Tanpa Sleep)
1. Buka [UptimeRobot.com](https://uptimerobot.com/) (Gratis).
2. Tambahkan monitor HTTP(s) ke URL backend Render Anda (`https://quantbot-backend.onrender.com/api/status`).
3. Set interval ping setiap **5 menit**. Backend akan menyala **24/7 non-stop!**
