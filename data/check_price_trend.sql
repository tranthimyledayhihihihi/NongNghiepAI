-- Query to check price trends
-- This script helps analyze price trends and patterns

-- Latest prices by crop and region
SELECT 
    crop_name,
    region,
    price_per_kg,
    quality_grade,
    date
FROM market_prices
WHERE date = (
    SELECT MAX(date)
    FROM market_prices mp2
    WHERE mp2.crop_name = market_prices.crop_name
        AND mp2.region = market_prices.region
)
ORDER BY crop_name, region;

-- Price trend (last 7 days)
SELECT 
    crop_name,
    region,
    date,
    price_per_kg,
    LAG(price_per_kg) OVER (PARTITION BY crop_name, region ORDER BY date) as prev_price,
    price_per_kg - LAG(price_per_kg) OVER (PARTITION BY crop_name, region ORDER BY date) as price_change,
    ROUND(
        ((price_per_kg - LAG(price_per_kg) OVER (PARTITION BY crop_name, region ORDER BY date)) 
        / LAG(price_per_kg) OVER (PARTITION BY crop_name, region ORDER BY date) * 100)::numeric, 
        2
    ) as percent_change
FROM market_prices
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY crop_name, region, date;

-- Average price by crop (last 30 days)
SELECT 
    crop_name,
    region,
    ROUND(AVG(price_per_kg)::numeric, 2) as avg_price,
    ROUND(MIN(price_per_kg)::numeric, 2) as min_price,
    ROUND(MAX(price_per_kg)::numeric, 2) as max_price,
    COUNT(*) as data_points
FROM market_prices
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY crop_name, region
ORDER BY crop_name, avg_price DESC;

-- Price volatility (standard deviation)
SELECT 
    crop_name,
    region,
    ROUND(AVG(price_per_kg)::numeric, 2) as avg_price,
    ROUND(STDDEV(price_per_kg)::numeric, 2) as price_volatility,
    ROUND((STDDEV(price_per_kg) / AVG(price_per_kg) * 100)::numeric, 2) as coefficient_of_variation
FROM market_prices
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY crop_name, region
HAVING COUNT(*) >= 5
ORDER BY coefficient_of_variation DESC;

-- Highest and lowest prices
SELECT 
    'Highest' as type,
    crop_name,
    region,
    price_per_kg,
    date
FROM market_prices
WHERE price_per_kg = (SELECT MAX(price_per_kg) FROM market_prices)
UNION ALL
SELECT 
    'Lowest' as type,
    crop_name,
    region,
    price_per_kg,
    date
FROM market_prices
WHERE price_per_kg = (SELECT MIN(price_per_kg) FROM market_prices);
