import pandas as pd
from pathlib import Path

def leer_csv_info_general_instrumentos():
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    CSV_PATH = BASE_DIR / "data" / "datos_generales_instrumentos.csv"

    df = pd.read_csv(
        CSV_PATH, sep=";", 
        encoding="utf-16",
        keep_default_na=False)
    
    return df.to_dict(orient="records")