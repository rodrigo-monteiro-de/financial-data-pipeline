SELECT 
    f.trade_id,
    d.trading_date,
    a.asset,
    o.operation,
    f.quantity,
    f.unit_price,
    f.gross_value,
    f.allocated_settlement_fee,
    f.allocated_emoluments,
    f.allocated_brokerage_fee,
    f.allocated_asset_transfer_fee,
    f.allocated_total_fees,
    f.allocated_total_cost
FROM {{ref('fact_trades')}} f
LEFT JOIN {{ref('dim_date')}} d
    ON f.date_key = d.date_key
LEFT JOIN {{ref('dim_operation')}} o
    ON f.operation_key = o.operation_key
LEFT JOIN {{ref('dim_asset')}} a
    ON f.asset_key = a.asset_key
