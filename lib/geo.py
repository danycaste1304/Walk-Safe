

from math import radians, cos, sin, asin, sqrt, atan2

#Calcula la distancia en kilometros entre 2 coordenadas (a y b)

def haversine_km(a_lat, a_lng, b_lat, b_lng):

    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [a_lat, a_lng, b_lat, b_lng])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    r = 6371
    return r * c

#Prueba
print(haversine_km(-0.2192, -78.5094, -0.2500, -78.5200))