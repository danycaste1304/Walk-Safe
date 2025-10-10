from datetime import datetime, timezone, timedelta
from lib.utils import utc_now_iso

#Calcula el tiempo transcurrido (la velocidad ahora está en default)
def eta_minutes_from_km (distance_km, walking_kmh=4.3):
    time= distance_km/walking_kmh
    return round(time*60)

#Calcula los segundos transcurridos 
def countdown_seconds(deadline_iso, current_time_iso=None):

    #Transformar el tiempo de formato ISO a datetime
    deadline =datetime.fromisoformat(deadline_iso)
    if current_time_iso is None:
        now=datetime.fromisoformat(utc_now_iso())
    else:
        now = datetime.fromisoformat(current_time_iso)
    
    difference = deadline-now
    return int(difference.total_seconds())


##PRUEBAS
if __name__ == "__main__":
    # Prueba eta_minutes_from_km
    print("\nPruebas de eta_minutes_from_km:")
    distancias = [1.0, 2.5, 4.3]
    for d in distancias:
        mins = eta_minutes_from_km(d)
        print(f"Distancia: {d}km -> {mins:.1f} minutos")

    # Prueba countdown_seconds
    print("\nPruebas de countdown_seconds:")
    # Caso 1: tiempo futuro (30 segundos desde ahora)
    future = (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat()
    print(f"Segundos hasta {future}: {countdown_seconds(future)}")
    
    # Caso 2: tiempo pasado (debería retornar 0)
    past = "2023-01-01T00:00:00+00:00"
    print(f"Segundos hasta {past}: {countdown_seconds(past)}")

    # Prueba con 5 minutos
    future = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat()
    print(f"Segundos hasta {future}: {countdown_seconds(future)}")  # Debería ser ~300 segundos


