import os 
from pypdf import PdfReader

#Configuracao dos diretorios relativos
#BASE_DIR = os.path.join(os.path.dirname(__file__),"..","..")
BASE_DIR = os.getcwd()
BRONZE_DIR = os.path.join(BASE_DIR,"data_lake","bronze")

def extract_text_from_pdf(pdf_path):
    #Read pdf file e extract data_lake
    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
                
        return full_text
         
    except Exception as e:
        print(f"Error - Reading PDF file {pdf_path}:{e}")
        return None
        
def run_ingestion():
    print("Starting ingestion on bronze layer")
    
    if not os.path.exists(BRONZE_DIR):
        print(f"Error - Path {BRONZE_DIR} not found")
        return
    
    #List files on Bronze folder
    files = os.listdir(BRONZE_DIR)
    
    #Only pdf files, ignoring Case and files like .gitkeep
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("Bronze files not found")
        return
    
    print(f"{len(pdf_files)}Files found to proccess")
    
    for pdf_name in pdf_files:
        pdf_path = os.path.join(BRONZE_DIR,pdf_name)
        print(f"Reading file: {pdf_name}")
        
        extract_text = extract_text_from_pdf(pdf_path)
        
        if extract_text:

            #extracting text from original pdf
            #Keeps the exact same name as original file, only changing the file extension
            #example: 'NotaCorretagem_Rico_123.pdf' vira 'NotaCorretagem_Rico_123.txt'
            
            
            txt_name = os.path.splitext(pdf_name)[0] + ".txt"
            txt_path= os.path.join(BRONZE_DIR,txt_name)
            
            #Save the raw text on bronze path
            with open(txt_path,"w", encoding="utf-8") as f:
                f.write(extract_text)
                
            print(f"=== Text successfully extracted and saved to:{txt_name} ===")
        else:
            print(f"=== Failed to extract text from file: {txt_name} ===")
            
if __name__ == "__main__":
    run_ingestion()
    
                
