import fitz
import camelot
import pandas as pd
import os # Importação mantida, embora não usada no snippet



lista_de_dfs_2025 = []
for ato in os.listdir("atos"):
    ano = ato.split("_")[0]
    
    if int(ano) != 2025: continue
    
    mes = ato.split("_")[1]
    
    print(f"Ano: {ano} e Mês: {mes}")
    
    filepath = f"./atos/{ato}"

    doc = fitz.open(filepath)
    num_pages = doc.page_count
    doc.close()

    lista_tabelas_camelot = camelot.read_pdf(
        filepath, 
        pages=f"2-{num_pages}", 
        flavor='lattice'
    )

    print(f"Número de tabelas encontradas: {lista_tabelas_camelot.n}")

    for i, tabela_atual in enumerate(lista_tabelas_camelot):
        print(f"\n--- Tabela {i+1} ---")
        
        df_atual = tabela_atual.df 
        print(df_atual.head())
        
        lista_de_dfs_2025.append(df_atual) 
        
tabela_final = pd.concat(lista_de_dfs_2025, ignore_index=True)
tabela_final.columns = ["Ato", "Data", "Envolvido", "Texto"]

nome_arquivo_csv = "atos_2025.csv"
nome_arquivo_excel = "atos_2025.xlsx"

tabela_final.to_csv(nome_arquivo_csv, index=False, encoding='utf-8')
tabela_final.to_excel("atos_2025.xlsx")

print("\n-------------------------------------")
print(f"Total de linhas na tabela final: {len(tabela_final)}")
print(f"Arquivo .csv final salvo como: {nome_arquivo_csv}")
print(f"Arquivo .xlsx final salvo como: {nome_arquivo_excel}")