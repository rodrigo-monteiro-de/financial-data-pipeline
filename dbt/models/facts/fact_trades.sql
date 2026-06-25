SELECT 
	DATE(trading_date) AS trade_date,
	asset,
	SUM(quantity) AS qtt
FROM {{ref('stg_transactions')}}
GROUP BY 1,2