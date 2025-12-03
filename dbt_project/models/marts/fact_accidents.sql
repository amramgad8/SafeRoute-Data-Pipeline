{{ config(
    materialized='table'
) }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_us_accidents') }}
),

final_fact AS (
    SELECT
        -- 1. Generate a Unique Key for the Fact Table itself
        -- (Optional but good for uniqueness checks)
        MD5(accident_id || '-' || TO_CHAR(start_time, 'YYYYMMDDHH24MISS')) AS accident_key,

        -- 2. Business Key (Original ID)
        accident_id,

        -- 3. Foreign Keys (Re-generating Hashes to match Dimensions) 🔗
        
        -- A. Date Key (Smart Key: YYYYMMDD)
        TO_NUMBER(TO_CHAR(start_time, 'YYYYMMDD')) AS date_key,

        -- B. Time Key (MD5: Hour - PartOfDay - DayNight)
        MD5(
            CAST(hour_24 AS VARCHAR) || '-' || 
            COALESCE(part_of_day, 'Unknown') || '-' || 
            COALESCE(day_night_indicator, 'Unknown')
        ) AS time_key,

        -- C. Location Key (MD5: Street - City - State - Zip - GeoPoint)
        MD5(
            street || '-' ||
            city || '-' ||
            county || '-' ||
            state_code || '-' ||
            zipcode || '-' ||
            ST_ASTEXT(geo_point) 
        ) AS location_key,

        -- D. Road Config Key (MD5: All 9 Flags)
        MD5(
            coalesce(cast(is_amenity as varchar), 'false') || '-' ||
            coalesce(cast(is_bump as varchar), 'false') || '-' ||
            coalesce(cast(is_crossing as varchar), 'false') || '-' ||
            coalesce(cast(is_junction as varchar), 'false') || '-' ||
            coalesce(cast(is_railway as varchar), 'false') || '-' ||
            coalesce(cast(is_station as varchar), 'false') || '-' ||
            coalesce(cast(is_stop as varchar), 'false') || '-' ||
            coalesce(cast(is_traffic_signal as varchar), 'false') || '-' ||
            coalesce(cast(is_turning_loop as varchar), 'false')
        ) AS road_config_key,

        -- E. Weather Key (MD5: Condition - Direction)
        MD5(
            coalesce(weather_condition, 'Unknown') || '-' ||
            coalesce(wind_direction, 'Unknown')
        ) AS weather_key,

        -- 4. Metrics (The Numbers we analyze) 📊
        severity,
        distance_miles,
        duration_minutes,
        temperature_f,
        visibility_miles,
        wind_speed_mph,
        precipitation_in,

        -- 5. Audit Column (Best Practice)
        CURRENT_TIMESTAMP() AS created_at

    FROM staging
    -- Filter out rows where essential keys might be null (Safety Net)
    WHERE start_time IS NOT NULL
)

SELECT * FROM final_fact