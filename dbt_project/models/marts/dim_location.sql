{{ config(
    materialized='table'
) }}

with staging as (
    select * from {{ ref('stg_us_accidents') }}
),

-- 1. التجهيز والتوحيد
cleaned_data as (
    select
        coalesce(street, 'Unknown') as street,
        coalesce(city, 'Unknown') as city,
        coalesce(county, 'Unknown') as county,
        coalesce(state_code, 'Unknown') as state_code,
        coalesce(zipcode, 'Unknown') as zipcode,
        
        -- تحويل الجغرافيا لنص ثابت عشان المقارنة
        ST_ASTEXT(geo_point) as geo_text,
        geo_point
    from staging
    where geo_point is not null
),

-- 2. إزالة التكرار "بالعافية" (Forced Deduplication)
deduplicated_locations as (
    select 
        *,
        -- بنرقم الصفوف المتشابهة
        ROW_NUMBER() OVER (
            PARTITION BY street, city, county, state_code, zipcode, geo_text 
            ORDER BY street
        ) as rn
    from cleaned_data
),

final_dim as (
    select
        -- نفس معادلة الهاش بالظبط
        md5(
            street || '-' ||
            city || '-' ||
            county || '-' ||
            state_code || '-' ||
            zipcode || '-' ||
            geo_text
        ) as location_key,

        street,
        city,
        county,
        state_code,
        zipcode,
        
        ST_Y(TO_GEOGRAPHY(geo_text)) as latitude,
        ST_X(TO_GEOGRAPHY(geo_text)) as longitude
        
        --,TO_GEOGRAPHY(geo_text) as geo_point

    from deduplicated_locations
    WHERE rn = 1  -- ⚠️ هنا السر: بناخد نسخة واحدة بس من المكان
)

select * from final_dim