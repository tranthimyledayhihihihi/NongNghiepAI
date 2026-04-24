# 📋 Tóm Tắt Chuyển Đổi SQL Server

## 🎯 Mục Tiêu
Chuyển đổi toàn bộ hệ thống AgriAI từ PostgreSQL sang SQL Server để tương thích với database **NongNghiepAI** của bạn.

## ✅ Đã Hoàn Thành

### 1. Database Schema (7 Tables)
Tất cả tables đã được chuyển đổi sang SQL Server syntax:

| File | Table Name | Columns | Status |
|------|-----------|---------|--------|
| `data/tables/Users.sql` | Users | 9 | ✅ |
| `data/tables/CropTypes.sql` | CropTypes | 5 | ✅ |
| `data/tables/MarketPrices.sql` | MarketPrices | 8 | ✅ |
| `data/tables/PriceHistory.sql` | PriceHistory | 7 | ✅ |
| `data/tables/HarvestSchedule.sql` | HarvestSchedule | 10 | ✅ |
| `data/tables/QualityRecords.sql` | QualityRecords | 8 | ✅ |
| `data/tables/AlertSubscriptions.sql` | AlertSubscriptions | 10 | ✅ |

### 2. Seed Data (3 Files)
| File | Description | Records | Status |
|------|-------------|---------|--------|
| `data/seeds/seed_crop_types.sql` | 10 loại cây trồng | 10 | ✅ |
| `data/seeds/seed_regions.sql` | 63 tỉnh/thành VN + table Regions | 63 | ✅ |
| `data/seeds/seed_market_prices.sql` | Giá mẫu 5 loại rau | 13 | ✅ |

### 3. Stored Procedures (3 Files)
| File | Procedure Name | Purpose | Status |
|------|---------------|---------|--------|
| `data/stored_procedures/sp_GetHarvestForecast.sql` | sp_GetHarvestForecast | Lấy dự báo thu hoạch | ✅ |
| `data/stored_procedures/sp_GetPriceHistory.sql` | sp_GetPriceHistory | Lấy lịch sử giá | ✅ |
| `data/stored_procedures/sp_UpdateMarketPrice.sql` | sp_UpdateMarketPrice | Cập nhật giá | ✅ |

### 4. Python Models (4 Files)
| File | Models | Status |
|------|--------|--------|
| `backend/app/models/user.py` | User | ✅ |
| `backend/app/models/crop.py` | CropType, HarvestSchedule, QualityRecord | ✅ |
| `backend/app/models/price.py` | MarketPrice, PriceHistory | ✅ |
| `backend/app/models/alert.py` | AlertSubscription | ✅ |

### 5. Configuration Files
| File | Purpose | Status |
|------|---------|--------|
| `backend/app/core/config.py` | SQL Server connection | ✅ |
| `.env` | Environment variables | ✅ |
| `backend/requirements.txt` | Python dependencies | ✅ |

### 6. Scripts & Tools
| File | Purpose | Status |
|------|---------|--------|
| `scripts/setup_sqlserver.py` | Auto setup database | ✅ |
| `backend/test_sqlserver_connection.py` | Test connection | ✅ |

### 7. Documentation
| File | Purpose | Status |
|------|---------|--------|
| `SQLSERVER_COMPLETE_GUIDE.md` | Hướng dẫn đầy đủ | ✅ |
| `SQLSERVER_QUICKSTART.md` | Quick start guide | ✅ |
| `SQLSERVER_SETUP.md` | Setup guide | ✅ |

## 🔄 Thay Đổi Chính

### Syntax Conversion

#### PostgreSQL → SQL Server

**Table Creation:**
```sql
-- PostgreSQL
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE
);

-- SQL Server
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]'))
BEGIN
    CREATE TABLE [dbo].[Users] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [Email] NVARCHAR(255),
        [IsActive] BIT DEFAULT 1
    );
END
GO
```

**Data Types:**
- `SERIAL` → `INT IDENTITY(1,1)`
- `BOOLEAN` → `BIT`
- `VARCHAR` → `NVARCHAR` (Unicode support)
- `TIMESTAMP WITH TIME ZONE` → `DATETIME2`
- `TEXT[]` → `NVARCHAR(MAX)` (JSON string)
- `CURRENT_TIMESTAMP` → `GETDATE()`
- `CURRENT_DATE` → `CAST(GETDATE() AS DATE)`

**Insert with Conflict:**
```sql
-- PostgreSQL
INSERT INTO crop_types (name, category) VALUES ('Cà chua', 'vegetable')
ON CONFLICT (name) DO NOTHING;

-- SQL Server
MERGE INTO CropTypes AS target
USING (VALUES ('Cà chua', 'vegetable')) AS source (Name, Category)
ON target.Name = source.Name
WHEN NOT MATCHED THEN
    INSERT (Name, Category) VALUES (source.Name, source.Category);
GO
```

**Stored Procedures:**
```sql
-- PostgreSQL
CREATE OR REPLACE FUNCTION sp_GetPriceHistory(...)
RETURNS TABLE (...) AS $$
BEGIN
    RETURN QUERY SELECT ...;
END;
$$ LANGUAGE plpgsql;

-- SQL Server
CREATE PROCEDURE sp_GetPriceHistory
    @CropName NVARCHAR(100),
    @Region NVARCHAR(100)
AS
BEGIN
    SET NOCOUNT ON;
    SELECT ...;
END
GO
```

### Naming Convention

**Tables:** PascalCase
- `users` → `Users`
- `crop_types` → `CropTypes`
- `market_prices` → `MarketPrices`

**Columns:** PascalCase
- `crop_name` → `CropName`
- `price_per_kg` → `PricePerKg`
- `is_active` → `IsActive`
- `created_at` → `CreatedAt`

### Python Models

**SQLAlchemy Models với PascalCase:**
```python
class MarketPrice(Base):
    __tablename__ = "MarketPrices"
    
    Id = Column("Id", Integer, primary_key=True)
    CropName = Column("CropName", String(100))
    PricePerKg = Column("PricePerKg", Numeric(10, 2))
    
    # Backward compatibility aliases
    @property
    def id(self):
        return self.Id
    
    @property
    def crop_name(self):
        return self.CropName
```

## 📊 Database Structure

```
NongNghiepAI Database
│
├── Users (9 columns)
│   ├── Id (PK)
│   ├── Email (Unique)
│   ├── Phone
│   ├── FullName
│   ├── HashedPassword
│   ├── IsActive
│   ├── IsVerified
│   ├── CreatedAt
│   └── UpdatedAt
│
├── CropTypes (5 columns)
│   ├── Id (PK)
│   ├── Name (Unique)
│   ├── NameEn
│   ├── Category
│   ├── AvgGrowthDays
│   └── CreatedAt
│
├── MarketPrices (8 columns)
│   ├── Id (PK)
│   ├── CropName
│   ├── Region
│   ├── PricePerKg
│   ├── QualityGrade
│   ├── MarketType
│   ├── Source
│   ├── Date
│   └── CreatedAt
│
├── PriceHistory (7 columns)
│   ├── Id (PK)
│   ├── CropName
│   ├── Region
│   ├── AvgPrice
│   ├── MinPrice
│   ├── MaxPrice
│   ├── Date
│   └── CreatedAt
│
├── HarvestSchedule (10 columns)
│   ├── Id (PK)
│   ├── CropTypeId (FK → CropTypes)
│   ├── Region
│   ├── PlantingDate
│   ├── PredictedHarvestDate
│   ├── ActualHarvestDate
│   ├── QuantityKg
│   ├── Notes
│   ├── CreatedAt
│   └── UpdatedAt
│
├── QualityRecords (8 columns)
│   ├── Id (PK)
│   ├── UserId (FK → Users)
│   ├── CropType
│   ├── QualityGrade
│   ├── Confidence
│   ├── DefectCount
│   ├── Defects (JSON)
│   ├── ImagePath
│   └── CreatedAt
│
├── AlertSubscriptions (10 columns)
│   ├── Id (PK)
│   ├── UserId (FK → Users)
│   ├── CropName
│   ├── Region
│   ├── PriceChangeThreshold
│   ├── NotifyMethod
│   ├── Contact
│   ├── IsActive
│   ├── CreatedAt
│   └── UpdatedAt
│
└── Regions (4 columns)
    ├── Id (PK)
    ├── Name (Unique)
    ├── Code
    ├── Type
    └── CreatedAt
```

## 🚀 Cách Sử Dụng

### Bước 1: Setup Database
```bash
python scripts/setup_sqlserver.py
```

### Bước 2: Test Connection
```bash
python backend/test_sqlserver_connection.py
```

### Bước 3: Start Backend
```bash
cd backend
uvicorn app.main:app --reload
```

### Bước 4: Start Frontend
```bash
cd frontend
npm run dev
```

## 📝 Connection String

**Current (Windows Authentication):**
```
mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**Alternatives:**

**Named Instance:**
```
mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

**SQL Authentication:**
```
mssql+pyodbc://sa:password@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server
```

## ✅ Verification Checklist

- [ ] SQL Server đang chạy
- [ ] Database NongNghiepAI đã tạo
- [ ] ODBC Driver 17 đã cài
- [ ] Python dependencies đã cài (`pip install -r requirements.txt`)
- [ ] Setup script chạy thành công
- [ ] Test connection pass
- [ ] Backend khởi động OK
- [ ] API docs accessible (http://localhost:8000/docs)
- [ ] Frontend khởi động OK
- [ ] App accessible (http://localhost:5173)

## 🎯 Expected Results

### After Setup Script:
```
✅ Database setup completed successfully!
✓ Found 8 tables
✓ CropTypes: 10 rows
✓ Regions: 63 rows
✓ MarketPrices: 13 rows
```

### After Test Connection:
```
🎉 All tests passed! Ready to use SQL Server.
✓ pyodbc connection: OK
✓ SQLAlchemy connection: OK
✓ Tables check: OK
```

### After Backend Start:
```
INFO: Uvicorn running on http://127.0.0.1:8000
INFO: Application startup complete.
```

## 📚 Documentation

Xem chi tiết tại:
- **SQLSERVER_COMPLETE_GUIDE.md** - Hướng dẫn đầy đủ
- **SQLSERVER_QUICKSTART.md** - Quick start
- **SQLSERVER_SETUP.md** - Setup guide

---

**Status: ✅ READY TO USE**

Tất cả files đã được chuyển đổi và sẵn sàng sử dụng với SQL Server!
