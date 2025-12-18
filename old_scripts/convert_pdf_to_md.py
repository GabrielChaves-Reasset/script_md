import pdfplumber
import pandas as pd
import os

pdf_path = r'c:\Pyton\Aula\teste\Resultados\0079104-04.2001.8.26.0100_reduzido.pdf'
md_path = r'c:\Pyton\Aula\teste\Resultados\0079104-04.2001.8.26.0100_reduzido.md'

def clean_headers(headers):
    """
    Deduplicate headers by appending _1, _2, etc. to duplicates.
    Also handle None or empty strings.
    """
    seen = {}
    new_headers = []
    for h in headers:
        h = str(h).strip() if h is not None else ""
        if not h:
            h = "Unnamed"
        if h in seen:
            seen[h] += 1
            new_headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 0
            new_headers.append(h)
    return new_headers

def convert_pdf_to_md(pdf_file, md_file):
    print(f"Opening PDF: {pdf_file}")
    
    with open(md_file, "w", encoding="utf-8") as f:
        f.write("# PDF Content\n\n")
        
        try:
            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)
                print(f"Total pages: {total_pages}")
                
                for i, page in enumerate(pdf.pages):
                    print(f"Processing page {i+1}/{total_pages}...")
                    f.write(f"## Page {i+1}\n\n")
                    
                    tables = page.extract_tables()
                    if tables:
                        for table in tables:
                            # Filter empty tables
                            if not table: 
                                continue
                                
                            try:
                                # Assume first row is header if valid
                                if len(table) > 1:
                                    headers = clean_headers(table[0])
                                    rows = table[1:]
                                    df = pd.DataFrame(rows, columns=headers)
                                    markdown_table = df.to_markdown(index=False)
                                    f.write(markdown_table + "\n\n")
                                else:
                                    # Single row or simple list
                                    df = pd.DataFrame(table)
                                    markdown_table = df.to_markdown(index=False, headers="keys") # Use default indices if no header
                                    f.write(markdown_table + "\n\n")
                            except Exception as e:
                                print(f"Error creating table on page {i+1}: {e}")
                                # Fallback to text if table fails
                                text = page.extract_text()
                                if text:
                                    f.write(text + "\n\n")
                    else:
                        text = page.extract_text()
                        if text:
                           f.write(text + "\n\n")
                        else:
                            f.write("*No content extracted*\n\n")
                            
            print(f"Successfully created: {md_file}")

        except Exception as e:
            print(f"Error processing PDF: {e}")

if __name__ == "__main__":
    if os.path.exists(pdf_path):
        convert_pdf_to_md(pdf_path, md_path)
    else:
        print(f"File not found: {pdf_path}")
