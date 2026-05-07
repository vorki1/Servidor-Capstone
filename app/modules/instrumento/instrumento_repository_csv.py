import pandas as pd
from pathlib import Path
import numpy as np

def leer_excel_instrumentos_mapeados():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    EXCEL_PATH = BASE_DIR / "data" / "TagsCNN_2026-04-30.xlsx"
    excel_instrumentos_mapeados = pd.read_excel(EXCEL_PATH)
    excel_instrumentos_mapeados.to_csv(EXCEL_PATH.with_suffix('.csv'), index=None, header=True)
    df_instrumentos_mapeados = pd.read_csv(EXCEL_PATH.with_suffix('.csv')).convert_dtypes()
    #Se retorna el dataframe leido
    return df_instrumentos_mapeados

def leer_csv_info_general_instrumentos():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    CSV_PATH = BASE_DIR / "data" / "datos_generales_instrumentos.csv"

    df_matriz_a = pd.read_csv(
        CSV_PATH, sep=";", 
        encoding="utf-16",
        keep_default_na=False)
    
    
    return df_matriz_a

def matriz_a():
    print("Leyendo matriz de excel de instrumentos mapeados...")
    df_mapeo_instrumentos = leer_excel_instrumentos_mapeados() #Aca es un dataframe
    cols_str = df_mapeo_instrumentos.select_dtypes(include=["object", "string"]).columns
    df_mapeo_instrumentos[cols_str] = df_mapeo_instrumentos[cols_str].fillna("Vacio").apply(lambda col: col.str.strip())
    cols_num = df_mapeo_instrumentos.select_dtypes(include=[np.number]).columns
    df_mapeo_instrumentos[cols_num] = df_mapeo_instrumentos[cols_num].fillna(0)
    df_mapeo_instrumentos = df_mapeo_instrumentos.rename(columns={"ID": "Identificador"})
    df_mapeo_instrumentos = df_mapeo_instrumentos[df_mapeo_instrumentos["Identificador"] > 0] #Se eliminan los instrumentos con identificador 0
    
    #Mandamos objeto python de los datos del excel filtrados por los identificadores en 0 y columnas sin datos con "Vacio" o "0"
    return df_mapeo_instrumentos.to_dict(orient="records")