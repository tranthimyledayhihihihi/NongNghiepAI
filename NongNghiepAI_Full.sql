/* ============================================================
DỰ ÁN: HỆ THỐNG AI HỖ TRỢ NÔNG DÂN
DỰ BÁO THU HOẠCH VÀ ĐỊNH GIÁ NÔNG SẢN
Cơ sở dữ liệu: SQL Server
Phiên bản: 1.0
Ngày tạo: 04/2026
Mô tả: Full schema + seed data cho hệ thống AgriAI
============================================================ */

-- ============================================================
-- BƯỚC 1: TẠO DATABASE
-- ============================================================
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'NongNghiepAI')
BEGIN
    CREATE DATABASE NongNghiepAI;
    PRINT N'✓ Đã tạo database NongNghiepAI';
END
GO

USE NongNghiepAI;
GO

-- ============================================================
-- BƯỚC 2: XÓA BẢNG CŨ (nếu chạy lại script)
-- ============================================================
IF OBJECT_ID('AIConversations',      'U') IS NOT NULL DROP TABLE AIConversations;
IF OBJECT_ID('QualityRecords',       'U') IS NOT NULL DROP TABLE QualityRecords;
IF OBJECT_ID('AlertSubscriptions',   'U') IS NOT NULL DROP TABLE AlertSubscriptions;
IF OBJECT_ID('PriceForecastResults', 'U') IS NOT NULL DROP TABLE PriceForecastResults;
IF OBJECT_ID('PriceHistory',         'U') IS NOT NULL DROP TABLE PriceHistory;
IF OBJECT_ID('MarketPrices',         'U') IS NOT NULL DROP TABLE MarketPrices;
IF OBJECT_ID('HarvestSchedule',      'U') IS NOT NULL DROP TABLE HarvestSchedule;
IF OBJECT_ID('WeatherData',          'U') IS NOT NULL DROP TABLE WeatherData;
IF OBJECT_ID('CropTypes',            'U') IS NOT NULL DROP TABLE CropTypes;
IF OBJECT_ID('Users',                'U') IS NOT NULL DROP TABLE Users;
GO

PRINT N'✓ Đã xóa các bảng cũ';
GO

-- ============================================================
-- BƯỚC 3: TẠO CÁC BẢNG
-- ============================================================

-- --------------------------------------------------------------
-- BẢNG 1: Người dùng (Nông dân / Admin)
-- --------------------------------------------------------------
CREATE TABLE Users (
    UserID          INT             PRIMARY KEY IDENTITY(1,1),
    FullName        NVARCHAR(100)   NOT NULL,
    Email           NVARCHAR(100)   UNIQUE,
    PhoneNumber     NVARCHAR(20),
    ZaloID          NVARCHAR(100),              -- Gửi cảnh báo qua Zalo
    PasswordHash    NVARCHAR(255)   NOT NULL,
    Role            NVARCHAR(20)    DEFAULT 'farmer'  
                    CHECK (Role IN ('farmer', 'admin', 'expert')),
    Region          NVARCHAR(100),              -- Tỉnh/thành phố
    IsActive        BIT             DEFAULT 1,
    IsVerified      BIT             DEFAULT 0,
    CreatedAt       DATETIME        DEFAULT GETDATE(),
    UpdatedAt       DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng Users';

-- --------------------------------------------------------------
-- BẢNG 2: Loại nông sản
-- --------------------------------------------------------------
CREATE TABLE CropTypes (
    CropID              INT             PRIMARY KEY IDENTITY(1,1),
    CropName            NVARCHAR(100)   NOT NULL UNIQUE,
    CropNameEN          NVARCHAR(100),           -- Tên tiếng Anh
    Category            NVARCHAR(50)    NOT NULL 
                        CHECK (Category IN (N'Rau củ', N'Trái cây', N'Lúa gạo', N'Công nghiệp', N'Khác')),
    GrowthDurationDays  INT,                     -- Số ngày từ gieo đến thu hoạch
    HarvestSeason       NVARCHAR(100),           -- Mùa vụ thu hoạch
    TypicalPriceMin     DECIMAL(18,2),           -- Giá tối thiểu thông thường (VNĐ/kg)
    TypicalPriceMax     DECIMAL(18,2),           -- Giá tối đa thông thường (VNĐ/kg)
    Description         NVARCHAR(MAX),
    ImageURL            NVARCHAR(500),
    CreatedAt           DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng CropTypes';

-- --------------------------------------------------------------
-- BẢNG 3: Dữ liệu thời tiết theo khu vực
-- --------------------------------------------------------------
CREATE TABLE WeatherData (
    WeatherID       INT             PRIMARY KEY IDENTITY(1,1),
    Region          NVARCHAR(100)   NOT NULL,
    RecordDate      DATE            NOT NULL,
    TempMin         FLOAT,                       -- Nhiệt độ thấp nhất (°C)
    TempMax         FLOAT,                       -- Nhiệt độ cao nhất (°C)
    Humidity        FLOAT,                       -- Độ ẩm (%)
    Rainfall        FLOAT,                       -- Lượng mưa (mm)
    SunshineHours   FLOAT,                       -- Số giờ nắng
    WeatherDesc     NVARCHAR(100),               -- Mô tả thời tiết
    CreatedAt       DATETIME        DEFAULT GETDATE(),
    CONSTRAINT UQ_Weather UNIQUE (Region, RecordDate)
);
GO

PRINT N'✓ Đã tạo bảng WeatherData';

-- --------------------------------------------------------------
-- BẢNG 4: Lịch trình thu hoạch của nông dân
-- --------------------------------------------------------------
CREATE TABLE HarvestSchedule (
    ScheduleID              INT             PRIMARY KEY IDENTITY(1,1),
    UserID                  INT             NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    CropID                  INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    PlantingDate            DATE            NOT NULL,           -- Ngày gieo trồng
    AreaSize                FLOAT,                              -- Diện tích (ha)
    Region                  NVARCHAR(100)   NOT NULL,
    ExpectedHarvestDate     DATE,                               -- Ngày thu hoạch dự kiến (AI tính)
    ActualHarvestDate       DATE,                               -- Ngày thu hoạch thực tế
    EstimatedYieldKg        FLOAT,                              -- Sản lượng ước tính (kg)
    ActualYieldKg           FLOAT,                              -- Sản lượng thực tế (kg)
    FertilizerUsed          NVARCHAR(200),                      -- Phân bón đã dùng
    PesticideUsed           NVARCHAR(200),                      -- Thuốc BVTV đã dùng
    Status                  NVARCHAR(50)    DEFAULT N'Đang trồng'
                            CHECK (Status IN (N'Đang trồng', N'Sắp thu hoạch', N'Đã thu hoạch', N'Thất mùa')),
    Notes                   NVARCHAR(MAX),
    CreatedAt               DATETIME        DEFAULT GETDATE(),
    UpdatedAt               DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng HarvestSchedule';

-- --------------------------------------------------------------
-- BẢNG 5: Giá thị trường hiện tại (dữ liệu cào web)
-- --------------------------------------------------------------
CREATE TABLE MarketPrices (
    PriceID         INT             PRIMARY KEY IDENTITY(1,1),
    CropID          INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    Region          NVARCHAR(100)   NOT NULL,
    PricePerKg      DECIMAL(18,2)   NOT NULL,                   -- Giá/kg (VNĐ)
    QualityGrade    NVARCHAR(20)    DEFAULT N'Loại 1'
                    CHECK (QualityGrade IN (N'Loại 1', N'Loại 2', N'Loại 3')),
    MarketType      NVARCHAR(50)    DEFAULT N'Bán lẻ'
                    CHECK (MarketType IN (N'Bán buôn', N'Bán lẻ', N'Xuất khẩu')),
    SourceURL       NVARCHAR(500),                              -- URL nguồn dữ liệu
    SourceName      NVARCHAR(100),                              -- Tên nguồn (agro.gov.vn, ...)
    PriceDate       DATE            NOT NULL,
    UpdatedAt       DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng MarketPrices';

-- --------------------------------------------------------------
-- BẢNG 6: Lịch sử biến động giá (dùng cho AI dự báo)
-- --------------------------------------------------------------
CREATE TABLE PriceHistory (
    HistoryID       INT             PRIMARY KEY IDENTITY(1,1),
    CropID          INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    Region          NVARCHAR(100)   NOT NULL,
    AvgPrice        DECIMAL(18,2)   NOT NULL,                   -- Giá trung bình ngày
    MinPrice        DECIMAL(18,2),                              -- Giá thấp nhất ngày
    MaxPrice        DECIMAL(18,2),                              -- Giá cao nhất ngày
    Volume          FLOAT,                                      -- Sản lượng giao dịch (tấn)
    RecordDate      DATE            NOT NULL,
    CreatedAt       DATETIME        DEFAULT GETDATE(),
    CONSTRAINT UQ_PriceHistory UNIQUE (CropID, Region, RecordDate)
);
GO

PRINT N'✓ Đã tạo bảng PriceHistory';

-- --------------------------------------------------------------
-- BẢNG 7: Kết quả dự báo giá từ AI Model
-- --------------------------------------------------------------
CREATE TABLE PriceForecastResults (
    ForecastID      INT             PRIMARY KEY IDENTITY(1,1),
    CropID          INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    Region          NVARCHAR(100)   NOT NULL,
    ForecastDate    DATE            NOT NULL,                   -- Ngày được dự báo
    PredictedPrice  DECIMAL(18,2)   NOT NULL,                   -- Giá dự báo
    ConfidenceLow   DECIMAL(18,2),                              -- Khoảng tin cậy thấp
    ConfidenceHigh  DECIMAL(18,2),                              -- Khoảng tin cậy cao
    PriceTrend      NVARCHAR(20)    CHECK (PriceTrend IN (N'Tăng', N'Giảm', N'Ổn định')),
    ModelVersion    NVARCHAR(50),                               -- Phiên bản AI model
    GeneratedAt     DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng PriceForecastResults';

-- --------------------------------------------------------------
-- BẢNG 8: Kết quả kiểm tra chất lượng bằng AI (YOLOv8)
-- --------------------------------------------------------------
CREATE TABLE QualityRecords (
    RecordID            INT             PRIMARY KEY IDENTITY(1,1),
    ScheduleID          INT             FOREIGN KEY REFERENCES HarvestSchedule(ScheduleID),
    UserID              INT             NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    CropID              INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    ImagePath           NVARCHAR(500)   NOT NULL,               -- Đường dẫn ảnh upload
    AIGrade             NVARCHAR(20)    CHECK (AIGrade IN (N'Loại 1', N'Loại 2', N'Loại 3')),
    ConfidenceScore     FLOAT,                                  -- Độ tin cậy (0.0 - 1.0)
    DetectedIssues      NVARCHAR(MAX),                          -- Bệnh/sâu hại phát hiện (JSON)
    SuggestedPriceMin   DECIMAL(18,2),                          -- Giá đề xuất tối thiểu
    SuggestedPriceMax   DECIMAL(18,2),                          -- Giá đề xuất tối đa
    Recommendation      NVARCHAR(MAX),                          -- Khuyến nghị xử lý
    CheckDate           DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng QualityRecords';

-- --------------------------------------------------------------
-- BẢNG 9: Đăng ký cảnh báo giá
-- --------------------------------------------------------------
CREATE TABLE AlertSubscriptions (
    AlertID             INT             PRIMARY KEY IDENTITY(1,1),
    UserID              INT             NOT NULL FOREIGN KEY REFERENCES Users(UserID),
    CropID              INT             NOT NULL FOREIGN KEY REFERENCES CropTypes(CropID),
    Region              NVARCHAR(100)   NOT NULL,
    TargetPrice         DECIMAL(18,2)   NOT NULL,               -- Giá mục tiêu muốn nhận cảnh báo
    AlertType           NVARCHAR(20)    DEFAULT N'Trên'
                        CHECK (AlertType IN (N'Trên', N'Dưới', N'Thay đổi')),
    NotifyMethod        NVARCHAR(20)    DEFAULT N'Email'
                        CHECK (NotifyMethod IN (N'Email', N'SMS', N'Zalo', N'App')),
    IsActive            BIT             DEFAULT 1,
    LastTriggered       DATETIME,                               -- Lần cuối cảnh báo được gửi
    CreatedAt           DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng AlertSubscriptions';

-- --------------------------------------------------------------
-- BẢNG 10: Lịch sử hội thoại với AI (Claude)
-- --------------------------------------------------------------
CREATE TABLE AIConversations (
    ConvID          INT             PRIMARY KEY IDENTITY(1,1),
    UserID          INT             FOREIGN KEY REFERENCES Users(UserID),
    SessionID       NVARCHAR(100),                              -- ID phiên trò chuyện
    UserMessage     NVARCHAR(MAX)   NOT NULL,                   -- Câu hỏi của nông dân
    AIResponse      NVARCHAR(MAX)   NOT NULL,                   -- Trả lời của AI
    Topic           NVARCHAR(50)    CHECK (Topic IN (N'Giá cả', N'Thu hoạch', N'Chất lượng', N'Thời tiết', N'Dịch bệnh', N'Khác')),
    RelatedCropID   INT             FOREIGN KEY REFERENCES CropTypes(CropID),
    CreatedAt       DATETIME        DEFAULT GETDATE()
);
GO

PRINT N'✓ Đã tạo bảng AIConversations';
GO

-- ============================================================
-- BƯỚC 4: TẠO INDEX để tăng tốc truy vấn
-- ============================================================
CREATE INDEX IDX_MarketPrices_Crop_Region    ON MarketPrices    (CropID, Region, PriceDate DESC);
CREATE INDEX IDX_PriceHistory_Crop_Region    ON PriceHistory    (CropID, Region, RecordDate DESC);
CREATE INDEX IDX_PriceForecast_Crop_Region   ON PriceForecastResults (CropID, Region, ForecastDate);
CREATE INDEX IDX_HarvestSchedule_User        ON HarvestSchedule (UserID, Status);
CREATE INDEX IDX_QualityRecords_User         ON QualityRecords  (UserID, CheckDate DESC);
CREATE INDEX IDX_AlertSubscriptions_Active   ON AlertSubscriptions (IsActive, CropID);
CREATE INDEX IDX_AIConversations_User        ON AIConversations (UserID, CreatedAt DESC);
GO

PRINT N'✓ Đã tạo các Index';
GO

-- ============================================================
-- BƯỚC 5: NẠP DỮ LIỆU MẪU (SEED DATA)
-- ============================================================

-- --- Dữ liệu mẫu: Người dùng ---
INSERT INTO Users (FullName, Email, PhoneNumber, ZaloID, PasswordHash, Role, Region) VALUES
(N'Nguyễn Văn An',      'nguyenvanan@gmail.com',    '0901234567', 'zalo_001', '$2b$12$hashpassword1', N'farmer', N'Hà Nội'),
(N'Trần Thị Mỹ',        'tranthimy2205@gmail.com',  '0912345678', 'zalo_002', '$2b$12$hashpassword2', N'farmer', N'TP.HCM'),
(N'Lê Văn Bình',        'levanbinhfarmer@gmail.com','0923456789', 'zalo_003', '$2b$12$hashpassword3', N'farmer', N'Cần Thơ'),
(N'Phạm Thị Lan',       'phamthilan@gmail.com',     '0934567890', 'zalo_004', '$2b$12$hashpassword4', N'farmer', N'Đà Lạt'),
(N'Admin Hệ thống',     'admin@agriAI.vn',          '0800000001', NULL,       '$2b$12$hashpassword0', N'admin',  N'Hà Nội');
GO

-- --- Dữ liệu mẫu: Loại nông sản ---
INSERT INTO CropTypes (CropName, CropNameEN, Category, GrowthDurationDays, HarvestSeason, TypicalPriceMin, TypicalPriceMax, Description) VALUES
(N'Lúa',        'Rice',         N'Lúa gạo',     100, N'Tháng 5-6, 10-11',    6000,   9000,   N'Lúa nước, cây lương thực chính của Việt Nam'),
(N'Ngô',        'Corn',         N'Lúa gạo',     90,  N'Tháng 3-4, 7-8',      5000,   8000,   N'Ngô lai, dùng làm thức ăn chăn nuôi và thực phẩm'),
(N'Cà phê',     'Coffee',       N'Công nghiệp', 270, N'Tháng 11-2',          30000,  60000,  N'Cà phê Robusta và Arabica, xuất khẩu chủ lực'),
(N'Sầu riêng',  'Durian',       N'Trái cây',    120, N'Tháng 5-8',           60000,  150000, N'Sầu riêng Musang King, Ri6, xuất khẩu Trung Quốc'),
(N'Xoài',       'Mango',        N'Trái cây',    90,  N'Tháng 3-5',           15000,  40000,  N'Xoài cát Hòa Lộc, xoài Đài Loan'),
(N'Thanh long', 'Dragon Fruit', N'Trái cây',    30,  N'Quanh năm',           8000,   25000,  N'Thanh long ruột đỏ, ruột trắng Bình Thuận'),
(N'Rau muống',  'Water Spinach',N'Rau củ',      25,  N'Quanh năm',           5000,   12000,  N'Rau muống nước và rau muống cạn'),
(N'Cà chua',    'Tomato',       N'Rau củ',      75,  N'Tháng 10-2',          8000,   20000,  N'Cà chua bi, cà chua thân gỗ'),
(N'Khoai lang', 'Sweet Potato', N'Rau củ',      100, N'Tháng 9-12',          7000,   15000,  N'Khoai lang tím, khoai lang mật'),
(N'Hồ tiêu',    'Black Pepper', N'Công nghiệp', 365, N'Tháng 1-3',           60000,  120000, N'Hồ tiêu đen Phú Quốc, Bình Phước');
GO

-- --- Dữ liệu mẫu: Thời tiết ---
INSERT INTO WeatherData (Region, RecordDate, TempMin, TempMax, Humidity, Rainfall, SunshineHours, WeatherDesc) VALUES
(N'Hà Nội',   '2026-04-01', 22, 30, 75, 5.2,  6.5, N'Nắng nhẹ'),
(N'Hà Nội',   '2026-04-02', 21, 28, 80, 15.0, 3.0, N'Mưa rào'),
(N'Hà Nội',   '2026-04-03', 23, 31, 70, 0.0,  8.0, N'Nắng'),
(N'TP.HCM',   '2026-04-01', 26, 35, 65, 0.0,  9.5, N'Nắng nóng'),
(N'TP.HCM',   '2026-04-02', 25, 33, 70, 20.5, 5.0, N'Mưa chiều'),
(N'Cần Thơ',  '2026-04-01', 25, 34, 72, 2.0,  8.5, N'Nắng nhẹ'),
(N'Đà Lạt',   '2026-04-01', 15, 23, 85, 8.0,  4.0, N'Sương mù buổi sáng'),
(N'Đà Nẵng',  '2026-04-01', 24, 32, 68, 0.0,  9.0, N'Nắng');
GO

-- --- Dữ liệu mẫu: Lịch trình thu hoạch ---
INSERT INTO HarvestSchedule (UserID, CropID, PlantingDate, AreaSize, Region, ExpectedHarvestDate, EstimatedYieldKg, Status) VALUES
(1, 1, '2026-01-15', 2.5, N'Hà Nội',  '2026-04-25', 12500, N'Sắp thu hoạch'),
(2, 4, '2025-12-01', 1.0, N'TP.HCM',  '2026-04-01', 8000,  N'Đã thu hoạch'),
(3, 6, '2026-02-01', 3.0, N'Cần Thơ', '2026-03-03', 15000, N'Đã thu hoạch'),
(4, 3, '2025-06-01', 5.0, N'Đà Lạt',  '2026-03-01', 25000, N'Đang trồng'),
(1, 8, '2026-02-15', 0.5, N'Hà Nội',  '2026-05-01', 3000,  N'Đang trồng');
GO

-- --- Dữ liệu mẫu: Giá thị trường hiện tại ---
INSERT INTO MarketPrices (CropID, Region, PricePerKg, QualityGrade, MarketType, SourceName, PriceDate) VALUES
(1, N'Hà Nội',   7500,  N'Loại 1', N'Bán lẻ',   N'agro.gov.vn',   '2026-04-24'),
(1, N'TP.HCM',   7200,  N'Loại 1', N'Bán lẻ',   N'agro.gov.vn',   '2026-04-24'),
(1, N'Cần Thơ',  6800,  N'Loại 1', N'Bán buôn', N'giaviet.com',   '2026-04-24'),
(4, N'TP.HCM',   95000, N'Loại 1', N'Bán lẻ',   N'agro.gov.vn',   '2026-04-24'),
(4, N'Cần Thơ',  85000, N'Loại 1', N'Bán buôn', N'giaviet.com',   '2026-04-24'),
(3, N'Đà Lạt',   45000, N'Loại 1', N'Xuất khẩu',N'vicofa.com.vn', '2026-04-24'),
(6, N'Bình Thuận',12000,N'Loại 1', N'Bán buôn', N'agro.gov.vn',   '2026-04-24'),
(5, N'Cần Thơ',  25000, N'Loại 1', N'Bán buôn', N'agro.gov.vn',   '2026-04-24');
GO

-- --- Dữ liệu mẫu: Lịch sử giá (30 ngày gần nhất cho Lúa - Hà Nội) ---
DECLARE @i INT = 30;
DECLARE @basePrice DECIMAL(18,2) = 7000;

WHILE @i >= 0
BEGIN
    INSERT INTO PriceHistory (CropID, Region, AvgPrice, MinPrice, MaxPrice, Volume, RecordDate)
    VALUES (
        1, 
        N'Hà Nội',
        @basePrice + (@i * 15) + (ABS(CHECKSUM(NEWID())) % 200 - 100),
        @basePrice + (@i * 15) - 200,
        @basePrice + (@i * 15) + 300,
        500 + (ABS(CHECKSUM(NEWID())) % 100),
        DATEADD(DAY, -@i, CAST('2026-04-24' AS DATE))
    );
    SET @i = @i - 1;
END
GO

PRINT N'✓ Đã nạp dữ liệu mẫu';
GO

-- ============================================================
-- BƯỚC 6: KIỂM TRA KẾT QUẢ
-- ============================================================
PRINT N'';
PRINT N'============================================================';
PRINT N'TỔNG KẾT';
PRINT N'============================================================';

SELECT 
    t.name AS TableName,
    p.rows AS RowCount
FROM 
    sys.tables t
INNER JOIN      
    sys.partitions p ON t.object_id = p.OBJECT_ID
WHERE 
    t.is_ms_shipped = 0
    AND p.index_id IN (0,1)
ORDER BY 
    t.name;

PRINT N'';
PRINT N'✅ Hoàn thành! Database NongNghiepAI đã sẵn sàng.';
PRINT N'';
PRINT N'📊 Thống kê:';
PRINT N'   - 10 tables';
PRINT N'   - 5 users (4 farmers + 1 admin)';
PRINT N'   - 10 crop types';
PRINT N'   - 8 weather records';
PRINT N'   - 5 harvest schedules';
PRINT N'   - 8 market prices';
PRINT N'   - 31 price history records';
PRINT N'';
PRINT N'🚀 Next steps:';
PRINT N'   1. Test connection: python test_connection_debug.py';
PRINT N'   2. Start backend: cd backend && uvicorn app.main:app --reload';
PRINT N'   3. Start frontend: cd frontend && npm run dev';
GO
