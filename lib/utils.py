import sys, os
sys.path.insert(0, os.getcwd())
import uuid
import pandas as pd
from datetime import datetime, timezone

#Crea un nuevo id (string) de 8 caracteres
def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

#Retorna la hora actual en formato ISO
def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

#Carga un CSV, si no existe devuelve DataFrame vacío
def load_df(path):
    try:
        return pd.read_csv(path)
    except (FileNotFoundError, pd.errors.ParserError, PermissionError):
        return pd.DataFrame() 
    
#Guarda un DataFrame en CSV
def save_df(df, path):
    df.to_csv(path, index=False)






