-- Stored procedure to get price history
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetPriceHistory]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetPriceHistory];
GO

CREATE PROCEDURE [dbo].[sp_GetPriceHistory]
    @CropName NVARCHAR(100),
    @Region NVARCHAR(100),
    @Days INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        ph.Date,
        ph.AvgPrice,
        ph.MinPrice,
        ph.MaxPrice
    FROM PriceHistory ph
    WHERE ph.CropName = @CropName
        AND ph.Region = @Region
        AND ph.Date >= DATEADD(DAY, -@Days, CAST(GETDATE() AS DATE))
    ORDER BY ph.Date DESC;
END
GO
