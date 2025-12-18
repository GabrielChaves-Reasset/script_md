import pdfplumber
import pandas as pd
import os
from pypdf import PdfReader, PdfWriter

pdf_path = r'c:\Pyton\Aula\teste\0079104-04.2001.8.26.0100.pdf'
excel_path = r'c:\Pyton\Aula\teste\nome_transbrasil.xlsx'
output_pdf_path = r'c:\Pyton\Aula\teste\Resultados\0079104-04.2001.8.26.0100_reduzido.pdf'

def create_filtered_pdf(pdf_path, excel_path, output_path):
    print("Reading Excel file...")
    try:
        df = pd.read_excel(excel_path)
        # Column name discovered: NOME_QGC
        possible_cols = [c for c in df.columns if 'nome' in c.lower()]
        if 'NOME_QGC' in df.columns:
            name_col = 'NOME_QGC'
        elif possible_cols:
            name_col = possible_cols[0]
        else:
            print("Could not find a 'Nome' column. Available columns:", df.columns.tolist())
            return

        names = df[name_col].dropna().astype(str).tolist()
        names = [n.strip() for n in names if len(n.strip()) > 3] # Filter out short noise
        print(f"Found {len(names)} names to search.")
        
    except Exception as e:
        print(f"Error reading Excel: {e}")
        return

    pages_to_keep = []
    
    print("Scanning PDF pages (this may take a while)...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages):
                if (i+1) % 50 == 0:
                    print(f"Scanning page {i+1}/{total_pages}...")
                
                text = page.extract_text()
                if not text:
                    continue
                
                text_upper = text.upper()
                for name in names:
                    if name.upper() in text_upper:
                        pages_to_keep.append(i)
                        break 
                        
        print(f"Found {len(pages_to_keep)} pages containing names.")
        
        if not pages_to_keep:
            print("No pages found with the specified names.")
            return

        print("Creating new PDF...")
        reader = PdfReader(pdf_path)
        writer = PdfWriter()
        
        for page_num in pages_to_keep:
            writer.add_page(reader.pages[page_num])
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        print(f"Successfully created: {output_path}")
        
    except ImportError:
        print("Error: pypdf not installed. Please install it using 'pip install pypdf'")
    except Exception as e:
        print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    if os.path.exists(pdf_path) and os.path.exists(excel_path):
        create_filtered_pdf(pdf_path, excel_path, output_pdf_path)
    else:
        print("Input files not found.")
