import duckdb
conn = duckdb.connect('dev.duckdb')

result = conn.execute("""
    SELECT * FROM 
    git status
    LIMIT 10
""").fetchdf()

print(result)