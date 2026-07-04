import duckdb
conn = duckdb.connect('dev.duckdb')

result = conn.execute("""
    SELECT * FROM 
    fact_trades
    LIMIT 10
""").fetchdf()

print(result)