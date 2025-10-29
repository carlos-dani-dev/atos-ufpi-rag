import pandas as pd
import numpy as np

if __name__ == "__main__":
    
    df = pd.read_excel("atos_2025.xlsx")
    atos = []
    i = 0
    
    while i < len(df):
        line = df.iloc[i]
        nmr_ato = line["Ato"]

        # Ignora linhas totalmente vazias ou NaN
        if pd.isna(nmr_ato) or str(nmr_ato).strip() == "":
            i += 1
            continue

        data = line["Data"]
        if isinstance(data, str):
            data = data.replace("\n", "")
        envolvido = line["Envolvido"]
        texto = str(line["Texto"]) if not pd.isna(line["Texto"]) else ""

        # Se a próxima linha for do mesmo ato (Ato NaN), junta o texto
        if i + 1 < len(df):
            next_line = df.iloc[i + 1]
            if pd.isna(next_line["Ato"]) or str(next_line["Ato"]).strip() == "":
                next_texto = str(next_line["Texto"]) if not pd.isna(next_line["Texto"]) else ""
                texto += " " + next_texto
                i += 1  # pula a próxima linha, já usada

        ato = (
            f"# Ato {len(atos) + 1}\n"
            f"Numero do ato: {nmr_ato}\n"
            f"Data do ato: {data}\n"
            f"Envolvido(s) no ato: {envolvido}\n"
            f"Texto do ato: {texto.strip()}\n\n"
        )
        atos.append(ato)
        i += 1  # passa para o próximo ato principal
    
    # Salva em arquivo
    with open("atos_md.txt", "w", encoding="utf-8") as arquivo:
        arquivo.writelines(atos)
