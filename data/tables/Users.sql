-- Users table
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Users]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Users] (
        [Id] INT IDENTITY(1,1) PRIMARY KEY,
        [Email] NVARCHAR(255) NOT NULL UNIQUE,
        [Phone] NVARCHAR(20),
        [FullName] NVARCHAR(255),
        [HashedPassword] NVARCHAR(255) NOT NULL,
        [IsActive] BIT DEFAULT 1,
        [IsVerified] BIT DEFAULT 0,
        [CreatedAt] DATETIME2 DEFAULT GETDATE(),
        [UpdatedAt] DATETIME2 DEFAULT GETDATE()
    );
END
GO

-- Indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('Users'))
    CREATE INDEX idx_users_email ON Users(Email);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_phone' AND object_id = OBJECT_ID('Users'))
    CREATE INDEX idx_users_phone ON Users(Phone);
GO
