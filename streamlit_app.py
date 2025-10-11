import os, json
import streamlit as st
import folium
from streamlit_folium import st_folium

#Configuracion de la Pagina
st.set_page_config(page_title="Walk-Safe • Mapa base", layout="wide")
st.title("Walk-Safe · Mapa base")

st.sidebar.header("Centro del mapa")
lat = st.sidebar.number_input("Latitud", value=-0.19685, format="%.6f")   
lng = st.sidebar.number_input("Longitud", value=-78.43608, format="%.6f") 
zoom = st.sidebar.slider("Zoom", 10, 19, 16)

#Crear mapa
MAP_CENTER = [lat, lng]
m = folium.Map(location=MAP_CENTER, zoom_start=zoom, control_scale=True)

#Colocar marcador inicial
folium.CircleMarker(
    location=MAP_CENTER,
    radius=8,
    tooltip="Campus / Centro"
).add_to(m)

#Rutas!!
Route_Path = "routes.json"
with open(Route_Path, "r", encoding="utf-8") as f:
    routes = json.load(f)

#dibujar rutas
for r in routes:
    coords = r["polyline"]
    name = r.get("name", "(sin nombre)")

    folium.PolyLine(
        locations=coords,
        color="blue",
        weight=5,
        tooltip=name
    ).add_to(m)

    
#Render
st_folium(m, width=900, height=600)

