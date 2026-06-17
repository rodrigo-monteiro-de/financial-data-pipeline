import os
import re
import json

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
        if "INTER" in line:
            brokerage = "INTER"
        if "RICO" in line:
            brokerage = "RICO"
            
        if "Data pregão" in line:
            # take the next line wich contains the trading date
            trading_date = parse_date(lines[i+1])
            

    if not brokerage or not trading_date:
        print(f"Brokerage or trading date not found")
        return []
    
    print(f"===== {source_file} ======")
    print(f"Extacting transactions | brokerage:{brokerage}| Trading date:{trading_date}")
    
    transactions = []
            
    #Second step: capture the transactions based on brokerage
    for idx,line in enumerate(lines):
            
        #PARSER - INTER
        if brokerage == "INTER" and line.startswith("Bovespa"):
            # Ex: Bovespa VISV 50 98.47 4,923.50 CDRN MICROSOFT (note: may or may not have D/C explicitly at the end)
            # Let's use a flexible regex to capture the blocks of numbers and the final text
            match = re.search(r"Bovespa\s+\w+\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+(.*?)(?:\s+([DC]))?$", line)
            
            if match:
                qtt = int(match.group(1))
                unit_price = clean_float(match.group(2))
                gross_value = clean_float(match.group(3))
                asset = match.group(4).strip()
               
                #print("ANTES:", repr(asset))
                asset = " ".join(asset.split())
                #print("DEPOIS:", repr(asset))
                
                dc_indicator = match.group(5) if match.group(5) else "C" # Default if not located on line
                
                operation = "B" if dc_indicator == "D" else "S" # D = Debit (Buy/B), C = Credit (Sell/S)
                
                transactions.append({
                
                "source_file": source_file,
                "trading_date":trading_date,
                "brokerage":brokerage,
                "operation":operation,
                "asset":asset,
                "quantity":qtt,
                "unit_price":unit_price,
                "gross_value":gross_value
                })
            
        #PARSER - RICO
        if brokerage == "RICO" and line in ["VISTA", "FRACIONARIO"]:
            cursor = idx + 1
            
            while cursor < len(lines):
                if re.fullmatch(r"\d+", lines[cursor].strip()):
                    break
                    
                cursor += 1
                
            if cursor >= len(lines):
                continue
                
            '''print("\n===== ATIVO RICO =====")
            for i in range(idx-4, idx+1):
                if i >= 0:
                    print(i, "|", lines[i])'''
            
            # Group the next lines  processing the number values by Regex 
            
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
            
            print(
                f"-----> asset={asset}, \n  ------ qtt={qtt}, "
                f"\n  ------ unit_price={unit_price}, "
                f"\n  ------ gross_value={gross_value},"
                f"\n  ------ debit/credit={dc_indicator}"
            )
            
            
            '''if lines[idx-1].strip() in ["N1", "N2", "NM", "EDJ", "EJ"]:
                #print("DEBUG --> caiu no IF")
                active_line = lines[idx-2].strip()
                if len(active_line.strip()) == 2:#"ED":
                    active_line = lines[idx-3].strip()
                print(f"Active_line: {active_line}")
            else:
                print("DEBUG --> caiu no ELSE")
                active_line = lines[idx-1].strip()
                print(f"Active_line: {active_line}")'''
           
            
            #print("ANTES:", repr(asset))
            #asset = " ".join(asset.split())

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
            
            #print("ASSET FINAL:", asset)
                
    settlement_fee = 0.0
    emoluments = 0.0
    brokerage_fee = 0.0
    asset_transfer_fee = 0.0

    if brokerage == "INTER":
        for idx, line in enumerate(lines):
            if "Valor líquido das operações" in line:
                if idx + 8 < len(lines): settlement_fee = clean_float(lines[idx+8])
            if "Emolumentos" in line:
                for offset in range(1, 10):
                    if idx + offset < len(lines) and "Total" in lines[idx+offset]:
                        emoluments = clean_float(lines[idx+offset].replace("Total", "").replace("D", "").replace("C", "").strip())
                        break
            if "Corretagem / Despesas" in line:
                for offset in range(1, 10):
                    if idx + offset < len(lines) and "Total" in lines[idx+offset]:
                        brokerage_fee = clean_float(lines[idx+offset].replace("Total", "").replace("D", "").replace("C", "").strip())
                        break
        for t in transactions:
            t["costs"] = {"settlement_fee": settlement_fee, "emoluments": emoluments, "brokerage_fee": brokerage_fee}

    if brokerage == "RICO":
        for idx, line in enumerate(lines):
            if "Taxa de Transf. de Ativos" in line:
                #settlement_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                asset_transfer_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                        
            if "Emolumentos" in line:
                emoluments = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())
                
            if "Taxa de liquidação" in line:
                settlement_fee = clean_float(lines[idx-1].replace("D", "").replace("C", "").strip())     
                #print("settlement_fee")
                #print(settlement_fee)
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
                    #transaction["total_cost"]= transaction["gross_value"] + transactiom[ #transaction["total_fees"]
                    
                    #print("===== transaction['total_cost'] =====")
                    #print(transaction["total_cost"])
                    
                    all_transactions.append(transaction)
                    
        df_silver = pd.DataFrame(all_transactions)
        
        #debug - asset 
        for asset in df_silver["asset"]:
            #print("===== ATIVO =====")
            #print(repr(asset))
        
            if len(all_transactions) == 0:
                raise Exception(
                    "No transactions found. Check if Bronze contains TXT files."
                )
        
        # ==========================================
        # Temporary fee allocation validation
        # ==========================================

        df_silver["weight"] = 0.0
        df_silver["allocated_settlement_fee"] = 0.0
        df_silver["allocated_emoluments"] = 0.0
        df_silver["allocated_brokerage_fee"] = 0.0
        df_silver["allocated_asset_transfer_fee"] = 0.0
        df_silver["allocated_total_fees"] = 0.0

        # ==========================================
        # End temporary validation
        # ==========================================     
        
        for source_file, group in df_silver.groupby("source_file"):
            gross_total = group["gross_value"].sum()

            #print(f"\n===== {source_file} =====")
            #print(f"Gross Total: {gross_total}")
            
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
                
                df_silver.loc[idx,"total_cost"]=(
                    df_silver.loc[idx, "gross_value"]
                    + df_silver.loc[idx,"allocated_total_fees"]
                )
        
        os.makedirs(silver_dir,exist_ok=True)
        parquet_path = os.path.join(silver_dir,"transactions.parquet")
        
        df_silver = df_silver.sort_values(by=['trading_date','source_file',  'asset'], ascending=[True, True,True])
        
        df_silver.to_parquet(parquet_path,index=False)
        
        print(f"\n=== Silver layer successfully recorded on:: {parquet_path} ===")
        
        print("\n=== Visualization - Silver data ===")
        
        print(df_silver.to_string()) # Show the complete structured table on terminal
    else:
        print(f"Directory {bronze_dir} not found")