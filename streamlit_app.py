import os, json
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw

#Configuracion de la Pagina
st.set_page_config(page_title="Walk-Safe • Rutas", layout="wide")
st.title("Walk-Safe · Rutas alrededor de la USFQ")

st.sidebar.header("Centro del mapa")
lat = st.sidebar.number_input("Latitud", value=-0.19685, format="%.6f")   
lng = st.sidebar.number_input("Longitud", value=-78.43608, format="%.6f") 
zoom = st.sidebar.slider("Zoom", 10, 19, 16)

#Cargar rutas Json
ROUTES_PATH = "routes.json"

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
        if not coords:
            continue
        folium.PolyLine(locations=coords, color="blue", weight=5, tooltip=name).add_to(m1)
        all_points.extend(coords)

    #Punto del campus
    folium.CircleMarker([lat, lng], radius=6, tooltip="Campus / Centro").add_to(m1)

    #render del mapa  
    st_folium(m1, width="100%", height=640, key="map_view")

#Pestana Rutas
with tab_editor:
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

    # Si ya hay puntos (p. ej., por haberlos extraído de un dibujo previo), muéstralos
    if len(st.session_state.drawing_points) >= 2:
        folium.PolyLine(st.session_state.drawing_points, color="red", weight=4, tooltip="trazando…").add_to(m2)

    # Render del editor (el Draw vive dentro del mapa)
    out = st_folium(
        m2,
        width="100%",
        height=640,
        key="map_editor_draw",
        return_on_hover=False
    )

    # 1) Si se acaba de dibujar/editar algo, capturamos la ÚLTIMA geometría activa
    #    (GeoJSON con 'geometry': { 'type': 'LineString', 'coordinates': [[lng,lat], ...] })
    if out and out.get("last_active_drawing"):
        feature = out["last_active_drawing"]
        geom = feature.get("geometry", {})
        if geom.get("type") == "LineString":
            coords_lnglat = geom.get("coordinates", [])
            # Convertir de [lng, lat] (GeoJSON) a [lat, lng] (Folium)
            st.session_state.drawing_points = [[c[1], c[0]] for c in coords_lnglat]

    # 2) Alternativamente, si hay múltiples dibujos, toma el último de all_drawings
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