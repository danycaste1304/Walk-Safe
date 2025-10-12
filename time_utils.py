import datetime as dt

DAYS_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"]

def parse_hhmm(s):
    s = s.strip()
    h, m = map(int, s.split(":"))
    return dt.time(h, m)

def time_range(t, start, end):
    """True si t está en [start, end]; soporta rangos que cruzan 00:00."""
    if start <= end:
        return start <= t <= end
    #Medianoche
    return t >= start or t <= end

def time_schedule(t, day_idx, schedule):
    """True si la hora t y el día day_idx caen en algún bloque del schedule."""
    if not schedule:
        return False
    for i in schedule:
        days = i.get("days", [])
        if day_idx not in days:
            continue
        start = parse_hhmm(i["start"])
        end = parse_hhmm(i["end"])
        if time_range(t, start, end):
            return True
    return False

def summarize_schedule(schedule):
    #Devuelve un texto compacto para tooltip.
    if not schedule:
        return "Sin horario"
    parts = []
    for i in schedule:
        start = i["start"]
        end = i["end"]
        days = i.get("days", [])
        if not days:
            day_txt = "Todos los días"
        else:
            ordered = sorted(days)
            # Si son consecutivos (p. ej., [1,2,3,4,5]) mostramos como rango
            if len(ordered) >= 3 and ordered == list(range(ordered[0], ordered[-1] + 1)):
                day_txt = f"{DAYS_LABELS[ordered[0]]}–{DAYS_LABELS[ordered[-1]]}"
            else:
                day_txt = ",".join(DAYS_LABELS[d] for d in ordered)
        parts.append(f"{start}–{end} ({day_txt})")
    return "; ".join(parts)
