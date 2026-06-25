import duckdb

con = duckdb.connect()

fact_trades = """
SELECT 
    DATE(trading_date) as trade_date,
    asset,
    SUM(quantity) as qtt   
FROM 'data_lake/silver/transactions/*.parquet'
GROUP BY asset, DATE(trading_date)
"""

df_fact = con.execute(fact_trades).df()

schema = con.execute("""
    DESCRIBE 
    SELECT * 
    FROM 'data_lake/silver/transactions/*.parquet'
    LIMIT 10
""").df()

print("DF SILVER - VIEW")
print(schema)

print("\n=== DADOS ===")

data = con.execute("""
    SELECT * 
    FROM 'data_lake/silver/transactions/*.parquet'
    LIMIT 10
"""
).df()
print(data.columns.tolist())


df_fact.to_parquet("data_lake/gold/fact_trades.parquet")

print("Gold generated!")