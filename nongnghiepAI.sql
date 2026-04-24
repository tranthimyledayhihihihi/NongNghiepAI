/* DỰ ÁN: HỆ THỐNG AI HỖ TRỢ NÔNG DÂN
    Cấu trúc DB: SQL Server
*/

-- 1. TẠO DATABASE (Nếu chưa có)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'NongNghiepAI')
BEGIN
    CREATE DATABASE NongNghiepAI;
END
GO

USE NongNghiepAI;
GO

-- 2. TẠO CÁC BẢNG (TABLES)

-- Bảng Người dùng 
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Users')
BEGIN
    CREATE TABLE Users (
        UserID INT PRIMARY KEY IDENTITY(1,1),
        FullName NVARCHAR(100) NOT NULL,
        Email NVARCHAR(100) UNIQUE,
        PhoneNumber NVARCHAR(20),
        ZaloID NVARCHAR(100), -- [cite: 6]
        CreatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- Bảng Loại nông sản [cite: 14]
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'CropTypes')
BEGIN
    CREATE TABLE CropTypes (
        CropID INT PRIMARY KEY IDENTITY(1,1),
        CropName NVARCHAR(100) NOT NULL,
        GrowthDurationDays INT, -- Dự báo thời gian thu hoạch [cite: 3]
        Description NVARCHAR(MAX)
    );
END
GO

-- Bảng Lịch trình thu hoạch [cite: 14]
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'HarvestSchedule')
BEGIN
    CREATE TABLE HarvestSchedule (
        ScheduleID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT FOREIGN KEY REFERENCES Users(UserID),
        CropID INT FOREIGN KEY REFERENCES CropTypes(CropID),
        PlantingDate DATE NOT NULL,
        AreaSize FLOAT,
        Region NVARCHAR(100),
        ExpectedHarvestDate DATE, -- [cite: 4, 13]
        Status NVARCHAR(50) DEFAULT 'Growing'
    );
END
GO

-- Bảng Giá thị trường (Dữ liệu cào) [cite: 14]
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MarketPrices')
BEGIN
    CREATE TABLE MarketPrices (
        PriceID INT PRIMARY KEY IDENTITY(1,1),
        CropID INT FOREIGN KEY REFERENCES CropTypes(CropID),
        Region NVARCHAR(100),
        PricePerKg DECIMAL(18, 2),
        SourceURL NVARCHAR(255), -- [cite: 10]
        UpdatedAt DATETIME DEFAULT GETDATE()
    );
END
GO

-- Bảng Lịch sử giá (Dự báo xu hướng) [cite: 14]
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'PriceHistory')
BEGIN
    CREATE TABLE PriceHistory (
        HistoryID INT PRIMARY KEY IDENTITY(1,1),
        CropID INT FOREIGN KEY REFERENCES CropTypes(CropID),
        Region NVARCHAR(100),
        OldPrice DECIMAL(18, 2),
        NewPrice DECIMAL(18, 2),
        ChangeDate DATETIME DEFAULT GETDATE()
    );
END
GO

-- Bảng Kết quả kiểm tra chất lượng (YOLOv8) 
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'QualityRecords')
BEGIN
    CREATE TABLE QualityRecords (
        RecordID INT PRIMARY KEY IDENTITY(1,1),
        ScheduleID INT FOREIGN KEY REFERENCES HarvestSchedule(ScheduleID),
        ImagePath NVARCHAR(500),
        AIGrade NVARCHAR(20), -- Loại 1, 2, 3 [cite: 5]
        ConfidenceScore FLOAT,
        DetectedDiseases NVARCHAR(MAX),
        CheckDate DATETIME DEFAULT GETDATE()
    );
END
GO

-- Bảng Đăng ký cảnh báo giá [cite: 14]
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AlertSubscriptions')
BEGIN
    CREATE TABLE AlertSubscriptions (
        AlertID INT PRIMARY KEY IDENTITY(1,1),
        UserID INT FOREIGN KEY REFERENCES Users(UserID),
        CropID INT FOREIGN KEY REFERENCES CropTypes(CropID),
        TargetPrice DECIMAL(18, 2),
        IsActive BIT DEFAULT 1 -- [cite: 6]
    );
END
GO

-- 3. NẠP DỮ LIỆU MẪU (SEEDS) [cite: 13]

IF NOT EXISTS (SELECT 1 FROM CropTypes WHERE CropName = N'Lúa')
    INSERT INTO CropTypes (CropName, GrowthDurationDays) VALUES (N'Lúa', 100);

IF NOT EXISTS (SELECT 1 FROM CropTypes WHERE CropName = N'Cà phê')
    INSERT INTO CropTypes (CropName, GrowthDurationDays) VALUES (N'Cà phê', 270);

IF NOT EXISTS (SELECT 1 FROM CropTypes WHERE CropName = N'Sầu riêng')
    INSERT INTO CropTypes (CropName, GrowthDurationDays) VALUES (N'Sầu riêng', 120);

-- Thêm một người dùng mẫu
IF NOT EXISTS (SELECT 1 FROM Users WHERE Email = 'leader@agriai.com')
    INSERT INTO Users (FullName, Email, PhoneNumber) VALUES (N'Trần Thị Mỹ', 'leader@agriai.com', '0123456789');
GO

-- 4. TẠO STORED PROCEDURE MẪU [cite: 13]
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_GetPriceHistory')
    DROP PROCEDURE sp_GetPriceHistory;
GO

CREATE PROCEDURE sp_GetPriceHistory
    @CropID INT,
    @Region NVARCHAR(100)
AS
BEGIN
    SELECT NewPrice, ChangeDate 
    FROM PriceHistory 
    WHERE CropID = @CropID AND Region = @Region
    ORDER BY ChangeDate DESC;
END;
GO