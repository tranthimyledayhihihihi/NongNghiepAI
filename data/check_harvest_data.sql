-- Query to check harvest data
-- This script helps verify harvest schedule data

-- Count total harvest schedules
SELECT COUNT(*) as total_schedules
FROM harvest_schedules;

-- Count by region
SELECT region, COUNT(*) as count
FROM harvest_schedules
GROUP BY region
ORDER BY count DESC;

-- Count by crop type
SELECT ct.name, COUNT(hs.id) as count
FROM harvest_schedules hs
JOIN crop_types ct ON hs.crop_type_id = ct.id
GROUP BY ct.name
ORDER BY count DESC;

-- Upcoming harvests (next 30 days)
SELECT 
    ct.name as crop_name,
    hs.region,
    hs.planting_date,
    hs.predicted_harvest_date,
    hs.quantity_kg
FROM harvest_schedules hs
JOIN crop_types ct ON hs.crop_type_id = ct.id
WHERE hs.predicted_harvest_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
ORDER BY hs.predicted_harvest_date;

-- Accuracy check (compare predicted vs actual)
SELECT 
    ct.name as crop_name,
    hs.region,
    hs.predicted_harvest_date,
    hs.actual_harvest_date,
    (hs.actual_harvest_date - hs.predicted_harvest_date) as days_difference
FROM harvest_schedules hs
JOIN crop_types ct ON hs.crop_type_id = ct.id
WHERE hs.actual_harvest_date IS NOT NULL
ORDER BY ABS(EXTRACT(DAY FROM (hs.actual_harvest_date - hs.predicted_harvest_date))) DESC;
