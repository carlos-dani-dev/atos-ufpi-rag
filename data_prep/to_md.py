import os
import re
import pandas as pd
import numpy as np


def normalizar(match):
        original = match.group(0)
        normalizado = re.sub(r"[./,-]", "", original)
        return f"{normalizado}"


def normalizar_siape(texto):
    padrao = r"\b\d{7},"
    return re.sub(padrao, normalizar, texto)

    
def normalizar_processos(texto):
    padrao = r"\b\d{5}\.\d{6}/\d{4}-\d{2}\b"
    return re.sub(padrao, normalizar, texto)


if __name__ == "__main__":
    
    atos_path = "./atos_excel/"
    for ato in os.listdir(atos_path):
        df = pd.read_excel(atos_path+ato)
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
                data = data.split("/")
                data = f"{data[1]}-{data[0]}-{data[2]}"
            texto = str(line["Texto"]) if not pd.isna(line["Texto"]) else ""
            
            # Se a próxima linha for do mesmo ato (Ato NaN), junta o texto
            if i + 1 < len(df):
                next_line = df.iloc[i + 1]
                if pd.isna(next_line["Ato"]) or str(next_line["Ato"]).strip() == "":
                    next_texto = str(next_line["Texto"]) if not pd.isna(next_line["Texto"]) else ""
                    texto += " " + next_texto
                    i += 1  # pula a próxima linha, já usada

            if len(texto.split("\n")[0]) == 1: texto = texto[1:]
            texto = (" ").join(texto.split("\n"))
            
            texto = normalizar_processos(texto)
            texto = normalizar_siape(texto)
            
            nmr_ato = nmr_ato.strip() if type(nmr_ato) == "str" else nmr_ato
            
            ato = (
                f"# Ato {int(nmr_ato)}\n"
                f"Numero do ato: {int(nmr_ato)} "
                f"Data do ato: {data} "
                f"Texto do ato: {texto.strip()} "
            )
            atos.append(ato)
            i += 1  # passa para o próximo ato principal
        
        # Salva em arquivo
        with open("atos_md.txt", "w", encoding="utf-8") as arquivo:
            for ato in atos:
                arquivo.write(f"{ato}\n\n")
            #arquivo.writelines(atos)
