import os, json, csv
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import datetime as dt
from time_utils import time_schedule, summarize_schedule, parse_hhmm, time_range, DAYS_LABELS
from contacts import contacts_component  
from walk import show_walk_ui, show_walk_timer


#Configuracion de la Pagina
st.set_page_config(page_title="Walk-Safe • Rutas", layout="wide")
st.title("Walk-Safe · Rutas alrededor de la USFQ")

st.sidebar.header("Centro del mapa")
lat = st.sidebar.number_input("Latitud", value=-0.19685, format="%.6f")   
lng = st.sidebar.number_input("Longitud", value=-78.43608, format="%.6f") 
zoom = st.sidebar.slider("Zoom", 10, 19, 16)

#Anadir en sidebar Horarios
st.sidebar.header("Horarios")
hora_sel: dt.time = st.sidebar.time_input("Hora", value=dt.time(7, 0))
dia_sel = st.sidebar.selectbox("Día", DAYS_LABELS, index=1)  
dia_idx = DAYS_LABELS.index(dia_sel)   

pagina = st.sidebar.selectbox("Sección:", ["Contactos", "Recorrido"])


#Cargar rutas Json
ROUTES_PATH = "routes.json"

#Cargar incidentes
INC_PATH = "incidents.csv"
INC_FIELDS = ["id","createdAt","lat","lng","type","description","start","end","days"]

#Crea un json si no existe
if not os.path.exists(ROUTES_PATH):
    with open(ROUTES_PATH, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)

#Abre y lee el archivo
with open(ROUTES_PATH, "r", encoding="utf-8") as f:
    routes = json.load(f)
if not isinstance(routes, list):
    routes = []

#crear pestanas
tab_mapa, tab_editor = st.tabs(["🗺️ Mapa", "✏️ Editor de rutas"])

    #pestana mapa
    with tab_mapa:
        m1 = folium.Map(location=[lat, lng], zoom_start=zoom, control_scale=True)

        #Dibujar rutas existentes
        all_points = []
        for i, r in enumerate(routes, start=1):
            coords = r.get("polyline", [])
            name = r.get("name", f"Ruta {i}")
            sched = r.get("schedule", [])

            if not coords:
                continue

            # Sin schedule = neutra (azul). Con schedule = verde/gris según hora/día.
            if not sched:
                color, weight = "blue", 5
                tip = f"{name} — Sin horario"
            else:
                in_time = time_schedule(hora_sel, dia_idx, sched)
                color  = "green" if in_time else "red"
                weight = 6 if in_time else 4
                tip = f"{name} — {summarize_schedule(sched)}"

            folium.PolyLine(
                locations=coords,
                color=color,
                weight=weight,
                tooltip=tip
            ).add_to(m1)

            all_points.extend(coords)

        #Punto del campus
        folium.CircleMarker([lat, lng], radius=6, tooltip="Campus / Centro").add_to(m1)

    #Incidentes
    

        #render del mapa  
        st_folium(m1, width="100%", height=640, key="map_view")

    #Pestana Rutas
    with tab_editor:
        mode = st.radio("¿Qué quieres crear?", ["Ruta", "Incidente"], horizontal=True)

        if mode == "Ruta":
            st.subheader("Traza tu ruta con la herramienta Polyline (clic en la calle, doble-clic para terminar)")
            st.caption("Tip: Acerca el zoom, sigue Diego de Robles u otras vías perimetrales. Luego guarda la ruta.")

            # Estado del trazado actual
            if "drawing_points" not in st.session_state:
                st.session_state.drawing_points = []

            colA, colB, colC = st.columns([1,1,2])
            with colA:
                name = st.text_input("Nombre de la ruta", value="Nueva ruta")
            with colB:
                route_id = st.text_input("ID (único)", value=f"r_{len(routes)+1}")
            with colC:
                st.write("")

            # Mapa de edición
            m2 = folium.Map(location=[lat, lng], zoom_start=zoom, control_scale=True)

            # Barra de dibujo: solo Polyline (desactivamos lo demás)
            Draw(
                export=False,
                position="topleft",
                draw_options={
                    "polyline": {
                        "allowIntersection": False,
                        "shapeOptions": {"color": "red", "weight": 4}
                    },
                    "polygon": False,
                    "rectangle": False,
                    "circle": False,
                    "circlemarker": False,
                    "marker": False
                },
                edit_options={
                    "edit": True,
                    "remove": True
                }
            ).add_to(m2)

            if len(st.session_state.drawing_points) >= 2:
                folium.PolyLine(st.session_state.drawing_points, color="red", weight=4, tooltip="trazando…").add_to(m2)

            # Render del editor
            out = st_folium(
                m2,
                width="100%",
                height=640,
                key="map_editor_draw",
                return_on_hover=False
            )

            if out and out.get("last_active_drawing"):
                feature = out["last_active_drawing"]
                geom = feature.get("geometry", {})
                if geom.get("type") == "LineString":
                    coords_lnglat = geom.get("coordinates", [])
                    # Convertir de [lng, lat] (GeoJSON) a [lat, lng] (Folium)
                    st.session_state.drawing_points = [[c[1], c[0]] for c in coords_lnglat]

            elif out and out.get("all_drawings"):
                drawings = out["all_drawings"]
                last = drawings[-1]
                geom = last.get("geometry", {})
                if geom.get("type") == "LineString":
                    coords_lnglat = geom.get("coordinates", [])
                    st.session_state.drawing_points = [[c[1], c[0]] for c in coords_lnglat]

        # Controles
        c1, c2, c3, c4 = st.columns([1,1,1,2])
        with c1:
            if st.button("🗑️ Limpiar trazado"):
                st.session_state.drawing_points = []
        with c2:
            # Botón para volcar cualquier dibujo del mapa a la sesión (por si editaste con la barra)
            if st.button("⤵️ Tomar último dibujo"):
                if out and out.get("all_drawings"):
                    last = out["all_drawings"][-1]
                    geom = last.get("geometry", {})
                    if geom.get("type") == "LineString":
                        coords_lnglat = geom.get("coordinates", [])
                        st.session_state.drawing_points = [[c[1], c[0]] for c in coords_lnglat]
                    else:
                        st.warning("El último dibujo no es una Polyline.")
                else:
                    st.info("No hay dibujos aún. Usa la herramienta Polyline.")
        with c3:
            save_enabled = bool(name.strip()) and bool(route_id.strip()) and len(st.session_state.drawing_points) >= 2
            if st.button("💾 Guardar ruta", disabled=not save_enabled, type="primary"):
                if any(r.get("id") == route_id for r in routes):
                    st.error(f"Ya existe una ruta con id='{route_id}'. Elige otro ID.")
                else:
                    new_route = {
                        "id": route_id.strip(),
                        "name": name.strip(),
                        "polyline": st.session_state.drawing_points
                    }
                    routes.append(new_route)
                    with open(ROUTES_PATH, "w", encoding="utf-8") as f:
                        json.dump(routes, f, ensure_ascii=False, indent=2)
                    st.success(f"Ruta '{name}' guardada en {ROUTES_PATH}.")
                    st.session_state.drawing_points = []
    else:
        st.subheader("Usa la herramienta Marker (pin) y haz clic en el mapa para fijar el incidente")

            # Estado: punto seleccionado
            if "inc_point" not in st.session_state:
                st.session_state.inc_point = None  # [lat, lng] o None

            col1, col2 = st.columns(2)
            with col1:
                itype = st.selectbox("Tipo", ["acoso","zona-oscura","asalto","otro"], index=0)
                start_inc = st.time_input("Inicio (HH:MM)", value=dt.time(19, 0))
            with col2:
                idesc = st.text_area("Descripción breve", placeholder="Ej: acoso cerca de parada")
                end_inc = st.time_input("Fin (HH:MM)", value=dt.time(21, 0))

            # Días (0=Dom ... 6=Sáb)
            day_labels = ["Dom","Lun","Mar","Mié","Jue","Vie","Sáb"]
            days_sel_labels = st.multiselect("Días", options=day_labels, default=["Lun","Mar","Mié","Jue","Vie"])
            days_sel = [day_labels.index(x) for x in days_sel_labels]

            # Mapa con barra Draw (solo Marker)
            m_inc = folium.Map(location=[lat, lng], zoom_start=zoom, control_scale=True)
            Draw(
                export=False,
                position="topleft",
                draw_options={
                    "polyline": False,
                    "polygon": False,
                    "rectangle": False,
                    "circle": False,
                    "circlemarker": False,
                    "marker": True  # <- activamos el pin
                },
                edit_options={"edit": True, "remove": True}
            ).add_to(m_inc)

            # Si ya tenemos un punto en sesión, muéstralo
            if st.session_state.inc_point:
                folium.CircleMarker(
                    st.session_state.inc_point,
                    radius=7, color="red", fill=True, fill_opacity=0.9,
                    tooltip="Incidente seleccionado"
                ).add_to(m_inc)

            # Render y captura del último dibujo activo
            out_inc = st_folium(
                m_inc, width="100%", height=520,
                key="map_editor_inc_draw",
                return_on_hover=False
            )

            # 1) Si hay un dibujo activo (Point), lo tomamos
            if out_inc and out_inc.get("last_active_drawing"):
                feat = out_inc["last_active_drawing"]
                geom = feat.get("geometry", {})
                if geom.get("type") == "Point":
                    # GeoJSON: [lng, lat] -> Folium/nuestro: [lat, lng]
                    lng, lat_ = geom.get("coordinates", [None, None])
                    if lng is not None and lat_ is not None:
                        st.session_state.inc_point = [float(lat_), float(lng)]

            # 2) Si no, tomamos el último de todos los dibujos (por si editaron)
            elif out_inc and out_inc.get("all_drawings"):
                last = out_inc["all_drawings"][-1]
                geom = last.get("geometry", {})
                if geom.get("type") == "Point":
                    lng, lat_ = geom.get("coordinates", [None, None])
                    if lng is not None and lat_ is not None:
                        st.session_state.inc_point = [float(lat_), float(lng)]

            # Controles
            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("🗑️ Quitar marcador"):
                    st.session_state.inc_point = None
            with c2:
                can_save = bool(st.session_state.inc_point) and bool(itype) and bool(days_sel)
                if st.button("💾 Guardar incidente", disabled=not can_save, type="primary"):
                    now = dt.datetime.now().isoformat(timespec="seconds")
                    inc_id = f"inc_{now.replace('-','').replace(':','').replace('T','_')}"
                    file_exists = os.path.exists(INC_PATH)
                    with open(INC_PATH, "a", newline="", encoding="utf-8") as f:
                        w = csv.writer(f)
                        if not file_exists:
                            w.writerow(INC_FIELDS)  # encabezados la 1ª vez
                        w.writerow([
                            inc_id, now,
                            st.session_state.inc_point[0], st.session_state.inc_point[1],
                            itype, idesc,
                            start_inc.strftime("%H:%M"), end_inc.strftime("%H:%M"),
                            ",".join(str(d) for d in days_sel)
                        ])
                    st.success(f"Incidente guardado: {inc_id}")
                    st.session_state.inc_point = None

elif pagina == "Mi Caminata":
    st.header("Tu caminata segura")
        
    tab1, tab2 = st.tabs(["🚶 Configurar Caminata", "⏱️ Temporizador"])
        
    with tab1:
        show_walk_ui()
            
    with tab2:
        show_walk_timer()
