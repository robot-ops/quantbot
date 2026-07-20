# 🛠️ 10. Panduan Alur Pengembangan (Development Workflow & CI/CD)

Dokumen ini berisi panduan teknis bagi developer untuk melakukan iterasi pengembangan (*development*), penambahan fitur baru, pengujian lokal, dan pengelolaan repositori Git.

---

## 🔄 1. Alur Pengembangan Lokal (Local Iteration)

Backend dan Frontend dirancang dengan fitur **Hot-Reloading** otomatis saat pengodean:

### A. Backend Python (FastAPI Engine)
```bash
cd backend
python run.py
```
- Server uvicorn berjalan dengan opsi `reload=True`. Setiap kali file `.py` diubah dan disimpan, backend akan merestart otomatis secara instan.

### B. Frontend React (Vite Web Dashboard)
```bash
cd frontend
npm run dev
```
- Vite menggunakan **Hot Module Replacement (HMR)**. Setiap perubahan pada file `.jsx` atau `.css` akan langsung ter-render di browser tanpa perlu *refresh*.

---

## 🌿 2. Strategi Branching Git (DevOps Standard)

Untuk menjaga stabilitas kode pada branch `main`:

1. **Buat Branch Fitur Baru**:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/nama-fitur-baru
   ```
2. **Commit dengan Standard Conventional Commits**:
   ```bash
   git add .
   git commit -m "feat(indicator): tambahkan indikator MACD & Bollinger Bands"
   # atau fix(ui): perbaiki alignment responsive header
   ```
3. **Push & Buat Pull Request (PR)**:
   ```bash
   git push origin feature/nama-fitur-baru
   ```
   Buka [GitHub Repository](https://github.com/robot-ops/quantbot) dan buat *Pull Request* untuk menguji dan merge ke branch `main`.

---

## 🧩 3. Panduan Arsitektur Penambahan Fitur Baru

### A. Menambah Indikator / Strategi Trading Baru
1. **Kalkulasi Matematis**: Tambahkan fungsi indikator baru pada `backend/app/services/indicator.py`.
2. **Logika Evaluasi Sinyal**: Hubungkan aturan indikator baru pada `backend/app/services/strategy.py` di dalam fungsi `evaluate_market_tick()`.
3. **Form Antarmuka UI**: Tambahkan input parameter kontrol di `frontend/src/components/SettingsModal.jsx`.

### B. Menambah Saluran Notifikasi Baru (Misal: Discord Webhook)
1. **Service Class**: Buat modul baru `backend/app/services/discord_service.py`.
2. **Integrasi Event**: Panggil `DiscordService` pada event `send_trade_open_alert` & `send_trade_close_alert` di `strategy.py`.
