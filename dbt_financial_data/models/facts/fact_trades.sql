{{config(
    materialized='incremental',
    unique_key='trade_id'
)}}

WITH source AS(
    SELECT
        trading_date,
        asset,
        operation,
        brokerage,
        quantity,
        unit_price,
        gross_value,
        allocated_settlement_fee,
        allocated_emoluments,
        allocated_brokerage_fee,
        allocated_asset_transfer_fee,
        allocated_total_fees,
        allocated_total_cost
    FROM {{ref('stg_transactions')}}
)

SELECT 
    -- fact surrogate_key -- avoiding duplication
    {{dbt_utils.generate_surrogate_key([
        's.trading_date',
        's.asset',
        's.operation',
        's.brokerage',
        's.unit_price',
        's.quantity',
        's.unit_price',
        's.gross_value',
        's.allocated_settlement_fee',
        's.allocated_emoluments',
        's.allocated_brokerage_fee',
        's.allocated_asset_transfer_fee',
        's.allocated_total_fees',
        's.allocated_total_cost'
    ]) }} AS trade_id,
    d.date_key,
    a.asset_key,
    o.operation_key,
    b.brokerage_key,
    s.unit_price,
    s.quantity,
    s.unit_price,
    s.gross_value,
    s.allocated_settlement_fee,
    s.allocated_emoluments,
    s.allocated_brokerage_fee,
    s.allocated_asset_transfer_fee,
    s.allocated_total_fees,
    s.allocated_total_cost
FROM source s

LEFT JOIN {{ref('dim_date')}} d
    ON s.trading_date = d.trading_date

LEFT JOIN {{ref('dim_operation')}} o
    ON s.operation = o.operation

LEFT JOIN {{ref('dim_asset')}} a
    ON s.asset = a.asset

LEFT JOIN {{ref('dim_brokerage')}} b
    ON s.brokerage = b.brokerage
 
