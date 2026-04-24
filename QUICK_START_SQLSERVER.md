# ⚡ Quick Start - SQL Server Setup

## 🎯 3 Bước Đơn Giản

### 1️⃣ Setup Database (1 phút)
```bash
python scripts/setup_sqlserver.py
```
✅ Tạo 8 tables + 86 records seed data + 3 stored procedures

### 2️⃣ Test Connection (30 giây)
```bash
python backend/test_sqlserver_connection.py
```
✅ Kiểm tra kết nối pyodbc + SQLAlchemy

### 3️⃣ Start Application (1 phút)
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```
✅ Backend: http://localhost:8000/docs
✅ Frontend: http://localhost:5173

---

## 🔧 Nếu Gặp Lỗi

### ❌ "ODBC Driver not found"
**Download & Install:**
https://go.microsoft.com/fwlink/?linkid=2249004

### ❌ "Cannot open database"
**Tạo database trong SSMS:**
```sql
CREATE DATABASE NongNghiepAI;
GO
```

### ❌ "Login failed"
**Kiểm tra connection string trong `.env`:**

**Windows Auth (Recommended):**
```env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Named Instance (SQLEXPRESS):**
```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Auth:**
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

---

## 📊 Kiểm Tra Dữ Liệu (SSMS)

```sql
USE NongNghiepAI;
GO

-- Xem tất cả tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

-- Xem dữ liệu
SELECT * FROM CropTypes;      -- 10 loại cây trồng
SELECT * FROM Regions;        -- 63 tỉnh/thành
SELECT * FROM MarketPrices;   -- 13 giá mẫu
```

---

## ✅ Expected Output

### Setup Script:
```
✅ Database setup completed successfully!
✓ Found 8 tables:
  - CropTypes: 5 columns, 10 rows
  - Regions: 4 columns, 63 rows
  - MarketPrices: 8 columns, 13 rows
  - Users: 9 columns, 0 rows
  - HarvestSchedule: 10 columns, 0 rows
  - QualityRecords: 8 columns, 0 rows
  - PriceHistory: 7 columns, 0 rows
  - AlertSubscriptions: 10 columns, 0 rows
```

### Test Connection:
```
🎉 All tests passed! Ready to use SQL Server.
pyodbc connection: ✓ OK
SQLAlchemy connection: ✓ OK
Tables check: ✓ OK
```

### Backend Start:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

---

## 🎯 Test API

**Open:** http://localhost:8000/docs

**Try:**
1. GET `/health` → `{"status": "healthy"}`
2. GET `/api/harvest/crops` → List 10 crops
3. POST `/api/pricing/current` → Get price

---

## 📚 Full Documentation

- **SQLSERVER_COMPLETE_GUIDE.md** - Hướng dẫn chi tiết
- **SQLSERVER_CONVERSION_SUMMARY.md** - Tóm tắt chuyển đổi

---

**That's it! 🚀 Chỉ 3 bước và bạn đã sẵn sàng!**
