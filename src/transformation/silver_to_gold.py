import pandas as pd
from pathlib import Path

debug = 0

df_silver = pd.read_parquet(
    "data_lake/silver/transactions.parquet"
)

df_silver["trading_date"] = pd.to_datetime(df_silver["trading_date"])

if debug ==1:
    print(df_silver.head(100))

    print(df_silver.shape)


# generate a dataframe [[]]]
# drop duplicate data, sorting by brokerage and reseting the index 
dim_brokerage = (
    df_silver[["brokerage"]]
    .drop_duplicates()
    .sort_values("brokerage")
    .reset_index(drop=True)
)

dim_asset = (
    df_silver[["asset"]]
        .drop_duplicates()
        .sort_values("asset")
        .reset_index(drop=True)
)

dim_operation=(
    df_silver[["operation"]]
        .drop_duplicates("operation")
        .sort_values("operation")
        .reset_index(drop=True)
)

dim_date=(
    df_silver[["trading_date"]]
        .drop_duplicates("trading_date")
        .sort_values("trading_date")
        .reset_index(drop=True)
)

#dim_date["trading_date"] = pd.to_datetime(dim_date["trading_date"])

dim_date["year"] = dim_date["trading_date"].dt.year
dim_date["month"] = dim_date["trading_date"].dt.month
dim_date["day"] = dim_date["trading_date"].dt.day
dim_date["quarter"] = dim_date["trading_date"].dt.quarter
dim_date["date_key"]= (
    dim_date["trading_date"]
    .dt.strftime("%Y%m%d")
    .astype(int)
)

#generating the surrogate_key
#the index will start on 1(one) 
dim_brokerage["brokerage_key"] = dim_brokerage.index + 1

dim_asset["asset_key"]= dim_asset.index+1

dim_operation["operation_key"] = dim_operation.index + 1

mapping = {
    "S":"Sell",
    "B":"Buy"
}

dim_operation["operation_description"] = dim_operation["operation"].map(mapping)

#create the dataframe with the two coluns: brokerage_key and brokerage
dim_brokerage = dim_brokerage[
    ["brokerage_key","brokerage"]
]

dim_asset = dim_asset[
    ["asset_key", "asset"]
]

dim_operation = dim_operation[
    ["operation_key", "operation", "operation_description"]
]

dim_date = dim_date[
    ["date_key", "trading_date","year","month", "day","quarter"]
]
    
print("========================= dim_brokerage =======================================")
print(dim_brokerage)

print("========================= dim_asset =======================================")
print(dim_asset)

print("========================= dim_operation =======================================")
print(dim_operation)


print("========================= dim_date =======================================")
print(dim_date)

gold_dir = Path("data_lake/gold")
gold_dir.mkdir(parents=True, exist_ok=True)

dim_brokerage.to_parquet(
    gold_dir / "dim_brokerage.parquet",
    index=False
)

dim_asset.to_parquet(
    gold_dir / "dim_asset.parquet",
    index=False
)

dim_operation.to_parquet(
    gold_dir / "dim_operation.parquet",
    index = False
 )
 
dim_date.to_parquet(
    gold_dir / "dim_date.parquet",
    index=False
)
 
fact_trades = df_silver.copy()
 
 #left join dataframe silver with dimension brokerage
fact_trades = fact_trades.merge(
    dim_brokerage,
    on = "brokerage",
    how="left"
)
 
 #left join dataframe silver with dimention asset
fact_trades = fact_trades.merge(
    dim_asset,
    on = "asset",
    how = "left"
)
 
 #left join dataframe silver with dimention operation
fact_trades=fact_trades.merge(
    dim_operation,
    on="operation",
    how="left"
)

#left join dataframe silver with dimention date
fact_trades=fact_trades.merge(
    dim_date,
    on="trading_date",
    how="left"
)

fact_trades = fact_trades[
    [
        "source_file",
        "trading_date",
        "date_key",
        "year",
        "month",
        "day",
        "quarter",
        "brokerage", 
        "operation", 
        "asset", 
        "quantity",
        "unit_price",
        "gross_value",
        "settlement_fee",
        "emoluments", 
        "brokerage_fee", 
        "asset_transfer_fee", 
        "total_fees", 
        "weight", 
        "allocated_settlement_fee", 
        "allocated_emoluments", 
        "allocated_brokerage_fee", 
        "allocated_asset_transfer_fee", 
        "allocated_total_fees", 
        "total_cost", 
        "brokerage_key", 
        "asset_key", 
        "operation_key", 
        "operation_description"
        ]
]
    
 
print("========================= fact_trades =======================================")
print(fact_trades.columns.tolist())


#print(dim_brokerage.columns.tolist())
print("*********************************")
#print(dim_asset.columns.tolist())
print(dim_date.columns.tolist())
#print(fact_trades.shape)
#print(fact_trades[["brokerage", "brokerage_key", "asset", "asset_key", "operation", "operation_key"]].drop_duplicates())