import os
import re
import json

def clean_float(value_str):
    #standardize currency to real (BR)
    if not value_str:
        return 0.0
    
    return float(value_str.replace(".","").replace(",",".").strip())

def parse_date(date_st):
    #standardize date in format DD/MM/YYYY to YYYY-MM-DD
    day,month,year = date_str.strip().split("/")
    return f"{year}-{month}-{day}"
    

def process_bronze_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines= [line.strip() for line in f.readlines()]
    
    trading_date = None
    brokerage = None
    
        
    
    #First step: find out the trading day and wich brokerage it is
    for i,line in enumerate(lines):
        if "INTER DTVM LTDA" in line:
            brokerage = "INTER"
        if "RICO CORRETORA" in line:
            brokerage = "RICO"
            
        if "Data pregão" in line:
            # take the next line wich contains the trading date
            trading_date = parse_date(line[i+1])
            
            if not brokerage or not trading_date:
                print(f"Brokerage or trading date not found")
                return []
            
            print(f"Extacting transactions | brokerage:{brokerage}| Trading date:{trading_date}")
            transactions = []
            
            
            
    
    #Second step: capture the transactions based on brokerage
    for idx,line in enumerate(lines):
        #PARSER - INTER
        if brokerage == "INTER" and line.startswith("Bovespa"):
            # Ex: Bovespa VISV 50 98.47 4,923.50 CDRN MICROSOFT (note: may or may not have D/C explicitly at the end)
            # Let's use a flexible regex to capture the blocks of numbers and the final text
            match=re.search(r"Bovespa\s+\w+\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+(.*?)(?:\s+([DC]))?$", line)
            
            if match:
                qtt = int(match.group(1))
                unit_price= clean_float(match.group(2))
                value=clean_float(match.group(3))
                asset=match.group(4).strip()
                dc_indicator =match.group(5) if match.group(5) else "C" # Default if not located on line
                operation = "C" if dc_indicator == "D" else "V" # D = Debit (Buy), C = Credit (Sell)
                
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
        if brokerage="RICO" and "1-BOVESPA" in line:
            # Ex: 1-BOVESPA C VISTA FII REC RECE          RECR11          CI
            # The next line contains the values: @ 5 82,49 412,45 D
            next_line = line[idx+1] if idx + 1 < len(lines) else ""
            
            # Captures the Asset (usually before 'CI') and the direct Operation from line 1
            match_valores = re.search(r"@\s+(\d+)\s+([\d.,]+)\s+([\d.,]+)\s+([DC])", next_line)
            
            if match_valores:
                qtt = int(match_valores.group(1)
                unit_price = clean_float(match_valores.group(2))
                total_value = clean_float(match_valores.group(3))
                dc_indicator = match_valores.group(4)
               
               operation = "C" if dc_indicator == "D" else "V"
               # Extracts the Ticker/Asset by isolating what is between the market (VISTA/FRACIONARIO) and the end of the line
               # A simple way is to split the string or get the word that comes before "CI"
               
               line_parts= line.split()
               asset = line_parts[-2] if "CI" in line_parts else line_parts[-1]
               
               transactions.append[{
                "trading_date":trading_date,
                "brokerage":brokerage,
                "operation":operation,
                "asset":asset,
                "quantity":qtt,
                "unit_price":unit_price,
                "total_value":total_value
               }]
        return transactions
        
        #execution fast test
        
        if "__name__" == "__main__":
            #Using bronze path
            bronze_dir = "data_lake/bronze"
            
            #If the folder doesn't exist on your local test, switch to the correct path where you saved the .txt file
            if os.path.exists(bronze_dir):
                for file in os.path.exists(bronze_dir):
                    if file.bandswitch(".txt"):
                        path=os.path.join(bronze_dir,file)
                        data=process_bronze_file(path)
                        print(data)
                
            
    
    