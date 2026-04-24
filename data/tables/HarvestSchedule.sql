-- HarvestSchedule table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[HarvestSchedule]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[HarvestSchedule] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [CropTypeId] INT NOT NULL,
        [Region] NVARCHAR(100) NOT NULL,
        [PlantingDate] DATETIME2 NOT NULL,
        [PredictedHarvestDate] DATETIME2,
        [ActualHarvestDate] DATETIME2,
        [QuantityKg] DECIMAL(10, 2),
        [Notes] NVARCHAR(MAX),
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        [UpdatedAt] DATETIME2 DEFAULT GETDATE(),
        FOREIGN KEY ([CropTypeId]) REFERENCES [CropTypes]([Id])
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_harvest_schedules_crop' AND object_id = OBJECT_ID('HarvestSchedule'))
    CREATE INDEX idx_harvest_schedules_crop ON HarvestSchedule(CropTypeId);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_harvest_schedules_region' AND object_id = OBJECT_ID('HarvestSchedule'))
    CREATE INDEX idx_harvest_schedules_region ON HarvestSchedule(Region);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_harvest_schedules_planting_date' AND object_id = OBJECT_ID('HarvestSchedule'))
    CREATE INDEX idx_harvest_schedules_planting_date ON HarvestSchedule(PlantingDate);
GO
