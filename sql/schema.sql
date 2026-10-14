-- Weather Data Pipeline
-- PostgreSQL database schema

CREATE TABLE IF NOT EXISTS weather_forecasts (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    forecast_time TIMESTAMPTZ NOT NULL,
    temperature_f DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT unique_city_time
        UNIQUE (city, forecast_time)
);