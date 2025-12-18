import pandas as pd
import sys

excel_path = r'c:\Pyton\Aula\teste\nome_transbrasil.xlsx'
try:
    df = pd.read_excel(excel_path)
    print("Columns:", df.columns.tolist())
    print("First 5 rows:")
    print(df.head())
    print("Total rows:", len(df))
except Exception as e:
    print(f"Error reading Excel: {e}")
