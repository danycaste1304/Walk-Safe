"""Configuración central: rutas de archivos y constantes de la app.

Las rutas se arman a partir de la ubicación de este archivo, así la app
funciona sin importar desde qué carpeta se ejecute `streamlit run`.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Archivos de datos
ROUTES_PATH = BASE_DIR / "routes.json"
INCIDENTS_PATH = BASE_DIR / "incidents.csv"
CONTACTS_PATH = BASE_DIR / "contacts.csv"
WALKS_PATH = BASE_DIR / "walks.csv"

# Columnas esperadas de cada CSV (se usan si el archivo no existe o está vacío)
INCIDENT_FIELDS = ["id", "createdAt", "lat", "lng", "type", "description", "start", "end", "days"]
CONTACT_FIELDS = ["id", "name", "whatsapp", "email"]
WALK_FIELDS = ["id", "userInitials", "o_lat", "o_lng", "d_lat", "d_lng",
               "etaMin", "graceMin", "startedAt", "status", "contactId"]

# Código de país para los números de WhatsApp (Ecuador)
COUNTRY_CODE = "593"
