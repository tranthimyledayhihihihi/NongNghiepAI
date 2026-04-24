-- Stored procedure to update or insert market price
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_UpdateMarketPrice]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_UpdateMarketPrice];
GO

CREATE PROCEDURE [dbo].[sp_UpdateMarketPrice]
    @CropName NVARCHAR(100),
    @Region NVARCHAR(100),
    @PricePerKg DECIMAL(10, 2),
    @QualityGrade NVARCHAR(20),
    @MarketType NVARCHAR(50),
    @Source NVARCHAR(100),
    @Date DATE
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Id INT;
    
    -- Check if price already exists for this date
    SELECT @Id = Id
    FROM MarketPrices
    WHERE CropName = @CropName
        AND Region = @Region
        AND QualityGrade = @QualityGrade
        AND Date = @Date
        AND Source = @Source;
    
    IF @Id IS NOT NULL
    BEGIN
        -- Update existing price
        UPDATE MarketPrices
        SET PricePerKg = @PricePerKg,
            MarketType = @MarketType,
            CreatedAt = GETDATE()
        WHERE Id = @Id;
    END
    ELSE
    BEGIN
        -- Insert new price
        INSERT INTO MarketPrices (
            CropName,
            Region,
            PricePerKg,
            QualityGrade,
            MarketType,
            Source,
            Date
        ) VALUES (
            @CropName,
            @Region,
            @PricePerKg,
            @QualityGrade,
            @MarketType,
            @Source,
            @Date
        );
        
        SET @Id = SCOPE_IDENTITY();
    END
    
    -- Return the ID
    SELECT @Id AS Id;
END
GO
