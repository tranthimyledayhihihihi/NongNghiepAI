-- QualityRecords table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[QualityRecords]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[QualityRecords] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [UserId] INT,
        [CropType] NVARCHAR(100),
        [QualityGrade] NVARCHAR(20) NOT NULL,
        [Confidence] DECIMAL(5, 4),
        [DefectCount] INT DEFAULT 0,
        [Defects] NVARCHAR(MAX), -- JSON array stored as string
        [ImagePath] NVARCHAR(500),
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        FOREIGN KEY ([UserId]) REFERENCES [Users]([Id])
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_quality_records_user' AND object_id = OBJECT_ID('QualityRecords'))
    CREATE INDEX idx_quality_records_user ON QualityRecords(UserId);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_quality_records_crop' AND object_id = OBJECT_ID('QualityRecords'))
    CREATE INDEX idx_quality_records_crop ON QualityRecords(CropType);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_quality_records_grade' AND object_id = OBJECT_ID('QualityRecords'))
    CREATE INDEX idx_quality_records_grade ON QualityRecords(QualityGrade);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_quality_records_date' AND object_id = OBJECT_ID('QualityRecords'))
    CREATE INDEX idx_quality_records_date ON QualityRecords(CreatedAt);
GO
