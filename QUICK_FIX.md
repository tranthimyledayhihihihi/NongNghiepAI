# ⚡ KHẮC PHỤC NHANH - Frontend Không Chạy

## 🎯 VẤN ĐỀ

Bạn đang truy cập **http://localhost:3000** nhưng frontend chạy trên **http://localhost:5173**

## ✅ GIẢI PHÁP (3 BƯỚC)

### 1️⃣ Cài Dependencies
```bash
cd frontend
npm install
```
⏱️ Chờ 2-3 phút

### 2️⃣ Start Frontend
```bash
npm run dev
```
✅ Xem terminal hiện: `Local: http://localhost:5173/`

### 3️⃣ Truy Cập Đúng URL
```
❌ SAI: http://localhost:3000
✅ ĐÚNG: http://localhost:5173
```

---

## 🔥 FULL SETUP (2 TERMINALS)

### Terminal 1 - Backend
```bash
cd backend
uvicorn app.main:app --reload
```
✅ Backend: http://localhost:8000

### Terminal 2 - Frontend
```bash
cd frontend
npm install
npm run dev
```
✅ Frontend: http://localhost:5173

---

## 📋 CHECKLIST

- [ ] `cd frontend`
- [ ] `npm install` (chạy xong)
- [ ] `npm run dev` (đang chạy)
- [ ] Mở browser: `http://localhost:5173`
- [ ] Backend đang chạy: `http://localhost:8000`

---

## ⚠️ NẾU VẪN LỖI

### Lỗi: "Cannot find module"
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Lỗi: "Port 5173 already in use"
```bash
# Tìm và kill process
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### Màn hình trắng
1. Mở DevTools (F12)
2. Xem tab Console
3. Screenshot lỗi và gửi cho tôi

---

**Xem chi tiết:** `FRONTEND_FIX.md`
