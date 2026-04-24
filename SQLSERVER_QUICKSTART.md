# 🚀 SQL Server Quick Start

## Bắt đầu nhanh với SQL Server

### Bước 1: Kiểm tra SQL Server

Mở SQL Server Management Studio và kết nối đến server của bạn.

### Bước 2: Tạo Database (nếu chưa có)

```sql
CREATE DATABASE NongNghiepAI;
GO

USE NongNghiepAI;
GO
```

### Bước 3: Cài đặt Python dependencies

```bash
cd backend
pip install pyodbc pymssql sqlalchemy
```

### Bước 4: Chạy setup script

```bash
python scripts/setup_sqlserver.py
```

Script này sẽ:
- ✅ Tạo tất cả tables
- ✅ Insert seed data
- ✅ Tạo stored procedures
- ✅ Verify setup

### Bước 5: Test kết nối

```bash
python backend/test_sqlserver_connection.py
```

Kết quả mong đợi:
```
✓ pyodbc connection successful!
✓ SQLAlchemy connection successful!
✓ All tables exist
🎉 All tests passed!
```

### Bước 6: Khởi động Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### Bước 7: Test API

Mở browser: http://localhost:8000/docs

Test endpoints:
- GET `/health` - Health check
- GET `/api/quality/grades` - Quality grades
- POST `/api/pricing/current` - Current price

### Bước 8: Khởi động Frontend

```bash
cd frontend
npm install
npm run dev
```

Truy cập: http://localhost:5173

## Troubleshooting

### Lỗi: "ODBC Driver not found"

**Cài đặt ODBC Driver 17:**
1. Download: https://go.microsoft.com/fwlink/?linkid=2249004
2. Chạy installer
3. Restart terminal

### Lỗi: "Cannot open database"

**Kiểm tra:**
```sql
-- Trong SSMS
SELECT name FROM sys.databases WHERE name = 'NongNghiepAI';
```

Nếu không có, tạo database:
```sql
CREATE DATABASE NongNghiepAI;
```

### Lỗi: "Login failed"

**Kiểm tra quyền:**
```sql
-- Trong SSMS
USE NongNghiepAI;
GO

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO [YourWindowsUser];
GO
```

## Connection String

Trong file `.env`:

```env
# Windows Authentication (Recommended)
DATABASE_URL=mssql+pyodbc://localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# SQL Server Authentication
# DATABASE_URL=mssql+pyodbc://sa:YourPassword@localhost/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server

# Named Instance
# DATABASE_URL=mssql+pyodbc://localhost\\SQLEXPRESS/NongNghiepAI?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes
```

## Verify Tables

```sql
USE NongNghiepAI;
GO

-- List all tables
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;

-- Check row counts
SELECT 
    t.NAME AS TableName,
    p.rows AS RowCounts
FROM 
    sys.tables t
INNER JOIN      
    sys.partitions p ON t.object_id = p.OBJECT_ID
WHERE 
    t.is_ms_shipped = 0
    AND p.index_id IN (0,1)
GROUP BY 
    t.NAME, p.Rows
ORDER BY 
    t.NAME;
```

## Next Steps

1. ✅ Database setup complete
2. ✅ Backend running
3. ✅ Frontend running
4. 🎯 Start using AgriAI!

---

**Cần hỗ trợ thêm?** Xem [SQLSERVER_SETUP.md](SQLSERVER_SETUP.md) để biết chi tiết.
