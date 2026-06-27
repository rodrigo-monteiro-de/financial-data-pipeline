SELECT
    asset,
    operation,
    quantity,
    unit_price,
    gross_value,
    trading_date
FROM {{ref('stg_transactions')}}