-- MarketPrices table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[MarketPrices]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[MarketPrices] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [CropName] NVARCHAR(100) NOT NULL,
        [Region] NVARCHAR(100) NOT NULL,
        [PricePerKg] DECIMAL(10, 2) NOT NULL,
        [QualityGrade] NVARCHAR(20),
        [MarketType] NVARCHAR(50),
        [Source] NVARCHAR(100),
        [Date] DATE NOT NULL,
        [CreatedAt] DATETIME2 DEFAULT GETDATE()
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_market_prices_crop' AND object_id = OBJECT_ID('MarketPrices'))
    CREATE INDEX idx_market_prices_crop ON MarketPrices(CropName);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_market_prices_region' AND object_id = OBJECT_ID('MarketPrices'))
    CREATE INDEX idx_market_prices_region ON MarketPrices(Region);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_market_prices_date' AND object_id = OBJECT_ID('MarketPrices'))
    CREATE INDEX idx_market_prices_date ON MarketPrices(Date);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_market_prices_composite' AND object_id = OBJECT_ID('MarketPrices'))
    CREATE INDEX idx_market_prices_composite ON MarketPrices(CropName, Region, Date);
GO
