# 🎯 Hướng Dẫn Hoàn Chỉnh SQL Server - AgriAI

## ✅ Đã Hoàn Thành

Tất cả các file đã được chuyển đổi từ PostgreSQL sang SQL Server:

### 📊 Database Tables (7 tables)
- ✅ `Users.sql` - Bảng người dùng
- ✅ `CropTypes.sql` - Bảng loại cây trồng
- ✅ `MarketPrices.sql` - Bảng giá thị trường
- ✅ `PriceHistory.sql` - Bảng lịch sử giá
- ✅ `HarvestSchedule.sql` - Bảng lịch thu hoạch
- ✅ `QualityRecords.sql` - Bảng kiểm tra chất lượng
- ✅ `AlertSubscriptions.sql` - Bảng đăng ký cảnh báo

### 🌱 Seed Data (3 files)
- ✅ `seed_crop_types.sql` - Dữ liệu mẫu cây trồng (10 loại)
- ✅ `seed_regions.sql` - Dữ liệu tỉnh thành (63 tỉnh/thành)
- ✅ `seed_market_prices.sql` - Dữ liệu giá mẫu

### 🔧 Stored Procedures (3 procedures)
- ✅ `sp_GetHarvestForecast` - Lấy dự báo thu hoạch
- ✅ `sp_GetPriceHistory` - Lấy lịch sử giá
- ✅ `sp_UpdateMarketPrice` - Cập nhật giá thị trường

### 🐍 Python Models (4 files)
- ✅ `user.py` - User model với PascalCase columns
- ✅ `crop.py` - CropType, HarvestSchedule, QualityRecord models
- ✅ `price.py` - MarketPrice, PriceHistory models
- ✅ `alert.py` - AlertSubscription model

## 🚀 Các Bước Thực Hiện

### Bước 1: Kiểm Tra SQL Server

Mở **SQL Server Management Studio** và kết nối đến server của bạn.

Kiểm tra database đã tồn tại:
```sql
SELECT name FROM sys.databases WHERE name = 'NongNghiepAI';
```

Nếu chưa có, tạo database:
```sql
CREATE DATABASE NongNghiepAI;
GO
```

### Bước 2: Cài Đặt Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Các package quan trọng:
- `pyodbc` - SQL Server driver
- `pymssql` - Alternative SQL Server driver
- `sqlalchemy` - ORM

### Bước 3: Kiểm Tra ODBC Driver

Chạy lệnh sau để kiểm tra ODBC Driver đã cài:

**Windows PowerShell:**
```powershell
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
```

**Hoặc kiểm tra thủ công:**
1. Mở "ODBC Data Sources (64-bit)" từ Start Menu
2. Tab "Drivers"
3. Tìm "ODBC Driver 17 for SQL Server"

**Nếu chưa có, download và cài đặt:**
https://go.microsoft.com/fwlink/?linkid=2249004

### Bước 4: Cấu Hình Connection String

File `.env` đã được cấu hình sẵn:

```env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Các trường hợp khác:**

**Named Instance (ví dụ: SQLEXPRESS):**
```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Server Authentication:**
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

**Remote Server:**
```env
DATABASE_URL=mssql+pyodbc://192.168.1.100/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

### Bước 5: Chạy Setup Script

Script này sẽ tự động:
- Tạo tất cả 7 tables
- Insert seed data (cây trồng, tỉnh thành, giá mẫu)
- Tạo 3 stored procedures
- Verify setup

```bash
python scripts/setup_sqlserver.py
```

**Kết quả mong đợi:**
```
===========================================================
AgriAI - SQL Server Database Setup
===========================================================

✓ Connected to NongNghiepAI database

===========================================================
Step 1: Creating Tables
===========================================================
Executing: Users.sql
  ✓ Success
Executing: CropTypes.sql
  ✓ Success
...

===========================================================
Step 2: Inserting Seed Data
===========================================================
Executing: seed_crop_types.sql
  ✓ Success
...

===========================================================
Step 3: Creating Stored Procedures
===========================================================
Executing: sp_GetHarvestForecast.sql
  ✓ Success
...

===========================================================
Step 4: Verifying Setup
===========================================================

✓ Found 8 tables:
  - AlertSubscriptions: 7 columns, 0 rows
  - CropTypes: 5 columns, 10 rows
  - HarvestSchedule: 10 columns, 0 rows
  - MarketPrices: 8 columns, 13 rows
  - PriceHistory: 7 columns, 0 rows
  - QualityRecords: 8 columns, 0 rows
  - Regions: 4 columns, 63 rows
  - Users: 9 columns, 0 rows

===========================================================
✅ Database setup completed successfully!
===========================================================
```

### Bước 6: Test Connection

```bash
python backend/test_sqlserver_connection.py
```

**Kết quả mong đợi:**
```
==================================================
SQL Server Connection Test
Database: NongNghiepAI
==================================================
Testing pyodbc connection...
✓ pyodbc connection successful!
SQL Server version: Microsoft SQL Server 2019...

✓ Found 8 tables:
  - AlertSubscriptions
  - CropTypes
  - HarvestSchedule
  - MarketPrices
  - PriceHistory
  - QualityRecords
  - Regions
  - Users

==================================================
Testing SQLAlchemy connection...
✓ SQLAlchemy connection successful!

✓ Found 8 tables via SQLAlchemy

==================================================
Checking required tables...
✓ Users: exists (0 rows)
✓ CropTypes: exists (10 rows)
✓ MarketPrices: exists (13 rows)
✓ PriceHistory: exists (0 rows)
✓ HarvestSchedule: exists (0 rows)
✓ QualityRecords: exists (0 rows)
✓ AlertSubscriptions: exists (0 rows)

==================================================
SUMMARY
==================================================
pyodbc connection: ✓ OK
SQLAlchemy connection: ✓ OK
Tables check: ✓ OK

🎉 All tests passed! Ready to use SQL Server.
```

### Bước 7: Khởi Động Backend

```bash
cd backend
uvicorn app.main:app --reload
```

**Kết quả mong đợi:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Bước 8: Test API

Mở browser: **http://localhost:8000/docs**

Test các endpoints:

1. **Health Check**
   - GET `/health`
   - Response: `{"status": "healthy"}`

2. **Get Crop Types**
   - GET `/api/harvest/crops`
   - Response: Danh sách 10 loại cây trồng

3. **Get Current Price**
   - POST `/api/pricing/current`
   - Body:
     ```json
     {
       "crop_name": "Cà chua",
       "region": "Hà Nội"
     }
     ```
   - Response: Giá hiện tại của cà chua tại Hà Nội

4. **Quality Check**
   - POST `/api/quality/check`
   - Upload ảnh nông sản
   - Response: Kết quả phân loại chất lượng

### Bước 9: Khởi Động Frontend

```bash
cd frontend
npm install
npm run dev
```

Truy cập: **http://localhost:5173**

## 🔍 Kiểm Tra Dữ Liệu Trong SSMS

### Xem tất cả tables:
```sql
USE NongNghiepAI;
GO

SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
```

### Xem dữ liệu cây trồng:
```sql
SELECT * FROM CropTypes;
```

### Xem dữ liệu giá:
```sql
SELECT * FROM MarketPrices;
```

### Xem tỉnh thành:
```sql
SELECT * FROM Regions;
```

### Test stored procedure:
```sql
-- Get price history
EXEC sp_GetPriceHistory 
    @CropName = N'Cà chua',
    @Region = N'Hà Nội',
    @Days = 30;
```

## ⚠️ Troubleshooting

### Lỗi: "ODBC Driver not found"

**Giải pháp:**
1. Download ODBC Driver 17: https://go.microsoft.com/fwlink/?linkid=2249004
2. Chạy installer
3. Restart terminal/IDE
4. Chạy lại test

### Lỗi: "Cannot open database 'NongNghiepAI'"

**Giải pháp:**
```sql
-- Trong SSMS
CREATE DATABASE NongNghiepAI;
GO
```

### Lỗi: "Login failed for user"

**Giải pháp 1 - Windows Authentication:**
```sql
USE NongNghiepAI;
GO

-- Grant permissions to your Windows user
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [YourDomain\YourUsername];
GO
```

**Giải pháp 2 - SQL Server Authentication:**
Đổi connection string trong `.env`:
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

### Lỗi: "Named Pipes Provider: Could not open a connection"

**Giải pháp:**
1. Mở SQL Server Configuration Manager
2. SQL Server Network Configuration > Protocols for [Instance]
3. Enable "TCP/IP" và "Named Pipes"
4. Restart SQL Server service

### Lỗi: "Table already exists"

**Giải pháp:**
Script đã có logic kiểm tra `IF NOT EXISTS`, nhưng nếu vẫn lỗi:

```sql
-- Drop all tables (CẢNH BÁO: Mất hết dữ liệu!)
USE NongNghiepAI;
GO

DROP TABLE IF EXISTS AlertSubscriptions;
DROP TABLE IF EXISTS QualityRecords;
DROP TABLE IF EXISTS HarvestSchedule;
DROP TABLE IF EXISTS PriceHistory;
DROP TABLE IF EXISTS MarketPrices;
DROP TABLE IF EXISTS CropTypes;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Regions;
GO

-- Sau đó chạy lại setup script
```

## 📝 Thay Đổi Quan Trọng

### 1. Table Names: PascalCase
- PostgreSQL: `crop_types` → SQL Server: `CropTypes`
- PostgreSQL: `market_prices` → SQL Server: `MarketPrices`

### 2. Column Names: PascalCase
- PostgreSQL: `crop_name` → SQL Server: `CropName`
- PostgreSQL: `price_per_kg` → SQL Server: `PricePerKg`

### 3. Data Types
- PostgreSQL: `SERIAL` → SQL Server: `IDENTITY(1,1)`
- PostgreSQL: `BOOLEAN` → SQL Server: `BIT`
- PostgreSQL: `TIMESTAMP WITH TIME ZONE` → SQL Server: `DATETIME2`
- PostgreSQL: `TEXT[]` → SQL Server: `NVARCHAR(MAX)` (JSON string)

### 4. Python Models
- Tất cả models đã được cập nhật với PascalCase columns
- Có property aliases để backward compatibility
- Ví dụ: `model.Id` hoặc `model.id` đều hoạt động

## ✅ Checklist Hoàn Thành

- [x] Chuyển đổi 7 table definitions sang SQL Server
- [x] Chuyển đổi 3 seed data files
- [x] Chuyển đổi 3 stored procedures
- [x] Cập nhật 4 Python models
- [x] Cập nhật connection string
- [x] Tạo setup script
- [x] Tạo test script
- [x] Tạo documentation

## 🎯 Next Steps

1. ✅ Chạy `python scripts/setup_sqlserver.py`
2. ✅ Chạy `python backend/test_sqlserver_connection.py`
3. ✅ Khởi động backend: `uvicorn app.main:app --reload`
4. ✅ Test API tại http://localhost:8000/docs
5. ✅ Khởi động frontend: `npm run dev`
6. ✅ Truy cập app tại http://localhost:5173

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra SQL Server đang chạy
2. Kiểm tra ODBC Driver đã cài
3. Kiểm tra connection string trong `.env`
4. Xem logs trong terminal
5. Kiểm tra permissions trong SQL Server

---

**Chúc bạn thành công! 🎉**
