-- This test returns records where end_time is BEFORE start_time (Logic Error)
select
    accident_id,
    start_time,
    end_time
from {{ ref('stg_us_accidents') }}
where end_time < start_time