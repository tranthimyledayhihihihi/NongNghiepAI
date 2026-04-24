-- Seed data for regions (reference data)
-- This is a reference table for common regions in Vietnam

-- Create Regions table if not exists
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Regions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Regions] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [Name] NVARCHAR(100) NOT NULL UNIQUE,
        [Code] NVARCHAR(10),
        [Type] NVARCHAR(20),
        [CreatedAt] DATETIME2 DEFAULT GETDATE()
    );
END
GO

-- Insert regions data
MERGE INTO Regions AS target
USING (VALUES
    (N'Hà Nội', 'HN', 'city'),
    (N'TP.HCM', 'HCM', 'city'),
    (N'Đà Nẵng', 'DN', 'city'),
    (N'Hải Phòng', 'HP', 'city'),
    (N'Cần Thơ', 'CT', 'city'),
    (N'An Giang', 'AG', 'province'),
    (N'Bà Rịa - Vũng Tàu', 'BRVT', 'province'),
    (N'Bắc Giang', 'BG', 'province'),
    (N'Bắc Kạn', 'BK', 'province'),
    (N'Bạc Liêu', 'BL', 'province'),
    (N'Bắc Ninh', 'BN', 'province'),
    (N'Bến Tre', 'BT', 'province'),
    (N'Bình Định', 'BD', 'province'),
    (N'Bình Dương', 'BDG', 'province'),
    (N'Bình Phước', 'BP', 'province'),
    (N'Bình Thuận', 'BTH', 'province'),
    (N'Cà Mau', 'CM', 'province'),
    (N'Cao Bằng', 'CB', 'province'),
    (N'Đắk Lắk', 'DL', 'province'),
    (N'Đắk Nông', 'DNO', 'province'),
    (N'Điện Biên', 'DB', 'province'),
    (N'Đồng Nai', 'DNI', 'province'),
    (N'Đồng Tháp', 'DT', 'province'),
    (N'Gia Lai', 'GL', 'province'),
    (N'Hà Giang', 'HG', 'province'),
    (N'Hà Nam', 'HNA', 'province'),
    (N'Hà Tĩnh', 'HT', 'province'),
    (N'Hải Dương', 'HD', 'province'),
    (N'Hậu Giang', 'HGI', 'province'),
    (N'Hòa Bình', 'HB', 'province'),
    (N'Hưng Yên', 'HY', 'province'),
    (N'Khánh Hòa', 'KH', 'province'),
    (N'Kiên Giang', 'KG', 'province'),
    (N'Kon Tum', 'KT', 'province'),
    (N'Lai Châu', 'LC', 'province'),
    (N'Lâm Đồng', 'LD', 'province'),
    (N'Lạng Sơn', 'LS', 'province'),
    (N'Lào Cai', 'LCA', 'province'),
    (N'Long An', 'LA', 'province'),
    (N'Nam Định', 'ND', 'province'),
    (N'Nghệ An', 'NA', 'province'),
    (N'Ninh Bình', 'NB', 'province'),
    (N'Ninh Thuận', 'NT', 'province'),
    (N'Phú Thọ', 'PT', 'province'),
    (N'Phú Yên', 'PY', 'province'),
    (N'Quảng Bình', 'QB', 'province'),
    (N'Quảng Nam', 'QN', 'province'),
    (N'Quảng Ngãi', 'QNG', 'province'),
    (N'Quảng Ninh', 'QNI', 'province'),
    (N'Quảng Trị', 'QT', 'province'),
    (N'Sóc Trăng', 'ST', 'province'),
    (N'Sơn La', 'SL', 'province'),
    (N'Tây Ninh', 'TN', 'province'),
    (N'Thái Bình', 'TB', 'province'),
    (N'Thái Nguyên', 'TNG', 'province'),
    (N'Thanh Hóa', 'TH', 'province'),
    (N'Thừa Thiên Huế', 'TTH', 'province'),
    (N'Tiền Giang', 'TG', 'province'),
    (N'Trà Vinh', 'TV', 'province'),
    (N'Tuyên Quang', 'TQ', 'province'),
    (N'Vĩnh Long', 'VL', 'province'),
    (N'Vĩnh Phúc', 'VP', 'province'),
    (N'Yên Bái', 'YB', 'province')
) AS source (Name, Code, Type)
ON target.Name = source.Name
WHEN NOT MATCHED THEN
    INSERT (Name, Code, Type)
    VALUES (source.Name, source.Code, source.Type);
GO
