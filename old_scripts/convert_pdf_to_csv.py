import pdfplumber
import pandas as pd
import os
import traceback

pdf_path = r'c:\Pyton\Aula\teste\0079104-04.2001.8.26.0100.pdf'
csv_path = r'c:\Pyton\Aula\teste\0079104-04.2001.8.26.0100.csv'

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

def convert_pdf_to_csv(pdf_file, csv_file):
    print(f"Opening PDF: {pdf_file}")
    all_table_dfs = []
    
    try:
        with pdfplumber.open(pdf_file) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total pages: {total_pages}")
            
            for i, page in enumerate(pdf.pages):
                if (i+1) % 10 == 0:
                    print(f"Processing page {i+1}/{total_pages}...")
                
                tables = page.extract_tables()
                for table in tables:
                    if not table:
                        continue
                    
                    # Assume first row is header
                    if len(table) > 1:
                        headers = clean_headers(table[0])
                        rows = table[1:]
                        try:
                            df = pd.DataFrame(rows, columns=headers)
                            all_table_dfs.append(df)
                        except Exception as e:
                            print(f"Warning: Could not create DataFrame for table on page {i+1}: {e}")
                    else:
                        # Single row table, treat as data without header or skip?
                        # Let's clean headers and treat as single row dataframe
                        # headers = clean_headers(table[0]) 
                        # Actually if it's 1 row, might be a header only or data only. 
                        # pdfplumber returns list of lists.
                        # We'll just append it as a simple dataframe with default columns if we can't determine headers.
                        # But for consistency with concat, we need headers.
                        # If we have previous tables, maybe align?
                        # For now, simplistic approach:
                        pass
                    
        if all_table_dfs:
            print(f"Found {len(all_table_dfs)} tables. Concatenating...")
            # Use sort=False to preserve order of columns if they differ
            final_df = pd.concat(all_table_dfs, ignore_index=True, sort=False)
            final_df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"Successfully converted tables to {csv_file}")
            print(f"Rows: {len(final_df)}")
        else:
            print("No structured tables found. Attempting text extraction fallback...")
            text_lines = []
            with pdfplumber.open(pdf_file) as pdf:
                 for page in pdf.pages:
                     text = page.extract_text()
                     if text:
                         text_lines.extend(text.split('\n'))
            
            if text_lines:
                df = pd.DataFrame(text_lines, columns=["Content"])
                df.to_csv(csv_file, index=False, encoding='utf-8-sig')
                print(f"No structured tables found. Extracted text lines to {csv_file}")
            else:
                 print("No text or tables found to extract.")
                 
    except Exception:
        print("Error during conversion:")
        traceback.print_exc()

if __name__ == "__main__":
    if os.path.exists(pdf_path):
        convert_pdf_to_csv(pdf_path, csv_path)
    else:
        print(f"File not found: {pdf_path}")
