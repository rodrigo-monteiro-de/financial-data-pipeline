{{config(
    materialized='incremental',
    unique_key='operation'
)}}

WITH source AS(
    SELECT DISTINCT operation 
    FROM {{ref('stg_transactions')}}
)

    SELECT
        {{dbt_utils.generate_surrogate_key(['s.operation'])}} AS operation_key,
        s.operation
    FROM source s

    {%if is_incremental() %}

    LEFT JOIN {{this}} o
    ON s.operation = o.operation


    WHERE o.operation IS NULL

    {% endif %} 
    
