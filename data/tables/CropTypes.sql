-- CropTypes table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[CropTypes]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[CropTypes] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [Name] NVARCHAR(100) NOT NULL UNIQUE,
        [NameEn] NVARCHAR(100),
        [Category] NVARCHAR(50),
        [AvgGrowthDays] INT,
        [CreatedAt] DATETIME2 DEFAULT GETDATE()
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_crop_types_name' AND object_id = OBJECT_ID('CropTypes'))
    CREATE INDEX idx_crop_types_name ON CropTypes(Name);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_crop_types_category' AND object_id = OBJECT_ID('CropTypes'))
    CREATE INDEX idx_crop_types_category ON CropTypes(Category);
GO
