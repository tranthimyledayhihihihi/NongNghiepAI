-- Seed data for crop types
SET IDENTITY_INSERT CropTypes ON;
GO

MERGE INTO CropTypes AS target
USING (VALUES
    ('Cà chua', 'Tomato', 'vegetable', 75),
    ('Dưa chuột', 'Cucumber', 'vegetable', 60),
    ('Rau muống', 'Water spinach', 'vegetable', 30),
    ('Cải xanh', 'Bok choy', 'vegetable', 45),
    ('Ớt', 'Chili', 'vegetable', 90),
    ('Cà rốt', 'Carrot', 'vegetable', 70),
    ('Khoai tây', 'Potato', 'vegetable', 90),
    ('Bắp cải', 'Cabbage', 'vegetable', 80),
    ('Rau xà lách', 'Lettuce', 'vegetable', 40),
    ('Hành lá', 'Spring onion', 'vegetable', 60)
) AS source (Name, NameEn, Category, AvgGrowthDays)
ON target.Name = source.Name
WHEN NOT MATCHED THEN
    INSERT (Name, NameEn, Category, AvgGrowthDays)
    VALUES (source.Name, source.NameEn, source.Category, source.AvgGrowthDays);
GO

SET IDENTITY_INSERT CropTypes OFF;
GO
