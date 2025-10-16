import math

def _deg_to_m_scale(lat_deg):
    lat_m = 111_320.0
    lon_m = 111_320.0 * math.cos(math.radians(lat_deg))
    return lat_m, lon_m

#Distancia de un punto a un segmento
def _point_to_segment_dist_m(p, a, b):
    lat0 = (a[0] + b[0]) * 0.5
    lat_m, lon_m = _deg_to_m_scale(lat0)

    ax, ay = a[1]*lon_m, a[0]*lat_m
    bx, by = b[1]*lon_m, b[0]*lat_m
    px, py = p[1]*lon_m, p[0]*lat_m

    abx, aby = bx-ax, by-ay
    ab2 = abx*abx + aby*aby
    if ab2 == 0:
        dx, dy = px-ax, py-ay
        return math.hypot(dx, dy)

    t = ((px-ax)*abx + (py-ay)*aby) / ab2
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t*abx, ay + t*aby
    return math.hypot(px-cx, py-cy)

#Dsitancia a una polylinea
def distance_point_to_polyline_m(polyline, p):
    if not polyline or len(polyline) == 1:
        return float("inf")
    dmin = float("inf")
    for i in range(len(polyline)-1):
        d = _point_to_segment_dist_m(p, polyline[i], polyline[i+1])
        if d < dmin:
            dmin = d
    return dmin
