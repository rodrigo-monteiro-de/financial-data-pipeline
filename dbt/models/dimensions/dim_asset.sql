SELECT DISTINCT 
	asset
FROM {{ref('stg_transactions)}}
ORDER BY asset
