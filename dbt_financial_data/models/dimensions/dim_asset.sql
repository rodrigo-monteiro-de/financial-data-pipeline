{{config(materialized='incremental', unique_key='asset')}}

SELECT 
    ROW_NUMBER() OVER(ORDER BY s.asset)  +
    COALESCE((SELECT MAX(asset_key) FROM {{this}}), 0) AS asset_key,
    s.asset,
FROM {{ref('stg_transactions')}} s
{% if is_incremental() %}
LEFT JOIN {{this}} d
    ON s.asset = d.asset
WHERE d.asset IS NULL
{% endif %}
GROUP BY s.asset
