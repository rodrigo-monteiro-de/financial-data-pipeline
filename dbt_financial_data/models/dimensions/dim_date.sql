{{config(
    materialized='incremental',
    unique_key='trading_date'
)}}

WITH source AS(
    SELECT DISTINCT trading_date 
    FROM {{ref('stg_transactions')}}
)

    SELECT
        {{dbt_utils.generate_surrogate_key(['s.trading_date'])}} AS date_key,
        s.trading_date
    FROM source s

    {%if is_incremental() %}

    LEFT JOIN {{this}} o
    ON s.trading_date = o.trading_date

    WHERE o.trading_date IS NULL

    {% endif %} 
    
