import streamlit as st
import sys
import os
sys.path.insert(0, os.getcwd())

from lib.utils import load_df, save_df, new_id, utc_now_iso
from lib.geo import haversine_km
from lib.lib import eta_minutes_from_km
import pandas as pd

def show_walk_ui():
    
    st.subheader("Origen")
    col1, col2 = st.columns(2)
    with col1:
        a_lat = st.number_input("Latitud A")
    with col2:
        a_lng = st.number_input("Longitud A")
    
    st.subheader("Destino")
    col3, col4 = st.columns(2)
    with col3:
        b_lat = st.number_input("Latitud B")
    with col4:
        b_lng = st.number_input("Longitud B")
   
    distance= haversine_km(a_lat, a_lng, b_lat, b_lng)
    st.metric("Distancia", f"{distance:.2f} km")

    time= eta_minutes_from_km(distance)
    st.metric("Tiempo transcurrido", f"{time:.2f} minutos")

    
    gracia= st.number_input('Minutos de gracia',min_value=5, value=15)
    
    df= load_df(r'contacts.csv')    