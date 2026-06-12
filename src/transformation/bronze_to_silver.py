import os
import re
import json

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
    
    # O print agora fica no lugar certo (executa se achar os dados)
    print(f"Extacting transactions | brokerage:{brokerage}| Trading date:{trading_date}")
    
    transactions = []
            
    #Second step: capture the transactions based on brokerage
    for idx,line in enumerate(lines):
        
        #if brokerage == "RICO" and ("@" in line or "BOVESPA" in line):
            #print(f"[RAIO-X RICO] Linha {idx} na memória: '{line}'")
            
        #PARSER - INTER
        if brokerage == "INTER" and line.startswith("Bovespa"):
            # Ex: Bovespa VISV 50 98.47 4,923.50 CDRN MICROSOFT (note: may or may not have D/C explicitly at the end)
            # Let's use a flexible regex to capture the blocks of numbers and the final text
            match = re.search(r"Bovespa\s+\w+\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+(.*?)(?:\s+([DC]))?$", line)
            
            if match:
                qtt = int(match.group(1))
                unit_price = clean_float(match.group(2))
                total_value = clean_float(match.group(3))
                asset = match.group(4).strip()
                dc_indicator = match.group(5) if match.group(5) else "C" # Default if not located on line
                
                operation = "B" if dc_indicator == "D" else "S" # D = Debit (Buy/B), C = Credit (Sell/S)
                
                transactions.append({
                "trading_date":trading_date,
                "brokerage":brokerage,
                "operation":operation,
                "asset":asset,
                "quantity":qtt,
                "unit_price":unit_price,
                "total_value":total_value
                })
            
        #PARSER - RICO
        if brokerage == "RICO" and line == "@":
            # Junta as próximas linhas para o Regex processar os valores numéricos
            next_lines = lines[idx+1 : idx+5]
            combined_text = "@ " + " ".join(next_lines)
            
            match_valores = re.search(r"@\s*(\d+)\s*(\S+)\s*(\S+)\s*([DC])", combined_text)
            
            if match_valores:
                qtt = int(match_valores.group(1))
                unit_price = clean_float(match_valores.group(2))
                total_value = clean_float(match_valores.group(3))
                dc_indicator = match_valores.group(4)
                operation = "B" if dc_indicator == "D" else "S"
                
                # Resgata a linha de cima (Linha 16), onde está o ativo
                line_ativo = lines[idx-1].strip()
                
                # Isola o ativo: divide a linha por espaços
                parts = line_ativo.split()
                if parts:
                    # Se a linha termina com "CI", pega o elemento anterior (o Ticker)
                    # Caso contrário, pega a última palavra disponível
                    asset = parts[-2] if parts[-1] == "CI" and len(parts) > 1 else parts[-1]
                else:
                    asset = "ATIVO_NAO_ENCONTRADO"

                transactions.append({
                    "trading_date": trading_date,
                    "brokerage": brokerage,
                    "operation": operation,
                    "asset": asset,
                    "quantity": qtt,
                    "unit_price": unit_price,
                    "total_value": total_value
                })
                
        # Bloco de custos reindentado com 8 espaços (dentro da função process_bronze_file)
        settlement_fee = 0.0
        emoluments = 0.0
        brokerage_fee = 0.0

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
                if "Taxa de liquidação" in line:
                    for offset in range(1, 5):
                        if idx + offset < len(lines) and any(char.isdigit() for char in lines[idx+offset]):
                            settlement_fee = clean_float(lines[idx+offset].replace("D", "").replace("C", "").strip())
                            break
                if "Emolumentos" in line:
                    for offset in range(1, 5):
                        if idx + offset < len(lines) and any(char.isdigit() for char in lines[idx+offset]):
                            emoluments = clean_float(lines[idx+offset].replace("D", "").replace("C", "").strip())
                            break
                if "Corretagem" in line or "Execução" in line:
                    for offset in range(1, 5):
                        if idx + offset < len(lines) and any(char.isdigit() for char in lines[idx+offset]):
                            brokerage_fee = clean_float(lines[idx+offset].replace("D", "").replace("C", "").strip())
                            break
            for t in transactions:
                t["costs"] = {"settlement_fee": settlement_fee, "emoluments": emoluments, "brokerage_fee": brokerage_fee}

    return transactions
        
#execution fast test

if __name__ == "__main__":
    import pandas as pd
    
    #Using bronze path
    bronze_dir = "data_lake/bronze"
    silver_dir = "data_lake/silver"
    
    all_transactions = []
    
    
    #If the folder doesn't exist on your local test, switch to the correct path where you saved the .txt file
    if os.path.exists(bronze_dir):
        for file in os.listdir(bronze_dir):
            if file.endswith(".txt"):
                path = os.path.join(bronze_dir,file)
                data = process_bronze_file(path)
                
                #Group the costs structure
                for transaction in data:
                    costs=transaction.pop("costs",{})
                    transaction["settlement_fee"] = costs.get("settlement_fee",0.0)
                    transaction["emonuments"] = costs.get("emolument",0.0)
                    transaction["brokerate_fee"] = costs.get("brokerate_fee",0.0)
                    
                    all_transactions.append(transaction)
                    
        df_silver = pd.DataFrame(all_transactions)
        
        os.makedirs(silver_dir,exist_ok=True)
        parquet_path = os.path.join(silver_dir,"fact_transactions.parquet")
        
        df_silver.to_parquet(parquet_path,index=False)
        
        print(f"\n✨ Silver layer successfully recorded on:: {parquet_path}")
        
        print("\n--- Visualização dos dados na Silver ---")
        
        print(df_silver.to_string()) # Exibe a tabela completa estruturada no terminal
                
                #print(f"\n============ Default Output for {file} ============")
                #print(data)
                
                #print(f"\n============ JSON Output for {file} ============")
                #print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print(f"Directory {bronze_dir} not found")