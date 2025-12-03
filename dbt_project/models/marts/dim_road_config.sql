{{ config(
    materialized='table'
) }}

/*
    DIM_ROAD_CONFIG (Standardized with MD5)
    Goal: Junk Dimension with deterministic Hash Keys.
*/

with staging as (

    select * from {{ ref('stg_us_accidents') }}

),

distinct_combinations as (

    -- Select distinct combinations of the 9 road flags
    select distinct
        is_amenity,
        is_bump,
        is_crossing,
        is_junction,
        is_railway,
        is_station,
        is_stop,
        is_traffic_signal,
        is_turning_loop
    from staging

)

select
    -- Generating Surrogate Key using MD5 (Unified Method) 🔑
    -- Concatenating all flags to create a unique fingerprint
    md5(
        coalesce(cast(is_amenity as varchar), 'false') || '-' ||
        coalesce(cast(is_bump as varchar), 'false') || '-' ||
        coalesce(cast(is_crossing as varchar), 'false') || '-' ||
        coalesce(cast(is_junction as varchar), 'false') || '-' ||
        coalesce(cast(is_railway as varchar), 'false') || '-' ||
        coalesce(cast(is_station as varchar), 'false') || '-' ||
        coalesce(cast(is_stop as varchar), 'false') || '-' ||
        coalesce(cast(is_traffic_signal as varchar), 'false') || '-' ||
        coalesce(cast(is_turning_loop as varchar), 'false')
    ) as road_config_key,

    -- The columns
    is_amenity,
    is_bump,
    is_crossing,
    is_junction,
    is_railway,
    is_station,
    is_stop,
    is_traffic_signal,
    is_turning_loop

from distinct_combinations