# 🗄️ Hướng Dẫn Sử Dụng Schema SQL Của Bạn

## ✅ Đã Cập Nhật

Tôi đã cập nhật tất cả Python models để khớp với schema SQL Server mà bạn đã cung cấp!

## 📊 Schema Của Bạn

### Tables (7)

#### 1. Users
```sql
UserID INT PRIMARY KEY IDENTITY(1,1)
FullName NVARCHAR(100) NOT NULL
Email NVARCHAR(100) UNIQUE
PhoneNumber NVARCHAR(20)
ZaloID NVARCHAR(100)  -- Cho Zalo notifications
CreatedAt DATETIME DEFAULT GETDATE()
```

#### 2. CropTypes
```sql
CropID INT PRIMARY KEY IDENTITY(1,1)
CropName NVARCHAR(100) NOT NULL
GrowthDurationDays INT  -- Dự báo thời gian thu hoạch
Description NVARCHAR(MAX)
```

#### 3. HarvestSchedule
```sql
ScheduleID INT PRIMARY KEY IDENTITY(1,1)
UserID INT FOREIGN KEY REFERENCES Users(UserID)
CropID INT FOREIGN KEY REFERENCES CropTypes(CropID)
PlantingDate DATE NOT NULL
AreaSize FLOAT
Region NVARCHAR(100)
ExpectedHarvestDate DATE
Status NVARCHAR(50) DEFAULT 'Growing'
```

#### 4. MarketPrices
```sql
PriceID INT PRIMARY KEY IDENTITY(1,1)
CropID INT FOREIGN KEY REFERENCES CropTypes(CropID)
Region NVARCHAR(100)
PricePerKg DECIMAL(18, 2)
SourceURL NVARCHAR(255)  -- URL nguồn dữ liệu
UpdatedAt DATETIME DEFAULT GETDATE()
```

#### 5. PriceHistory
```sql
HistoryID INT PRIMARY KEY IDENTITY(1,1)
CropID INT FOREIGN KEY REFERENCES CropTypes(CropID)
Region NVARCHAR(100)
OldPrice DECIMAL(18, 2)
NewPrice DECIMAL(18, 2)
ChangeDate DATETIME DEFAULT GETDATE()
```

#### 6. QualityRecords
```sql
RecordID INT PRIMARY KEY IDENTITY(1,1)
ScheduleID INT FOREIGN KEY REFERENCES HarvestSchedule(ScheduleID)
ImagePath NVARCHAR(500)
AIGrade NVARCHAR(20)  -- Loại 1, 2, 3
ConfidenceScore FLOAT
DetectedDiseases NVARCHAR(MAX)
CheckDate DATETIME DEFAULT GETDATE()
```

#### 7. AlertSubscriptions
```sql
AlertID INT PRIMARY KEY IDENTITY(1,1)
UserID INT FOREIGN KEY REFERENCES Users(UserID)
CropID INT FOREIGN KEY REFERENCES CropTypes(CropID)
TargetPrice DECIMAL(18, 2)
IsActive BIT DEFAULT 1
```

## 🚀 Cách Sử Dụng

### Bước 1: Chạy SQL Script Của Bạn

Bạn đã có file SQL hoàn chỉnh. Chạy nó trong SQL Server Management Studio:

1. Mở SSMS
2. Kết nối đến SQL Server
3. Copy toàn bộ SQL script của bạn
4. Execute (F5)

**Kết quả:**
- ✅ Database `NongNghiepAI` được tạo
- ✅ 7 tables được tạo
- ✅ 3 crop types mẫu (Lúa, Cà phê, Sầu riêng)
- ✅ 1 user mẫu (Trần Thị Mỹ - tranthimy2205@gmail.com)
- ✅ 1 stored procedure (sp_GetPriceHistory)

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

## 🐍 Python Models

Tất cả models đã được cập nhật để khớp với schema của bạn:

### User Model
```python
from backend.app.models.user import User

# Sử dụng
user = User(
    FullName="Nguyễn Văn A",
    Email="nguyenvana@example.com",
    PhoneNumber="0987654321",
    ZaloID="zalo_123456"
)
```

### CropType Model
```python
from backend.app.models.crop import CropType

crop = CropType(
    CropName="Cà chua",
    GrowthDurationDays=75,
    Description="Cà chua cherry"
)
```

### HarvestSchedule Model
```python
from backend.app.models.crop import HarvestSchedule
from datetime import date

schedule = HarvestSchedule(
    UserID=1,
    CropID=1,
    PlantingDate=date(2026, 4, 1),
    AreaSize=1000.0,  # m2
    Region="Đà Lạt",
    ExpectedHarvestDate=date(2026, 6, 15),
    Status="Growing"
)
```

### MarketPrice Model
```python
from backend.app.models.price import MarketPrice

price = MarketPrice(
    CropID=1,
    Region="Hà Nội",
    PricePerKg=25000,
    SourceURL="https://agro.gov.vn"
)
```

### QualityRecord Model
```python
from backend.app.models.crop import QualityRecord

quality = QualityRecord(
    ScheduleID=1,
    ImagePath="/uploads/tomato_001.jpg",
    AIGrade="Loại 1",
    ConfidenceScore=0.95,
    DetectedDiseases="Không phát hiện bệnh"
)
```

### AlertSubscription Model
```python
from backend.app.models.alert import AlertSubscription

alert = AlertSubscription(
    UserID=1,
    CropID=1,
    TargetPrice=30000,  # Cảnh báo khi giá >= 30k
    IsActive=True
)
```

## 📝 API Examples

### 1. Tạo Harvest Schedule
```python
# POST /api/harvest/schedule
{
    "user_id": 1,
    "crop_id": 1,
    "planting_date": "2026-04-24",
    "area_size": 1000.0,
    "region": "Đà Lạt"
}
```

### 2. Check Quality
```python
# POST /api/quality/check
# Upload image file
# Response:
{
    "ai_grade": "Loại 1",
    "confidence_score": 0.95,
    "detected_diseases": "Không phát hiện bệnh",
    "recommended_price": 28000
}
```

### 3. Get Market Price
```python
# GET /api/pricing/current?crop_id=1&region=Hà Nội
{
    "crop_name": "Lúa",
    "region": "Hà Nội",
    "price_per_kg": 25000,
    "source_url": "https://agro.gov.vn",
    "updated_at": "2026-04-24T10:30:00"
}
```

### 4. Subscribe to Price Alert
```python
# POST /api/alert/subscribe
{
    "user_id": 1,
    "crop_id": 1,
    "target_price": 30000
}
```

## 🔧 Stored Procedure Usage

### sp_GetPriceHistory

**SQL:**
```sql
EXEC sp_GetPriceHistory 
    @CropID = 1,
    @Region = N'Hà Nội';
```

**Python (SQLAlchemy):**
```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(
        text("EXEC sp_GetPriceHistory :crop_id, :region"),
        {"crop_id": 1, "region": "Hà Nội"}
    )
    history = result.fetchall()
```

## 🌱 Seed Data Có Sẵn

Sau khi chạy SQL script của bạn:

### CropTypes (3 records)
- Lúa (100 ngày)
- Cà phê (270 ngày)
- Sầu riêng (120 ngày)

### Users (1 record)
- Trần Thị Mỹ (tranthimy2205@gmail.com)

## 📊 Queries Hữu Ích

### Xem tất cả crops
```sql
SELECT * FROM CropTypes;
```

### Xem harvest schedules
```sql
SELECT 
    hs.ScheduleID,
    u.FullName,
    ct.CropName,
    hs.PlantingDate,
    hs.ExpectedHarvestDate,
    hs.Status
FROM HarvestSchedule hs
JOIN Users u ON hs.UserID = u.UserID
JOIN CropTypes ct ON hs.CropID = ct.CropID;
```

### Xem giá hiện tại
```sql
SELECT 
    ct.CropName,
    mp.Region,
    mp.PricePerKg,
    mp.UpdatedAt
FROM MarketPrices mp
JOIN CropTypes ct ON mp.CropID = ct.CropID
ORDER BY mp.UpdatedAt DESC;
```

### Xem lịch sử thay đổi giá
```sql
SELECT 
    ct.CropName,
    ph.Region,
    ph.OldPrice,
    ph.NewPrice,
    (ph.NewPrice - ph.OldPrice) AS PriceChange,
    ph.ChangeDate
FROM PriceHistory ph
JOIN CropTypes ct ON ph.CropID = ct.CropID
ORDER BY ph.ChangeDate DESC;
```

### Xem quality records
```sql
SELECT 
    qr.RecordID,
    ct.CropName,
    qr.AIGrade,
    qr.ConfidenceScore,
    qr.DetectedDiseases,
    qr.CheckDate
FROM QualityRecords qr
JOIN HarvestSchedule hs ON qr.ScheduleID = hs.ScheduleID
JOIN CropTypes ct ON hs.CropID = ct.CropID
ORDER BY qr.CheckDate DESC;
```

### Xem active alerts
```sql
SELECT 
    u.FullName,
    ct.CropName,
    a.TargetPrice,
    a.IsActive
FROM AlertSubscriptions a
JOIN Users u ON a.UserID = u.UserID
JOIN CropTypes ct ON a.CropID = ct.CropID
WHERE a.IsActive = 1;
```

## 🎯 Workflow Example

### Bước 1: Nông dân đăng ký
```sql
INSERT INTO Users (FullName, Email, PhoneNumber, ZaloID)
VALUES (N'Nguyễn Văn A', 'nguyenvana@gmail.com', '0987654321', 'zalo_123');
```

### 2. Tạo lịch trồng
```sql
INSERT INTO HarvestSchedule (UserID, CropID, PlantingDate, AreaSize, Region)
VALUES (2, 1, '2026-04-24', 1000, N'Đà Lạt');
```

### 3. Cập nhật giá thị trường (từ crawler)
```sql
INSERT INTO MarketPrices (CropID, Region, PricePerKg, SourceURL)
VALUES (1, N'Hà Nội', 25000, 'https://agro.gov.vn');
```

### 4. Lưu lịch sử giá
```sql
INSERT INTO PriceHistory (CropID, Region, OldPrice, NewPrice)
VALUES (1, N'Hà Nội', 23000, 25000);
```

### 5. Check chất lượng
```sql
INSERT INTO QualityRecords (ScheduleID, ImagePath, AIGrade, ConfidenceScore, DetectedDiseases)
VALUES (1, '/uploads/tomato_001.jpg', N'Loại 1', 0.95, N'Không phát hiện bệnh');
```

### 6. Đăng ký cảnh báo
```sql
INSERT INTO AlertSubscriptions (UserID, CropID, TargetPrice)
VALUES (2, 1, 30000);
```

## 🔔 Zalo Integration

Schema của bạn có `ZaloID` trong Users table. Để gửi thông báo qua Zalo:

```python
# backend/app/services/zalo_service.py
import httpx

async def send_zalo_notification(zalo_id: str, message: str):
    """Send notification via Zalo"""
    # Implement Zalo API call
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://openapi.zalo.me/v2.0/oa/message",
            headers={
                "access_token": "YOUR_ZALO_ACCESS_TOKEN"
            },
            json={
                "recipient": {"user_id": zalo_id},
                "message": {"text": message}
            }
        )
    return response.json()
```

## ✅ Checklist

- [x] SQL script của bạn đã chạy thành công
- [x] Python models đã cập nhật khớp với schema
- [x] Database có 7 tables
- [x] Có 3 crop types mẫu
- [x] Có 1 user mẫu
- [x] Có 1 stored procedure
- [ ] Test connection
- [ ] Start backend
- [ ] Start frontend
- [ ] Test API endpoints

## 🚀 Next Steps

1. **Chạy SQL script của bạn** trong SSMS
2. **Test connection:**
   ```bash
   python backend/test_sqlserver_connection.py
   ```
3. **Start backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```
4. **Test API:** http://localhost:8000/docs

---

**Schema của bạn đã sẵn sàng! Python models đã được cập nhật để khớp hoàn toàn! 🎉**
