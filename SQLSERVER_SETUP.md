# 🗄️ SQL Server Setup Guide

## Kết nối với SQL Server

Dự án AgriAI đã được cấu hình để kết nối với SQL Server database **NongNghiepAI**.

## Yêu cầu

1. **SQL Server** đã cài đặt và đang chạy
2. **ODBC Driver 17 for SQL Server** đã cài đặt
3. Database **NongNghiepAI** đã được tạo
4. Windows Authentication được bật

## Cài đặt ODBC Driver

### Windows
Download và cài đặt từ:
https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### Kiểm tra driver đã cài
```powershell
Get-OdbcDriver | Where-Object {$_.Name -like "*SQL Server*"}
```

## Cấu hình Database

### 1. Connection String

File `.env`:
```env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

### 2. Cấu trúc Database

Database **NongNghiepAI** cần có các tables:

- ✅ **Users** - Thông tin người dùng
- ✅ **CropTypes** - Loại cây trồng
- ✅ **MarketPrices** - Giá thị trường
- ✅ **PriceHistory** - Lịch sử giá
- ✅ **HarvestSchedule** - Lịch thu hoạch
- ✅ **QualityRecords** - Bản ghi chất lượng
- ✅ **AlertSubscriptions** - Đăng ký cảnh báo

### 3. Tạo Tables

Chạy các script SQL trong thư mục `data/tables/`:

```sql
-- Trong SQL Server Management Studio
USE NongNghiepAI;
GO

-- Chạy từng file:
-- 1. data/tables/Users.sql
-- 2. data/tables/CropTypes.sql
-- 3. data/tables/MarketPrices.sql
-- 4. data/tables/PriceHistory.sql
-- 5. data/tables/HarvestSchedule.sql
-- 6. data/tables/QualityRecords.sql
-- 7. data/tables/AlertSubscriptions.sql
```

### 4. Seed Data

Chạy seed data:

```sql
-- Seed crop types
-- data/seeds/seed_crop_types.sql

-- Seed market prices
-- data/seeds/seed_market_prices.sql

-- Seed regions
-- data/seeds/seed_regions.sql
```

## Test Connection

### 1. Cài đặt dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test kết nối

```bash
python test_sqlserver_connection.py
```

Kết quả mong đợi:
```
==================================================
SQL Server Connection Test
Database: NongNghiepAI
==================================================
Testing pyodbc connection...
✓ pyodbc connection successful!
SQL Server version: Microsoft SQL Server 2019...

✓ Found 7 tables:
  - AlertSubscriptions
  - CropTypes
  - HarvestSchedule
  - MarketPrices
  - PriceHistory
  - QualityRecords
  - Users

==================================================
Testing SQLAlchemy connection...
✓ SQLAlchemy connection successful!

==================================================
Checking required tables...
✓ Users: exists (0 rows)
✓ CropTypes: exists (0 rows)
✓ MarketPrices: exists (0 rows)
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

## Khởi động Backend

```bash
cd backend
uvicorn app.main:app --reload
```

Truy cập:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## Troubleshooting

### Lỗi: "Data source name not found"

**Giải pháp:** Cài đặt ODBC Driver 17 for SQL Server

### Lỗi: "Login failed for user"

**Giải pháp:** 
1. Kiểm tra SQL Server Authentication mode
2. Đảm bảo Windows Authentication được bật
3. User hiện tại có quyền truy cập database

### Lỗi: "Cannot open database"

**Giải pháp:**
1. Kiểm tra database NongNghiepAI đã được tạo
2. Kiểm tra tên database trong connection string

### Kiểm tra SQL Server đang chạy

```powershell
Get-Service | Where-Object {$_.Name -like "*SQL*"}
```

### Kiểm tra databases

```sql
SELECT name FROM sys.databases;
```

## Connection String Options

### Windows Authentication (Recommended)
```
mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

### SQL Server Authentication
```
mssql+pyodbc://username:password@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

### Named Instance
```
mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

## Lưu ý

1. **Backup database** trước khi chạy scripts
2. **Kiểm tra quyền** của user trên database
3. **Firewall** có thể block connection
4. **SQL Server Browser** service cần chạy nếu dùng named instance

## Next Steps

Sau khi kết nối thành công:

1. ✅ Chạy seed data
2. ✅ Test API endpoints
3. ✅ Khởi động frontend
4. ✅ Test toàn bộ hệ thống

---

**Cần hỗ trợ?** Xem logs trong SQL Server Management Studio hoặc check file `backend/app.log`
