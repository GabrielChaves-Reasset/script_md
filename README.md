# Pipeline PDF → Markdown

Script Python para filtrar páginas de um PDF com base em nomes de uma planilha Excel e converter para Markdown.

## Funcionalidades

1. **Filtrar PDF**: Mantém apenas páginas que contêm nomes listados em um Excel
2. **Converter para Markdown**: Extrai tabelas e texto do PDF filtrado

## Dependências

```bash
pip install pymupdf pandas openpyxl
```

## Uso

1. Configure os caminhos no início do arquivo `pipeline_unificada.py`
2. Execute:

```bash
python pipeline_unificada.py
```

## Arquivos

- `pipeline_unificada.py` - Script principal com a pipeline otimizada
