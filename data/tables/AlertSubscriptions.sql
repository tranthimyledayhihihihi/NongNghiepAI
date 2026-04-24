-- AlertSubscriptions table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[AlertSubscriptions]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[AlertSubscriptions] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [UserId] INT,
        [CropName] NVARCHAR(100) NOT NULL,
        [Region] NVARCHAR(100) NOT NULL,
        [PriceChangeThreshold] DECIMAL(5, 2) DEFAULT 10.0,
        [NotifyMethod] NVARCHAR(20) DEFAULT 'email',
        [Contact] NVARCHAR(255) NOT NULL,
        [IsActive] BIT DEFAULT 1,
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        [UpdatedAt] DATETIME2 DEFAULT GETDATE(),
        FOREIGN KEY ([UserId]) REFERENCES [Users]([Id])
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_alert_subscriptions_user' AND object_id = OBJECT_ID('AlertSubscriptions'))
    CREATE INDEX idx_alert_subscriptions_user ON AlertSubscriptions(UserId);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_alert_subscriptions_crop' AND object_id = OBJECT_ID('AlertSubscriptions'))
    CREATE INDEX idx_alert_subscriptions_crop ON AlertSubscriptions(CropName);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_alert_subscriptions_active' AND object_id = OBJECT_ID('AlertSubscriptions'))
    CREATE INDEX idx_alert_subscriptions_active ON AlertSubscriptions(IsActive);
GO
