-- Seed data for market prices (sample data for testing)
MERGE INTO MarketPrices AS target
USING (VALUES
    -- Cà chua
    ('Cà chua', N'Hà Nội', 20000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Cà chua', N'TP.HCM', 22000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Cà chua', N'Đà Nẵng', 21000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Cà chua', N'Cần Thơ', 19000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    
    -- Dưa chuột
    ('Dưa chuột', N'Hà Nội', 15000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Dưa chuột', N'TP.HCM', 16000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Dưa chuột', N'Đà Nẵng', 15500, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    
    -- Rau muống
    ('Rau muống', N'Hà Nội', 8000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Rau muống', N'TP.HCM', 9000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    
    -- Cải xanh
    ('Cải xanh', N'Hà Nội', 12000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Cải xanh', N'TP.HCM', 13000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    
    -- Ớt
    ('Ớt', N'Hà Nội', 35000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE)),
    ('Ớt', N'TP.HCM', 38000, 'grade_1', 'wholesale', 'sample_data', CAST(GETDATE() AS DATE))
) AS source (CropName, Region, PricePerKg, QualityGrade, MarketType, Source, Date)
ON target.CropName = source.CropName 
   AND target.Region = source.Region 
   AND target.Date = source.Date
WHEN NOT MATCHED THEN
    INSERT (CropName, Region, PricePerKg, QualityGrade, MarketType, Source, Date)
    VALUES (source.CropName, source.Region, source.PricePerKg, source.QualityGrade, 
            source.MarketType, source.Source, source.Date);
GO
