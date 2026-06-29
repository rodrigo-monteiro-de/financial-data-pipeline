{{config(
    materialized='incremental', 
    unique_key='brokerage'
    )
}}

WITH source AS(
    SELECT DISTINCT 
        brokerage
    FROM {{ref('stg_transactions')}}
)

SELECT 
    {{dbt_utils.generate_surrogate_key(['s.brokerage'])}} AS brokerage_key,
    s.brokerage
FROM source s

{% if is_incremental() %}

LEFT JOIN {{this}} d
    ON s.brokerage = d.brokerage

WHERE d.brokerage IS NULL

{% endif %}
