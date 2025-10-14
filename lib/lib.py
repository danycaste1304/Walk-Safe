import sys, os
sys.path.insert(0, os.getcwd())
from datetime import datetime, timezone, timedelta
from lib.utils import utc_now_iso


#Calcula el tiempo transcurrido (la velocidad ahora está en default)
def eta_minutes_from_km (distance_km, walking_kmh=40):
    time= distance_km/walking_kmh
    return round(time*60)

#Calcula los segundos transcurridos 
def countdown_seconds(started_iso, total_minutes):

    # Convertir el tiempo de inicio ISO a datetime
    started = datetime.fromisoformat(started_iso)
    
    # Calcular el deadline sumando los minutos
    deadline = started + timedelta(minutes=total_minutes)
    
    # Obtener la hora actual (UTC)
    now = datetime.now(timezone.utc)
    
    # Calcular la diferencia en segundos
    difference = (deadline - now).total_seconds()
    return int(difference)


