import os
import re
import json

debug = 0

if debug == 1:
    print("=" * 70)
    print(">>> DEBUG --> Executing bronze to silver code! <<<")
    print("=" * 70)

def is_auxiliary_marker(text):
    return text in(
         "@", "@#", "N1", "N2", "NM", "ED", "EDJ", "EJ"
    )

def clean_float(value_str):
    #standardize currency to real (BR)
    if not value_str:
        return 0.0
    
    return float(value_str.replace(".","").replace(",",".").strip())

def parse_date(date_str):
    #standardize date in format DD/MM/YYYY to YYYY-MM-DD
    day,month,year = date_str.strip().split("/")
    return f"{year}-{month}-{day}"
    

def process_bronze_file(file_path):
    #save que file name
    source_file = os.path.basename(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]
    
    trading_date = None
    brokerage = None
    
    #First step: find out the trading day and wich brokerage it is
    for i,line in enumerate(lines):
        if "RICO" in line:
            brokerage = "RICO"
            
        if "Data pregão" in line:
            # take the next line wich contains the trading date
            trading_date = parse_date(lines[i+1])
            

    if not brokerage or not trading_date:
        print(f"Brokerage or trading date not found")
        return []
    
    if debug == 1:
        print("=" * 70)
        print(f"===== {source_file} ======")
        print(f"Extacting transactions | brokerage:{brokerage}| Trading date:{trading_date}")
        print("=" * 70)
    
    transactions = []
            
    #Second step: capture the transactions based on brokerage
    for idx,line in enumerate(lines):
            
        #PARSER - RICO
        if brokerage == "RICO" and line in ["VISTA", "FRACIONARIO"]:
            cursor = idx + 1
            
            while cursor < len(lines):
                if re.fullmatch(r"\d+", lines[cursor].strip()):
                    break
                    
                cursor += 1
                
            if cursor >= len(lines):
                continue
            
            if cursor + 3 >= len(lines):
                    continue
            
            qtt = int(lines[cursor].strip())
            unit_price = clean_float(lines[cursor+1].strip())
            gross_value = clean_float(lines[cursor+2].strip())
            dc_indicator = lines[cursor+3].strip()
            
            operation = "B" if dc_indicator == "D" else "S"
            
            asset_idx = cursor -1
            
            while (
                asset_idx >= 0
                and is_auxiliary_marker(lines[asset_idx].strip())
                ):
                asset_idx -= 1

            asset = " ".join(lines[asset_idx].split())

            if debug == 1: 
                print("=" * 70)                
                print(
                    f"-----> asset={asset}, \n  ------ qtt={qtt}, "
                    f"\n  ------ unit_price={unit_price}, "
                    f"\n  ------ gross_value={gross_value},"
                    f"\n  ------ debit/credit={dc_indicator}"
                    f"\n  ------ operation={operation}"
                )
                print("=" * 70)

            transactions.append({
                "source_file": source_file,
                "trading_date": trading_date,
                "brokerage": brokerage,
                "operation": operation,
                "asset": asset,
                "quantity": qtt,
                "unit_price": unit_price,
                "gross_value": gross_value
            })
                
    settlement_fee = 0.0
    emoluments = 0.0
    brokerage_fee = 0.0
    asset_transfer_fee = 0.0

    if brokerage == "RICO":
        for idx, line in enumerate(lines):
            if "Taxa de Transf. de Ativos" in line:
                #settlement_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                asset_transfer_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                        
            if "Emolumentos" in line:
                emoluments = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                
            if "Taxa de liquidação" in line:
                settlement_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())     
        for t in transactions:
            t["costs"] = {"settlement_fee": settlement_fee,  "asset_transfer_fee": asset_transfer_fee, "emoluments": emoluments, "brokerage_fee": brokerage_fee}

    return transactions
        
#execution fast test

if __name__ == "__main__":
    import pandas as pd
    
    #Using bronze path
    bronze_dir = "data_lake/bronze"
    silver_dir = "data_lake/silver"
    
    all_transactions = []

    #If the folder doesn't exist on local test, switch to the correct path where saved the .txt file
    if os.path.exists(bronze_dir):
        for file in os.listdir(bronze_dir):
            if file.endswith(".txt"):
                path = os.path.join(bronze_dir,file)
                data = process_bronze_file(path)
                
                #Group the costs structure
                for transaction in data:
                    costs=transaction.pop("costs",{})
                    transaction["settlement_fee"] = costs.get("settlement_fee",0.0)#+ costs.get("asset_transfer_fee",0.0)
                    transaction["emoluments"] = costs.get("emoluments",0.0)
                    transaction["brokerage_fee"] = costs.get("brokerage_fee",0.0)
                    transaction["asset_transfer_fee"] = costs.get("asset_transfer_fee",0.0)
                    transaction["total_fees"]= transaction["settlement_fee"] + transaction["emoluments"] + transaction["brokerage_fee"] + transaction["asset_transfer_fee"]
                    
                    all_transactions.append(transaction)
                    
        df_silver = pd.DataFrame(all_transactions)
        
        #debug - asset 
        for asset in df_silver["asset"]:
        
            if len(all_transactions) == 0:
                raise Exception(
                    "No transactions found. Check if Bronze contains TXT files."
                )

        df_silver["weight"] = 0.0
        df_silver["allocated_settlement_fee"] = 0.0
        df_silver["allocated_emoluments"] = 0.0
        df_silver["allocated_brokerage_fee"] = 0.0
        df_silver["allocated_asset_transfer_fee"] = 0.0
        df_silver["allocated_total_fees"] = 0.0 
        
        for source_file, group in df_silver.groupby("source_file"):
            gross_total = group["gross_value"].sum()
            
            for idx in group.index:
                
                weight = (
                    df_silver.loc[idx,"gross_value"]
                    / gross_total
                )
                
                df_silver.loc[idx,"weight"] = weight
                
                df_silver.loc[idx,"allocated_settlement_fee"] =(
                    df_silver.loc[idx,"settlement_fee"] * weight
                )
                
                df_silver.loc[idx, "allocated_emoluments"] = (
                            df_silver.loc[idx, "emoluments"] * weight
                        )

                df_silver.loc[idx, "allocated_brokerage_fee"] = (
                    df_silver.loc[idx, "brokerage_fee"] * weight
                )

                df_silver.loc[idx, "allocated_asset_transfer_fee"] = (
                    df_silver.loc[idx, "asset_transfer_fee"] * weight
                )

                df_silver.loc[idx, "allocated_total_fees"] = (
                    df_silver.loc[idx, "allocated_settlement_fee"]
                    + df_silver.loc[idx, "allocated_emoluments"]
                    + df_silver.loc[idx, "allocated_brokerage_fee"]
                    + df_silver.loc[idx, "allocated_asset_transfer_fee"]
                )
                
                if df_silver.loc[idx,"operation"] == "S":
                    df_silver.loc[idx,"total_cost"]=(
                        df_silver.loc[idx, "gross_value"]
                        - df_silver.loc[idx,"allocated_total_fees"]
                    )
                else:
                     df_silver.loc[idx,"total_cost"]=(
                        df_silver.loc[idx, "gross_value"]
                        + df_silver.loc[idx,"allocated_total_fees"]
                    )               
        
        os.makedirs(silver_dir,exist_ok=True)
        parquet_path = os.path.join(silver_dir,"transactions.parquet")
        
        df_silver = df_silver.sort_values(by=['trading_date','source_file',  'asset'], ascending=[True, True,True])
        
        df_silver.to_parquet(parquet_path,index=False)
        
        print("=" * 70)
        print("=" * 70)
        print(f"\n=== SUCCESS - Silver layer successfully recorded on: {parquet_path} ===")
        print("#" * 100)
        
        print("#" * 230)
        print("#"*100 ,  "VISUALIZATION - SILVER DATA", "#"*101)
        print("#" * 230)
        
        print(df_silver.to_string()) # Show the complete structured table on terminal
        print("#" * 230)
    else:
        print("=" * 70)
        print(f"Directory {bronze_dir} not found")
        print("=" * 70)