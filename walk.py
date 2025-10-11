import streamlit as st
import pandas as pd
from urllib.parse import quote
import sys
import os
sys.path.insert(0, os.getcwd())

from lib.utils import load_df, save_df, new_id, utc_now_iso
from lib.geo import haversine_km
from lib.lib import eta_minutes_from_km


#Funciones auxiliares

#Mensaje que se envia al contacto de emergencia asignado
def mensaje_salida(o_lat, o_lng, d_lat, d_lng, eta_min, gracia_min, user_initials):
    return f"""¡Hola! Estoy usando Walk-Safe para mi seguridad.
    Voy desde ({o_lat:.4f}, {o_lng:.4f}) 
    Hasta ({d_lat:.4f}, {d_lng:.4f})
    Llegaré en {eta_min} minutos 
    Tiempo extra: {gracia_min} min
    --- {user_initials}"""
        
#Creacion de link de whatsapp
def whatsapp_link(phone,message,country_code='593'):
    clean_phone = ''.join(filter(str.isdigit, phone))
    # Si el número empieza con 0, quitarlo
    if clean_phone.startswith('0'):
        clean_phone = clean_phone[1:]
    # Agregar código de país si no está presente
    if not clean_phone.startswith(country_code):
        clean_phone = f"{country_code}{clean_phone}"
    wpp=quote(message)
    return f"https://wa.me/{clean_phone}?text={wpp}"

#Funcion principal 
def show_walk_ui():
    """
    Interfaz de usuario para iniciar una caminata segura.
    Permite al usuario:
    - Seleccionar origen (A) y destino (B)
    - Ver la distancia y ETA calculada
    - Ajustar minutos de gracia
    - Seleccionar contacto de emergencia
    - Iniciar la caminata y guardarla en walks.csv
    """
    # Contenedores para mensajes dinámicos
    message_container = st.empty()
    whatsapp_container = st.empty()
    status_container = st.empty()
    

    #Convierte tanto comas como puntos a formato float válido
    def normalize_number(value):
        if value is None:
            return None
        # Convertir a string, reemplazar coma por punto
        value_str = str(value).replace(',', '.')
        try:
            return float(value_str)
        except ValueError:
            return None   
        
    #Seleccionar origen
    st.subheader("Origen")
    col1, col2 = st.columns(2)
    with col1:
        a_lat = st.number_input("Latitud A", format="%.4f")
    with col2:
        a_lng = st.number_input("Longitud A", format="%.4f")
    
    #Seleccionar destino
    st.subheader("Destino")
    col3, col4 = st.columns(2)
    with col3:
        b_lat = st.number_input("Latitud B", format="%.4f")
    with col4:
        b_lng = st.number_input("Longitud B", format="%.4f")

    # Normalizar los valores ingresados
    a_lat = normalize_number(a_lat)
    a_lng = normalize_number(a_lng)
    b_lat = normalize_number(b_lat)
    b_lng = normalize_number(b_lng)
   
   #Calcular la distancia entre el origen y el destino (se asume una velocidad por default de 4.3 km/h)
    distance= haversine_km(a_lat, a_lng, b_lat, b_lng)
    st.metric("📍 Distancia total", f"{distance:.2f} km")

    #Calcular el tiempo estimado del recorrido
    time= eta_minutes_from_km(distance)
    st.metric("⏱️ Tiempo estimado", f"{time:.0f} minutos")

    #Tiempo extra permitido antes de activar la alerta (por defecto 15 min, mínimo 5 min)
    st.markdown("### ⚡ Tiempo extra de seguridad")
    st.caption("Si no confirmas tu llegada después del tiempo estimado + tiempo extra, enviaremos una alerta a tu contacto")
    gracia= st.number_input('Minutos de gracia',min_value=5, value=15)
    
   # Mostrar qué contacto de emergencia será notificado
    if 'default_contact_id' in st.session_state and st.session_state['default_contact_id']:
         st.success(f"✨ {st.session_state['default_contact_name']} está lista para cuidarte en este viaje")
    else:
        st.warning("👋 Primero selecciona a alguien de confianza como tu contacto de seguridad")

    #Validaciones (todos los campos esten completos)
    if a_lat is None or a_lng is None or b_lat is None or b_lng is None:
        st.warning(" Completa Origen y Destino")
    elif distance == 0:
        st.warning(" Origen y Destino deben ser diferentes")

    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        #Boton para iniciar recorrido
        if st.button("🚶‍♀️ Iniciar mi camino"):   
            walk = {
                'id': new_id('wk'),
                'userInitials': 'DC',
                'o_lat': a_lat,
                'o_lng': a_lng,
                'd_lat': b_lat,
                'd_lng': b_lng,
                'etaMin': int(time),
                'graceMin': int(gracia),
                'startedAt': utc_now_iso(),
                'status': 'ACTIVE',
                'contactId': st.session_state['default_contact_id']
            }

            # Convertir diccionario a DataFrame y guardar
            walk_df = pd.DataFrame([walk])
            save_df(walk_df, r'walks.csv')

            # Guardar el ID de la caminata
            st.session_state['active_walk_id'] = walk['id']

            # Mostrar resumen de la caminata
            message_container.markdown(f"""
            ### 🌟 Resumen de tu viaje
            
            #### Detalles del recorrido:
            - 🚶‍♀️ **Distancia**: {distance:.2f} km
            - ⏱️ **Tiempo estimado**: {time:.0f} minutos
            - ⚡ **Tiempo extra**: {gracia} minutos
            - 👤 **Contacto**: {st.session_state['default_contact_name']}
            
            > 💝 ¡Tu seguridad es nuestra prioridad! 
            """)

            # Preparar y enviar mensaje de WhatsApp
            contacts = load_df(r'contacts.csv')
            contact_id = st.session_state.get('default_contact_id')
            if contact_id:
                contact = contacts[contacts['id'] == contact_id].iloc[0]
                phone = contact['whatsapp']
                mensaje = mensaje_salida(a_lat, a_lng, b_lat, b_lng, time, gracia, 'DC')
                try:
                    link = whatsapp_link(phone, mensaje)
                    whatsapp_container.markdown(f"[📱 Enviar mensaje de salida]({link})")
                    status_container.success('✨ ¡Recorrido iniciado!')
                except ValueError as e:
                    status_container.error(f"Error: {str(e)}")

       
    with col2:

        if st.button("🏠 ¡Llegué a salvo!"):  
            walks=load_df(r'walks.csv')
            walk_id = st.session_state.get('active_walk_id')
            
            if walk_id:
                # Obtener el contacto nuevamente
                contacts = load_df(r'contacts.csv')
                contact_id = st.session_state.get('default_contact_id')
                if contact_id:
                    contact = contacts[contacts['id'] == contact_id].iloc[0]
                    phone = contact['whatsapp']  
                    
                walks.loc[walks['id'] == walk_id, 'status'] = 'ARRIVED' # Cambiar status en el DataFrame
                save_df(walks, r'walks.csv') #Guardar el csv actualizado

                # Limpiar mensajes anteriores
                message_container.empty()
                whatsapp_container.empty()
                
                # Mostrar mensaje de llegada
                status_container.success("🎉 ¡Has llegado a tu destino!")
                st.balloons()

                # Mensaje de WhatsApp de llegada
                mensaje_llegada = "¡Hola! Ya llegué a mi destino sana y salva 🌟"
                try:
                    link_llegada = whatsapp_link(phone, mensaje_llegada)
                    whatsapp_container.markdown(f"[📱 Enviar mensaje de llegada]({link_llegada})")
                except ValueError as e:
                    status_container.error(f"Error: {str(e)}")


#