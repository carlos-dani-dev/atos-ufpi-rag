import fitz
import camelot
import pandas as pd
import os # Importação mantida, embora não usada no snippet


if __name__ == "__main__":
    for ano in [2021, 2022, 2023, 2024, 2025]:
        lista_de_dfs = []
        for ato in os.listdir("atos"):
            ano_file = ato.split("_")[0]
            
            if int(ano_file) != ano: continue
            
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

            """
            if ano == 2020 or ano == 2021 or ano == 2022 or ano == 2023 or ano == 2024:
                for i, tabela_atual in enumerate(lista_tabelas_camelot):
                    print(f"\n--- Tabela {i+1} ---")
                    
                    df_atual = tabela_atual.df
                    
                    print(df_atual.head())
                    
                    if len(df_atual.columns) > 3: df_atual = df_atual.loc[:, :2]
                    
                    lista_de_dfs.append(df_atual)
            """
            if ano == 2025:
                for i, tabela_atual in enumerate(lista_tabelas_camelot):
                    print(f"\n--- Tabela {i+1} ---")
                    
                    df_atual = tabela_atual.df
                    print(df_atual.head())
                    
                    lista_de_dfs.append(df_atual)
                
        tabela_final = pd.concat(lista_de_dfs, ignore_index=True)
        print(tabela_final.columns)
        print(tabela_final.head())
        tabela_final.columns = ["Ato", "Data", "Envolvidos", "Texto"]

        nome_arquivo_csv = f"./atos_csv/atos_{ano}.csv"
        nome_arquivo_excel = f"./atos_excel/atos_{ano}.xlsx"

        tabela_final.to_csv(nome_arquivo_csv, index=False, encoding='utf-8')
        tabela_final.to_excel(nome_arquivo_excel)

        print("\n-------------------------------------")
        print(f"Total de linhas na tabela final: {len(tabela_final)}")
        print(f"Arquivo .csv final salvo como: {nome_arquivo_csv}")
        print(f"Arquivo .xlsx final salvo como: {nome_arquivo_excel}")