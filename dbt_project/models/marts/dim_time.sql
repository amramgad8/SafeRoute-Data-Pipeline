{{ config(
    materialized='table'
) }}

WITH staging AS (
    SELECT * FROM {{ ref('stg_us_accidents') }}
),

distinct_times AS (
    -- Get unique combinations of Hour + Time of Day + Day/Night
    SELECT DISTINCT
        hour_24,
        part_of_day,
        day_night_indicator -- Sunrise_Sunset
    FROM staging
)

SELECT
    -- Generate Surrogate Key using MD5
    -- We use MD5 here because Day/Night changes for the same hour
    MD5(
        CAST(hour_24 AS VARCHAR) || '-' || 
        COALESCE(part_of_day, 'Unknown') || '-' || 
        COALESCE(day_night_indicator, 'Unknown')
    ) AS time_key,

    hour_24,
    part_of_day,
    day_night_indicator

FROM distinct_times
ORDER BY hour_24