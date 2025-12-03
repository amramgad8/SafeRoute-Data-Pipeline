{{ config(
    materialized='table'
) }}

-- Create a dim_date table spanning all dates present in the accidents staging table.
WITH staging AS (
    -- Bring in all data from the staging layer. We'll use this to determine date boundaries.
    SELECT * FROM {{ ref('stg_us_accidents') }}
),

date_range AS (
    -- Find the earliest and latest start_time (as DATE) in the data; this defines our dimension's span.
    SELECT
        MIN(CAST(start_time AS DATE)) AS min_date,
        MAX(CAST(start_time AS DATE)) AS max_date
    FROM staging
),

date_spine AS (
    -- This recursive common table expression (CTE) builds one row for every date in the range.
    -- Start with the minimum date, then repeatedly add one day until we reach the max_date.
    SELECT min_date AS date_day
    FROM date_range

    UNION ALL

    SELECT DATEADD(day, 1, date_day)
    FROM date_spine
    WHERE DATEADD(day, 1, date_day) <= (SELECT max_date FROM date_range)
)

SELECT
    -- YYYYMMDD integer for joining fact tables. Ex: 20230215
    TO_NUMBER(TO_CHAR(date_day, 'YYYYMMDD')) AS date_key,

    -- Full date value (DATE type)
    date_day AS full_date,

    -- Extract year (numeric, e.g., 2021)
    DATE_PART(year, date_day) AS year,

    -- Extract month number (1-12)
    DATE_PART(month, date_day) AS month,

    -- Extract month name (e.g., 'January')
    MONTHNAME(date_day) AS month_name,

    -- Extract day name (e.g., 'Monday')
    DAYNAME(date_day) AS day_name, -- ⚠️ Common error: a stray comma here will break code

    -- Boolean: TRUE if weekend (Saturday or Sunday), else FALSE
    CASE 
        WHEN DAYNAME(date_day) IN ('Sat', 'Sun') THEN TRUE 
        ELSE FALSE 
    END AS is_weekend

FROM date_spine