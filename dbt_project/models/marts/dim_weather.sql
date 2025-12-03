{{ config(
    materialized='table'
) }}

/*
    DIM_WEATHER
    Goal: Capture unique weather conditions and wind directions.
*/

with staging as (

    select * from {{ ref('stg_us_accidents') }}

),

distinct_weather as (

    -- Select unique combinations of weather description
    select distinct
        weather_condition,
        wind_direction
    from staging

),

final_dim as (

    select
        -- Generate Surrogate Key using MD5 🔑
        md5(
            coalesce(weather_condition, 'Unknown') || '-' ||
            coalesce(wind_direction, 'Unknown')
        ) as weather_key,

        weather_condition,
        wind_direction

    from distinct_weather

)

select * from final_dim