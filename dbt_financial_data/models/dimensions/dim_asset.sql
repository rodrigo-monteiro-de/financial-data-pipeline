{{config(
    materialized='incremental', 
    unique_key='asset'
    )
}}

WITH source AS(
    SELECT DISTINCT 
        asset
    FROM {{ref('stg_transactions')}}
)

SELECT 
    {{dbt_utils.generate_surrogate_key(['s.asset'])}} AS asset_key,
    s.asset
FROM source s
LEFT JOIN {{this}} d
    ON s.asset = d.asset

{% if is_incremental() %}

WHERE d.asset IS NULL

{% endif %}
