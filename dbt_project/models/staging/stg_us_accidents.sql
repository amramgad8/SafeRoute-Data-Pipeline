-- staging model for us accidents data
with source as (
    select * from {{ source('raw_data', 'US_ACCIDENTS_RAW') }}
),

cleaned_data AS (
    SELECT
        -- 1. Identifiers
        CAST(ID AS TEXT) AS accident_id,

        -- 2. Severity & Metrics
        TRY_TO_NUMBER(Severity) AS severity,
        TRY_TO_DOUBLE("DISTANCE(MI)") AS distance_miles,

        -- 3. Time & Duration & Derived Time Columns (Added Here) ➕
        TRY_TO_TIMESTAMP(Start_Time) AS start_time,
        TRY_TO_TIMESTAMP(End_Time) AS end_time,
        DATEDIFF('minute', TRY_TO_TIMESTAMP(Start_Time), TRY_TO_TIMESTAMP(End_Time)) AS duration_minutes,

        -- Extract Hour (0-23)
        DATE_PART(hour, TRY_TO_TIMESTAMP(Start_Time)) as hour_24,

        -- Calculate Part of Day based on Hour
        CASE 
            WHEN DATE_PART(hour, TRY_TO_TIMESTAMP(Start_Time)) BETWEEN 6 AND 11 THEN 'Morning'
            WHEN DATE_PART(hour, TRY_TO_TIMESTAMP(Start_Time)) BETWEEN 12 AND 16 THEN 'Afternoon'
            WHEN DATE_PART(hour, TRY_TO_TIMESTAMP(Start_Time)) BETWEEN 17 AND 20 THEN 'Evening' -- Rush Hour usually
            ELSE 'Night'
        END as part_of_day,

        -- 4. Location Details
        ST_MAKEPOINT(TRY_TO_DOUBLE(Start_Lng), TRY_TO_DOUBLE(Start_Lat)) as geo_point,
        
        COALESCE(CAST(Street AS TEXT), 'Unknown') AS street,
        COALESCE(CAST(City AS TEXT), 'Unknown') AS city,
        CAST(County AS TEXT) AS county,
        CAST(State AS TEXT) AS state_code,
        COALESCE(CAST(Zipcode AS TEXT), 'Unknown') AS zipcode,

        -- 5. Weather Conditions
        TRY_TO_DOUBLE("TEMPERATURE(F)") AS temperature_f,
        TRY_TO_DOUBLE("VISIBILITY(MI)") AS visibility_miles,
        COALESCE(TRY_TO_DOUBLE("WIND_SPEED(MPH)"), 0.0) AS wind_speed_mph,
        COALESCE(TRY_TO_DOUBLE("PRECIPITATION(IN)"), 0.0) AS precipitation_in,
        
        COALESCE(CAST(Weather_Condition AS TEXT), 'Unknown') AS weather_condition,
        COALESCE(CAST(Wind_Direction AS TEXT), 'Unknown') AS wind_direction,

        -- 6. Road Features
        TRY_TO_BOOLEAN(Amenity) AS is_amenity,
        TRY_TO_BOOLEAN(Bump) AS is_bump,
        TRY_TO_BOOLEAN(Crossing) AS is_crossing,
        TRY_TO_BOOLEAN(Junction) AS is_junction,
        TRY_TO_BOOLEAN(Railway) AS is_railway,
        TRY_TO_BOOLEAN(Station) AS is_station,
        TRY_TO_BOOLEAN(Stop) AS is_stop,
        TRY_TO_BOOLEAN(Traffic_Signal) AS is_traffic_signal,
        TRY_TO_BOOLEAN(Turning_Loop) AS is_turning_loop,

        -- 7. Day/Night Indicator
        CAST(Sunrise_Sunset AS TEXT) AS day_night_indicator

    FROM source
)

SELECT * FROM cleaned_data
WHERE start_time IS NOT NULL 
  AND severity IS NOT NULL