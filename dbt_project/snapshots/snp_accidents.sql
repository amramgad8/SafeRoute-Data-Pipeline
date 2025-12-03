{% snapshot snp_accidents %}

{{
    config(
      target_schema='snapshots',
      unique_key='ID',
      strategy='check',
      check_cols=['Severity', 'Description', 'City']
    )
}}

select * from {{ source('raw_data', 'US_ACCIDENTS_RAW') }}

{% endsnapshot %}