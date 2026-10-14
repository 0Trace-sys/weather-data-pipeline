
-- Weather Data Pipeline
-- Forecast analysis queries

-- 1. Total forecast records
SELECT COUNT(*) AS total_records
FROM weather_forecasts;


-- 2. Temperature statistics by city
SELECT
    city,
    ROUND(AVG(temperature_f)::numeric, 2) AS avg_temp_f,
    MIN(temperature_f) AS min_temp_f,
    MAX(temperature_f) AS max_temp_f
FROM weather_forecasts
GROUP BY city;


-- 3. Daily temperature statistics (Central Time)
SELECT
    city,
    (forecast_time AT TIME ZONE 'America/Chicago')::date
        AS forecast_date,
    ROUND(AVG(temperature_f)::numeric, 2) AS avg_temp_f,
    MIN(temperature_f) AS min_temp_f,
    MAX(temperature_f) AS max_temp_f
FROM weather_forecasts
GROUP BY city, forecast_date
ORDER BY forecast_date;
