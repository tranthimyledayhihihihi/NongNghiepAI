# 🗄️ AgriAI - SQL Server Setup

## 📌 Tổng Quan

Dự án AgriAI đã được chuyển đổi hoàn toàn để sử dụng **SQL Server** thay vì PostgreSQL.

**Database Name:** `NongNghiepAI`

## 🚀 Quick Start (3 Bước)

### Bước 1: Setup Database
```bash
python scripts/setup_sqlserver.py
```

### Bước 2: Test Connection
```bash
python backend/test_sqlserver_connection.py
```

### Bước 3: Start Application
```bash
# Backend
cd backend
uvicorn app.main:app --reload

# Frontend (terminal mới)
cd frontend
npm run dev
```

## 📁 Cấu Trúc Database

### Tables (8)
1. **Users** - Người dùng hệ thống
2. **CropTypes** - Loại cây trồng (10 loại mẫu)
3. **Regions** - Tỉnh/thành VN (63 tỉnh)
4. **MarketPrices** - Giá thị trường hiện tại
5. **PriceHistory** - Lịch sử giá theo ngày
6. **HarvestSchedule** - Lịch thu hoạch
7. **QualityRecords** - Kết quả kiểm tra chất lượng
8. **AlertSubscriptions** - Đăng ký cảnh báo giá

### Stored Procedures (3)
1. **sp_GetHarvestForecast** - Lấy dự báo thu hoạch
2. **sp_GetPriceHistory** - Lấy lịch sử giá
3. **sp_UpdateMarketPrice** - Cập nhật giá thị trường

### Seed Data (86 records)
- 10 loại cây trồng (Cà chua, Dưa chuột, Rau muống, etc.)
- 63 tỉnh/thành Việt Nam
- 13 giá mẫu cho 5 loại rau

## 🔧 Cấu Hình

### Connection String

**File:** `.env`

**Windows Authentication (Recommended):**
```env
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Named Instance (SQLEXPRESS):**
```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Server Authentication:**
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

### Requirements

**Python Packages:**
```
pyodbc==5.0.1
pymssql==2.2.11
sqlalchemy==2.0.25
```

**ODBC Driver:**
- ODBC Driver 17 for SQL Server
- Download: https://go.microsoft.com/fwlink/?linkid=2249004

## 📊 Database Schema

```
Users
├── Id (PK)
├── Email (Unique)
├── Phone
├── FullName
├── HashedPassword
├── IsActive
├── IsVerified
├── CreatedAt
└── UpdatedAt

CropTypes
├── Id (PK)
├── Name (Unique)
├── NameEn
├── Category
├── AvgGrowthDays
└── CreatedAt

MarketPrices
├── Id (PK)
├── CropName
├── Region
├── PricePerKg
├── QualityGrade
├── MarketType
├── Source
├── Date
└── CreatedAt

HarvestSchedule
├── Id (PK)
├── CropTypeId (FK → CropTypes)
├── Region
├── PlantingDate
├── PredictedHarvestDate
├── ActualHarvestDate
├── QuantityKg
├── Notes
├── CreatedAt
└── UpdatedAt

QualityRecords
├── Id (PK)
├── UserId (FK → Users)
├── CropType
├── QualityGrade
├── Confidence
├── DefectCount
├── Defects (JSON)
├── ImagePath
└── CreatedAt

AlertSubscriptions
├── Id (PK)
├── UserId (FK → Users)
├── CropName
├── Region
├── PriceChangeThreshold
├── NotifyMethod
├── Contact
├── IsActive
├── CreatedAt
└── UpdatedAt
```

## 🛠️ Scripts & Tools

### Setup Script
**File:** `scripts/setup_sqlserver.py`

**Chức năng:**
- Tạo tất cả 8 tables
- Insert seed data (86 records)
- Tạo 3 stored procedures
- Verify setup

**Usage:**
```bash
python scripts/setup_sqlserver.py
```

### Test Script
**File:** `backend/test_sqlserver_connection.py`

**Chức năng:**
- Test pyodbc connection
- Test SQLAlchemy connection
- Check all tables exist
- Count rows in each table

**Usage:**
```bash
python backend/test_sqlserver_connection.py
```

## 📚 Documentation

### Main Guides
1. **QUICK_START_SQLSERVER.md** - 3-step quick start
2. **SQLSERVER_COMPLETE_GUIDE.md** - Full setup guide
3. **SQLSERVER_CONVERSION_SUMMARY.md** - Conversion details
4. **CONVERSION_CHECKLIST.md** - 24 files converted

### Reference
- **SQLSERVER_QUICKSTART.md** - Quick reference
- **SQLSERVER_SETUP.md** - Setup instructions

## ⚠️ Common Issues

### Issue 1: ODBC Driver Not Found
**Error:** `[Microsoft][ODBC Driver Manager] Data source name not found`

**Solution:**
1. Download ODBC Driver 17: https://go.microsoft.com/fwlink/?linkid=2249004
2. Install
3. Restart terminal
4. Run test again

### Issue 2: Cannot Open Database
**Error:** `Cannot open database "NongNghiepAI"`

**Solution:**
```sql
-- In SQL Server Management Studio
CREATE DATABASE NongNghiepAI;
GO
```

### Issue 3: Login Failed
**Error:** `Login failed for user`

**Solution 1 - Windows Auth:**
```sql
USE NongNghiepAI;
GO
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [YourDomain\YourUser];
GO
```

**Solution 2 - SQL Auth:**
Update `.env`:
```env
DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

### Issue 4: Named Instance
**Error:** Connection timeout

**Solution:**
Update `.env` with instance name:
```env
DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

## ✅ Verification

### Check Database in SSMS
```sql
USE NongNghiepAI;
GO

-- List all tables
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Check data
SELECT COUNT(*) FROM CropTypes;      -- Should be 10
SELECT COUNT(*) FROM Regions;        -- Should be 63
SELECT COUNT(*) FROM MarketPrices;   -- Should be 13

-- Test stored procedure
EXEC sp_GetPriceHistory 
    @CropName = N'Cà chua',
    @Region = N'Hà Nội',
    @Days = 30;
```

### Check Backend API
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Open browser
http://localhost:8000/docs

# Test endpoints
GET /health
GET /api/harvest/crops
POST /api/pricing/current
```

### Check Frontend
```bash
# Start frontend
cd frontend
npm run dev

# Open browser
http://localhost:5173
```

## 🎯 Expected Results

### After Setup:
```
✅ Database setup completed successfully!
✓ Found 8 tables:
  - CropTypes: 10 rows
  - Regions: 63 rows
  - MarketPrices: 13 rows
  - Users: 0 rows
  - HarvestSchedule: 0 rows
  - QualityRecords: 0 rows
  - PriceHistory: 0 rows
  - AlertSubscriptions: 0 rows
```

### After Test:
```
🎉 All tests passed! Ready to use SQL Server.
pyodbc connection: ✓ OK
SQLAlchemy connection: ✓ OK
Tables check: ✓ OK
```

### After Backend Start:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

## 🔄 Migration from PostgreSQL

All files have been converted:
- ✅ 7 table definitions
- ✅ 3 seed data files
- ✅ 3 stored procedures
- ✅ 4 Python models
- ✅ Configuration files
- ✅ Scripts & tools

**Key Changes:**
- `SERIAL` → `INT IDENTITY(1,1)`
- `BOOLEAN` → `BIT`
- `VARCHAR` → `NVARCHAR`
- `TIMESTAMP WITH TIME ZONE` → `DATETIME2`
- snake_case → PascalCase (tables & columns)

## 📞 Support

**Documentation:**
- See `SQLSERVER_COMPLETE_GUIDE.md` for detailed instructions
- See `CONVERSION_CHECKLIST.md` for conversion details

**Issues:**
- Check connection string in `.env`
- Verify ODBC Driver installed
- Check SQL Server is running
- Review logs in terminal

## 🎉 Ready to Use!

Database **NongNghiepAI** is ready with:
- ✅ 8 tables
- ✅ 86 seed records
- ✅ 3 stored procedures
- ✅ Python models
- ✅ API endpoints
- ✅ Frontend UI

**Start building your AgriAI application! 🚀**
