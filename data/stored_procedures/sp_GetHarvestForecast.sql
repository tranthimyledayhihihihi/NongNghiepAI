-- Stored procedure to get harvest forecast
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GetHarvestForecast]') AND type in (N'P', N'PC'))
    DROP PROCEDURE [dbo].[sp_GetHarvestForecast];
GO

CREATE PROCEDURE [dbo].[sp_GetHarvestForecast]
    @CropTypeId INT,
    @Region NVARCHAR(100),
    @StartDate DATE,
    @EndDate DATE
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        hs.Id,
        hs.CropTypeId,
        hs.Region,
        hs.PlantingDate,
        hs.PredictedHarvestDate,
        hs.ActualHarvestDate,
        hs.QuantityKg,
        hs.Notes
    FROM HarvestSchedule hs
    WHERE hs.CropTypeId = @CropTypeId
        AND hs.Region = @Region
        AND hs.PredictedHarvestDate BETWEEN @StartDate AND @EndDate
    ORDER BY hs.PredictedHarvestDate;
END
GO
