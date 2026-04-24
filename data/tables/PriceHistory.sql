-- PriceHistory table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[PriceHistory]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[PriceHistory] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [CropName] NVARCHAR(100) NOT NULL,
        [Region] NVARCHAR(100) NOT NULL,
        [AvgPrice] DECIMAL(10, 2) NOT NULL,
        [MinPrice] DECIMAL(10, 2),
        [MaxPrice] DECIMAL(10, 2),
        [Date] DATE NOT NULL,
        [CreatedAt] DATETIME2 DEFAULT GETDATE()
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_price_history_crop' AND object_id = OBJECT_ID('PriceHistory'))
    CREATE INDEX idx_price_history_crop ON PriceHistory(CropName);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_price_history_region' AND object_id = OBJECT_ID('PriceHistory'))
    CREATE INDEX idx_price_history_region ON PriceHistory(Region);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_price_history_date' AND object_id = OBJECT_ID('PriceHistory'))
    CREATE INDEX idx_price_history_date ON PriceHistory(Date);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_price_history_composite' AND object_id = OBJECT_ID('PriceHistory'))
    CREATE INDEX idx_price_history_composite ON PriceHistory(CropName, Region, Date);
GO
