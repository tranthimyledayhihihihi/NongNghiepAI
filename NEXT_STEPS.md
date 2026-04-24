# 🎯 NEXT STEPS - Bước Tiếp Theo

## ✅ Đã Hoàn Thành

Tất cả files đã được chuyển đổi từ PostgreSQL sang SQL Server:
- ✅ 7 table definitions
- ✅ 3 seed data files  
- ✅ 3 stored procedures
- ✅ 4 Python models
- ✅ Configuration files
- ✅ Setup & test scripts
- ✅ Complete documentation

## 🚀 Bây Giờ Bạn Cần Làm Gì?

### 📋 Checklist

#### 1. Kiểm Tra SQL Server
- [ ] SQL Server đang chạy
- [ ] Có thể kết nối qua SQL Server Management Studio
- [ ] Database `NongNghiepAI` đã tồn tại (hoặc sẽ tạo)

#### 2. Kiểm Tra ODBC Driver
- [ ] ODBC Driver 17 for SQL Server đã cài
- [ ] Kiểm tra: Mở "ODBC Data Sources (64-bit)" → Tab "Drivers"
- [ ] Nếu chưa có: Download tại https://go.microsoft.com/fwlink/?linkid=2249004

#### 3. Cài Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```
- [ ] pyodbc installed
- [ ] pymssql installed
- [ ] sqlalchemy installed

#### 4. Chạy Setup Script
```bash
python scripts/setup_sqlserver.py
```
**Kết quả mong đợi:**
```
✅ Database setup completed successfully!
✓ Found 8 tables
✓ CropTypes: 10 rows
✓ Regions: 63 rows
✓ MarketPrices: 13 rows
```

#### 5. Test Connection
```bash
python backend/test_sqlserver_connection.py
```
**Kết quả mong đợi:**
```
🎉 All tests passed! Ready to use SQL Server.
```

#### 6. Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```
**Kết quả mong đợi:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
```

#### 7. Test API
- [ ] Mở browser: http://localhost:8000/docs
- [ ] Test endpoint: GET `/health`
- [ ] Test endpoint: GET `/api/harvest/crops`

#### 8. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
**Kết quả mong đợi:**
```
Local: http://localhost:5173/
```

#### 9. Test Application
- [ ] Mở browser: http://localhost:5173
- [ ] Kiểm tra UI load
- [ ] Test các chức năng

---

## 📝 Commands Tóm Tắt

### Setup & Test (Chạy 1 lần)
```bash
# 1. Setup database
python scripts/setup_sqlserver.py

# 2. Test connection
python backend/test_sqlserver_connection.py
```

### Development (Chạy mỗi lần dev)
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 🔧 Nếu Gặp Lỗi

### Lỗi 1: "ODBC Driver not found"
```bash
# Download & install ODBC Driver 17
# Link: https://go.microsoft.com/fwlink/?linkid=2249004
# Sau đó restart terminal và chạy lại
```

### Lỗi 2: "Cannot open database"
```sql
-- Trong SQL Server Management Studio
CREATE DATABASE NongNghiepAI;
GO
```

### Lỗi 3: "Login failed"
**Option A - Windows Auth (Recommended):**
```env
# File .env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Option B - Named Instance:**
```env
# File .env (nếu dùng SQLEXPRESS)
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Option C - SQL Auth:**
```env
# File .env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

---

## 📚 Documentation

Nếu cần thêm thông tin:

### Quick Start
- **QUICK_START_SQLSERVER.md** - 3 bước đơn giản

### Full Guide
- **SQLSERVER_COMPLETE_GUIDE.md** - Hướng dẫn đầy đủ
- **README_SQLSERVER.md** - Overview & reference

### Technical Details
- **SQLSERVER_CONVERSION_SUMMARY.md** - Chi tiết chuyển đổi
- **CONVERSION_CHECKLIST.md** - 24 files converted

---

## 🎯 Timeline Dự Kiến

### Lần Đầu Setup (15-20 phút)
1. ✅ Kiểm tra SQL Server (2 phút)
2. ✅ Cài ODBC Driver nếu cần (5 phút)
3. ✅ Cài Python dependencies (3 phút)
4. ✅ Chạy setup script (2 phút)
5. ✅ Test connection (1 phút)
6. ✅ Start backend (2 phút)
7. ✅ Start frontend (5 phút)

### Lần Sau (2 phút)
1. ✅ Start backend (1 phút)
2. ✅ Start frontend (1 phút)

---

## ✨ Sau Khi Setup Xong

Bạn sẽ có:
- ✅ Database NongNghiepAI với 8 tables
- ✅ 86 records seed data
- ✅ 3 stored procedures
- ✅ Backend API running on port 8000
- ✅ Frontend UI running on port 5173
- ✅ Full AgriAI system ready to use!

---

## 🚀 Ready to Start?

### Bước 1: Chạy Setup
```bash
python scripts/setup_sqlserver.py
```

### Bước 2: Test
```bash
python backend/test_sqlserver_connection.py
```

### Bước 3: Start
```bash
# Terminal 1
cd backend && uvicorn app.main:app --reload

# Terminal 2
cd frontend && npm run dev
```

---

## 📞 Cần Hỗ Trợ?

1. Kiểm tra file `.env` - connection string đúng chưa?
2. Kiểm tra SQL Server đang chạy chưa?
3. Kiểm tra ODBC Driver đã cài chưa?
4. Xem logs trong terminal
5. Đọc `SQLSERVER_COMPLETE_GUIDE.md` để biết chi tiết

---

**Good luck! 🎉 Chúc bạn thành công với AgriAI!**
