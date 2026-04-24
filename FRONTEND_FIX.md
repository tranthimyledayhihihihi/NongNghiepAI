# 🔧 Khắc Phục Frontend Không Chạy

## ✅ ĐÃ SỬA

Tôi đã tạo file `frontend/index.html` ở đúng vị trí (thư mục gốc frontend).

## 🚀 CÁC BƯỚC KHỞI ĐỘNG FRONTEND

### Bước 1: Cài đặt dependencies (nếu chưa cài)

```bash
cd frontend
npm install
```

**Chờ npm cài đặt xong** (có thể mất 2-3 phút lần đầu)

### Bước 2: Khởi động dev server

```bash
npm run dev
```

**Kết quả mong đợi:**
```
  VITE v5.0.11  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
  ➜  press h to show help
```

### Bước 3: Truy cập đúng URL

**❌ SAI:** `http://localhost:3000` (port này không có gì)

**✅ ĐÚNG:** `http://localhost:5173` (Vite dev server)

---

## 🔍 KIỂM TRA LỖI

### Lỗi 1: "Cannot find module"

**Nguyên nhân:** Chưa cài dependencies

**Giải pháp:**
```bash
cd frontend
npm install
```

### Lỗi 2: "Port 5173 already in use"

**Nguyên nhân:** Port đang được sử dụng

**Giải pháp:**
```bash
# Tìm process đang dùng port 5173
netstat -ano | findstr :5173

# Kill process (thay PID bằng số từ lệnh trên)
taskkill /PID <PID> /F

# Hoặc đổi port trong vite.config.js
```

### Lỗi 3: "Failed to resolve import"

**Nguyên nhân:** Thiếu file hoặc import sai

**Giải pháp:** Kiểm tra console để xem file nào bị thiếu

### Lỗi 4: Màn hình trắng

**Nguyên nhân:** Lỗi trong React component

**Giải pháp:**
1. Mở DevTools (F12)
2. Xem tab Console
3. Kiểm tra lỗi JavaScript

---

## 📊 CẤU TRÚC FRONTEND

```
frontend/
├── index.html              ← Entry point (ĐÃ TẠO)
├── package.json            ← Dependencies
├── vite.config.js          ← Vite config (port 5173)
├── tailwind.config.js      ← Tailwind CSS config
├── postcss.config.js       ← PostCSS config
│
└── src/
    ├── main.jsx            ← React entry point
    ├── App.jsx             ← Main App component
    ├── index.css           ← Global styles
    │
    ├── pages/              ← Page components
    │   ├── Dashboard.jsx
    │   ├── PricingPage.jsx
    │   ├── QualityCheckPage.jsx
    │   └── ...
    │
    ├── components/         ← Reusable components
    │   ├── Navbar.jsx
    │   ├── Sidebar.jsx
    │   └── ...
    │
    ├── services/           ← API services
    │   ├── api.js
    │   ├── priceApi.js
    │   └── ...
    │
    └── hooks/              ← Custom hooks
        └── useWebSocket.js
```

---

## 🎯 CHECKLIST

- [x] File `frontend/index.html` đã tạo
- [ ] Dependencies đã cài (`npm install`)
- [ ] Dev server đã start (`npm run dev`)
- [ ] Truy cập đúng URL: `http://localhost:5173`
- [ ] Không có lỗi trong console
- [ ] Backend đang chạy trên port 8000

---

## 🔗 KIỂM TRA BACKEND

Frontend cần backend để hoạt động. Đảm bảo backend đang chạy:

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Kiểm tra: http://localhost:8000/docs
```

---

## 📝 COMMANDS NHANH

```bash
# Cài dependencies
cd frontend
npm install

# Start dev server
npm run dev

# Build production
npm run build

# Preview production build
npm run preview
```

---

## 🌐 URLS QUAN TRỌNG

- **Frontend Dev:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **API ReDoc:** http://localhost:8000/redoc

---

## ⚡ QUICK START

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev

# Mở browser: http://localhost:5173
```

---

**Nếu vẫn gặp lỗi, gửi screenshot console (F12) để tôi giúp debug!** 🔍
