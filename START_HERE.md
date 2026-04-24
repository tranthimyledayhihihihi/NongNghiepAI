# 🚀 BẮT ĐẦU NHANH - AgriAI

## ✅ ĐÃ CẤU HÌNH

Connection đã được cấu hình cho SQL Server của bạn:

- **Server:** `DESKTOP-7T57RI\SQLEXPRESS02`
- **Database:** `NongNghiepAI`
- **User:** `sa`
- **Password:** `123`

## 📋 CÁC BƯỚC THỰC HIỆN

### Bước 1: Chạy SQL Script (Trong SSMS)

Bạn đã có SQL script hoàn chỉnh. Chạy nó trong SQL Server Management Studio:

1. Mở SSMS
2. Kết nối đến `DESKTOP-7T57RI\SQLEXPRESS02`
3. Copy toàn bộ SQL script của bạn (file bạn đã gửi)
4. Execute (F5)

**SQL Script sẽ tạo:**
- ✅ Database `NongNghiepAI`
- ✅ 7 tables (Users, CropTypes, HarvestSchedule, MarketPrices, PriceHistory, QualityRecords, AlertSubscriptions)
- ✅ 3 crop types mẫu (Lúa, Cà phê, Sầu riêng)
- ✅ 1 user mẫu (Trần Thị Mỹ - tranthimy2205@gmail.com)
- ✅ 1 stored procedure (sp_GetPriceHistory)

### Bước 2: Test Connection

Mở terminal/cmd trong thư mục dự án:

```bash
python backend/test_sqlserver_connection.py
```

**Kết quả mong đợi:**
```
✓ pyodbc connection successful!
✓ SQLAlchemy connection successful!
✓ Found 7 tables
🎉 All tests passed!
```

### Bước 3: Cài Python Dependencies (Nếu chưa cài)

```bash
cd backend
pip install -r requirements.txt
```

### Bước 4: Start Backend

```bash
cd backend
uvicorn app.main:app --reload
```

**Kết quả mong đợi:**
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

### Bước 5: Test API

Mở browser: **http://localhost:8000/docs**

Test các endpoints:
- GET `/health` - Health check
- GET `/api/harvest/crops` - Lấy danh sách crops

### Bước 6: Start Frontend (Terminal mới)

```bash
cd frontend
npm install
npm run dev
```

Truy cập: **http://localhost:5173**

---

## 🔧 CONNECTION STRING

File `.env` đã được cấu hình:

```env
DATABASE_URL=mssql+pyodbc://sa:123@DESKTOP-7T57RI\SQLEXPRESS02/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

---

## 📊 KIỂM TRA DATABASE (Trong SSMS)

```sql
USE NongNghiepAI;
GO

-- Xem tất cả tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

-- Xem dữ liệu
SELECT * FROM CropTypes;      -- 3 crops
SELECT * FROM Users;          -- 1 user
SELECT * FROM MarketPrices;   -- 0 rows (chưa có data)
```

---

## ⚠️ NẾU GẶP LỖI

### Lỗi: "Login failed for user 'sa'"
**Giải pháp:** Kiểm tra password trong SSMS, đảm bảo là `123`

### Lỗi: "ODBC Driver not found"
**Giải pháp:** 
1. Download ODBC Driver 17: https://go.microsoft.com/fwlink/?linkid=2249004
2. Cài đặt
3. Restart terminal
4. Chạy lại test

### Lỗi: "Cannot open database 'NongNghiepAI'"
**Giải pháp:** Chạy SQL script trong SSMS để tạo database

---

## 🎯 QUICK COMMANDS

```bash
# Test connection
python backend/test_sqlserver_connection.py

# Start backend
cd backend
uvicorn app.main:app --reload

# Start frontend (terminal mới)
cd frontend
npm run dev
```

---

## 📚 TÀI LIỆU THAM KHẢO

- **USER_SCHEMA_GUIDE.md** - Hướng dẫn sử dụng schema của bạn
- **README.md** - Tổng quan dự án
- **API_DOCUMENTATION.md** - Chi tiết API endpoints

---

## ✅ CHECKLIST

- [ ] SQL script đã chạy trong SSMS
- [ ] Database `NongNghiepAI` đã tạo
- [ ] 7 tables đã tạo
- [ ] Test connection thành công
- [ ] Backend đã start
- [ ] API docs accessible (http://localhost:8000/docs)
- [ ] Frontend đã start
- [ ] App accessible (http://localhost:5173)

---

**Chúc bạn thành công! 🎉**

Nếu gặp vấn đề, hãy chạy test connection trước:
```bash
python backend/test_sqlserver_connection.py
```
