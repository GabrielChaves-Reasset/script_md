"""
Pipeline Unificada OTIMIZADA: Filtrar PDF por Nomes e Converter para Markdown

Versão otimizada usando:
- pymupdf (fitz): 10-50x mais rápido que pdfplumber
- Regex compilado: busca eficiente de múltiplos nomes
- Processamento unificado: menos operações de I/O

Dependências:
    pip install pymupdf pandas openpyxl

Uso:
    python pipeline_unificada.py
"""

import fitz  # pymupdf
import pandas as pd
import os
import re
import time

# =============================================================================
# CONFIGURAÇÕES
# =============================================================================

PDF_ORIGEM = r'c:\Pyton\Aula\teste\0079104-04.2001.8.26.0100.pdf'
EXCEL_NOMES = r'c:\Pyton\Aula\teste\nome_transbrasil.xlsx'
PASTA_SAIDA = r'c:\Pyton\Aula\teste\Resultados'

os.makedirs(PASTA_SAIDA, exist_ok=True)

PDF_FILTRADO = os.path.join(PASTA_SAIDA, '0079104-04.2001.8.26.0100_reduzido.pdf')
MARKDOWN_SAIDA = os.path.join(PASTA_SAIDA, '0079104-04.2001.8.26.0100_reduzido.md')

# =============================================================================
# FUNÇÕES AUXILIARES
# =============================================================================

def carregar_nomes_do_excel(caminho_excel: str) -> list:
    """
    Carrega lista de nomes do Excel.
    
    Returns:
        Lista de nomes limpos (strings com mais de 3 caracteres)
    """
    print("[1] Carregando nomes do Excel...")
    
    df = pd.read_excel(caminho_excel)
    
    # Encontrar coluna de nomes
    if 'NOME_QGC' in df.columns:
        coluna = 'NOME_QGC'
    else:
        colunas_nome = [c for c in df.columns if 'nome' in c.lower()]
        if not colunas_nome:
            raise ValueError(f"Coluna de nomes não encontrada. Colunas: {df.columns.tolist()}")
        coluna = colunas_nome[0]
    
    nomes = df[coluna].dropna().astype(str).tolist()
    nomes = [n.strip() for n in nomes if len(n.strip()) > 3]
    
    print(f"    Coluna: '{coluna}' | Nomes: {len(nomes)}")
    return nomes


def criar_regex_nomes(nomes: list) -> re.Pattern:
    """
    Cria um regex compilado para buscar todos os nomes de uma vez.
    
    Muito mais eficiente que iterar nome por nome.
    """
    # Escapa caracteres especiais de regex nos nomes
    nomes_escapados = [re.escape(nome) for nome in nomes]
    # Cria pattern: (nome1|nome2|nome3|...)
    pattern = '(' + '|'.join(nomes_escapados) + ')'
    return re.compile(pattern, re.IGNORECASE)


def extrair_tabelas_da_pagina(page) -> str:
    """
    Tenta extrair tabelas de uma página usando pymupdf.
    
    Retorna texto formatado para Markdown ou string vazia.
    """
    try:
        # pymupdf pode encontrar tabelas
        tabs = page.find_tables()
        if tabs.tables:
            resultado = ""
            for tab in tabs.tables:
                df = tab.to_pandas()
                if not df.empty:
                    resultado += df.to_markdown(index=False) + "\n\n"
            return resultado
    except Exception:
        pass
    return ""


# =============================================================================
# PIPELINE PRINCIPAL OTIMIZADA
# =============================================================================

def executar_pipeline():
    """
    Executa toda a pipeline de forma otimizada.
    
    1. Carrega nomes do Excel
    2. Filtra PDF mantendo páginas com os nomes
    3. Converte páginas filtradas para Markdown
    
    Tudo em uma única passagem pelo PDF original.
    """
    inicio = time.time()
    
    print("=" * 60)
    print("  PIPELINE OTIMIZADA: PDF → Filtrado → Markdown")
    print("=" * 60)
    
    # --- Validar arquivos ---
    if not os.path.exists(PDF_ORIGEM):
        print(f"ERRO: PDF não encontrado: {PDF_ORIGEM}")
        return
    if not os.path.exists(EXCEL_NOMES):
        print(f"ERRO: Excel não encontrado: {EXCEL_NOMES}")
        return
    
    # --- Carregar nomes e criar regex ---
    try:
        nomes = carregar_nomes_do_excel(EXCEL_NOMES)
        regex_nomes = criar_regex_nomes(nomes)
    except Exception as e:
        print(f"ERRO ao carregar nomes: {e}")
        return
    
    # --- Processar PDF ---
    print(f"\n[2] Processando PDF: {os.path.basename(PDF_ORIGEM)}")
    
    doc_original = fitz.open(PDF_ORIGEM)
    doc_filtrado = fitz.open()  # Novo PDF vazio
    total_paginas = len(doc_original)
    
    print(f"    Total de páginas: {total_paginas}")
    
    paginas_encontradas = []
    conteudo_markdown = ["# Conteúdo do PDF Filtrado\n\n"]
    
    for i, pagina in enumerate(doc_original):
        # Progresso a cada 50 páginas
        if (i + 1) % 50 == 0:
            print(f"    Página {i + 1}/{total_paginas}...")
        
        texto = pagina.get_text()
        
        # Busca otimizada com regex
        if regex_nomes.search(texto):
            paginas_encontradas.append(i)
            
            # Adiciona página ao PDF filtrado
            doc_filtrado.insert_pdf(doc_original, from_page=i, to_page=i)
            
            # Gera conteúdo Markdown desta página
            conteudo_markdown.append(f"## Página {len(paginas_encontradas)}\n\n")
            
            # Tenta extrair tabelas primeiro
            tabelas_md = extrair_tabelas_da_pagina(pagina)
            if tabelas_md:
                conteudo_markdown.append(tabelas_md)
            else:
                # Fallback para texto puro
                if texto.strip():
                    conteudo_markdown.append(texto + "\n\n")
                else:
                    conteudo_markdown.append("*Nenhum conteúdo extraído*\n\n")
    
    doc_original.close()
    
    # --- Resultados ---
    print(f"\n[3] Páginas com nomes encontrados: {len(paginas_encontradas)}")
    
    if not paginas_encontradas:
        print("AVISO: Nenhuma página contém os nomes especificados.")
        doc_filtrado.close()
        return
    
    # --- Salvar PDF filtrado ---
    print(f"\n[4] Salvando PDF filtrado...")
    doc_filtrado.save(PDF_FILTRADO)
    doc_filtrado.close()
    print(f"    Salvo: {PDF_FILTRADO}")
    
    # --- Salvar Markdown ---
    print(f"\n[5] Salvando Markdown...")
    with open(MARKDOWN_SAIDA, "w", encoding="utf-8") as f:
        f.write("".join(conteudo_markdown))
    print(f"    Salvo: {MARKDOWN_SAIDA}")
    
    # --- Tempo total ---
    tempo_total = time.time() - inicio
    print("\n" + "=" * 60)
    print(f"  CONCLUÍDO em {tempo_total:.1f} segundos")
    print("=" * 60)


if __name__ == "__main__":
    executar_pipeline()
