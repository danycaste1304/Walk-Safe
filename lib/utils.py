import uuid
import pandas as pd
from datetime import datetime, timezone

#Crea un nuevo id (string) de 8 caracteres
def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

#Retorna la hora actual en formato ISO
def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

#Carga un CSV. Si no existe o está vacío, devuelve un DataFrame vacío
#con las columnas indicadas (para que el código que busca columnas no falle)
def load_df(path, columns=None):
    try:
        df = pd.read_csv(path)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError, PermissionError):
        df = pd.DataFrame()
    if columns:
        for col in columns:
            if col not in df.columns:
                df[col] = pd.Series(dtype=object)
    return df
    
#Guarda un DataFrame en CSV
def save_df(df, path):
    df.to_csv(path, index=False)






