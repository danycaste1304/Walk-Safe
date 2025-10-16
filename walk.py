
import streamlit as st
import pandas as pd
from urllib.parse import quote
from streamlit_autorefresh import st_autorefresh
import time
import sys
import os
import json
import pyautogui
import pywhatkit as kit
sys.path.insert(0, os.getcwd())

from lib.utils import load_df, save_df, new_id, utc_now_iso
from lib.geo import haversine_km
from lib.lib import eta_minutes_from_km, countdown_seconds


#Funciones auxiliares

#Mensaje que se envia al contacto de emergencia asignado
def mensaje_salida(route, eta_min, gracia_min):
    return f"""
    Hey! Estoy usando Walk-Safe 
    En camino por la ruta: {route}
    Llego en {eta_min} min (+{gracia_min} extra).
    Si me tardo, la app te avisa 
    """
        
#Creacion de link de whatsapp
def whatsapp_link(phone,message,country_code='593'):
    phone = str(phone)
    clean_phone = ''.join(filter(str.isdigit, phone))
    # Si el número empieza con 0, quitarlo
    if clean_phone.startswith('0'):
        clean_phone = clean_phone[1:]
    # Agregar código de país si no está presente
    if not clean_phone.startswith(country_code):
        clean_phone = f"{country_code}{clean_phone}"
    wpp=quote(message)
    return f"https://wa.me/{clean_phone}?text={wpp}"


def has_default_contact():
    required_keys = ['default_contact_id', 'default_contact_name']
    return all(key in st.session_state and st.session_state[key] for key in required_keys)

def cargar_routes():
    try:
        with open('routes.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []


#Funcion principal 
def show_walk_ui():
    """
    Interfaz de usuario para iniciar una caminata segura.
    Permite al usuario:
    - Seleccionar origen (A) y destino (B)
    - Ver la distancia y tiempo (aproximado) de recorrido calculado
    - Ajustar minutos de gracia
    - Seleccionar contacto de emergencia
    - Iniciar la caminata y guardarla en walks.csv
    """

    # Contenedores para mensajes dinámicos
    whatsapp_container = st.empty()
    status_container = st.empty()

    routes = cargar_routes()

    if not routes:
        st.warning("No hay rutas disponibles")
        st.stop()

    # Selector de ruta
    nombres_rutas = [r['name'] for r in routes]
    ruta_seleccionada = st.selectbox("Selecciona una ruta", nombres_rutas)

    # Buscar ruta
    ruta = next((r for r in routes if r['name'] == ruta_seleccionada), None)

    if ruta:
        a_lat, a_lng = ruta['polyline'][0]
        b_lat, b_lng = ruta['polyline'][-1]
        
   
    #2) Calcular métricas que se muestran en la pantalla

    #Calcular la distancia entre el origen y el destino (se asume una velocidad por default de 5 km/h)
    distance= haversine_km(a_lat, a_lng, b_lat, b_lng)
    st.metric("📍 Distancia total", f"{distance:.2f} km")

    #Calcular el tiempo estimado del recorrido
    time= eta_minutes_from_km(distance)
    st.metric("⏱️ Tiempo estimado", f"{time:.0f} minutos")

    #Tiempo extra permitido antes de activar la alerta (por defecto 5 min, mínimo 3 min)
    st.markdown("### ⚡ Tiempo extra de seguridad")
    st.caption("Si no confirmas tu llegada después del tiempo estimado + tiempo extra, enviaremos una alerta a tu contacto")
    gracia= st.number_input('Minutos de gracia',min_value=3, value=5)
    
   # Mostrar qué contacto de emergencia será notificado
    if has_default_contact():
         st.success(f"✨ {st.session_state['default_contact_name']} está lista para cuidarte en este viaje")
    else:
        st.warning("👋 Primero selecciona a alguien de confianza como tu contacto de seguridad")

    #Validaciones (todos los campos esten completos)
    if (a_lat != 0 or a_lng != 0 or b_lat != 0 or b_lng != 0) and distance > 0:

        st.divider()

        col1, col2 = st.columns(2)
   
        with col1:
            walk_id = st.session_state.get('active_walk_id')
            
    #3) Botón de iniciar mi camino

            if walk_id:
            # Ya hay caminata activa, deshabilitar botón
                st.button("🚶‍♀️ Iniciar mi camino", disabled=True)
                st.caption("Ya tienes una caminata en progreso. Marca 'Llegué a salvo' para terminarla.")
            else:
            #Boton para iniciar recorrido
                if st.button("🚶‍♀️ Iniciar mi camino"):   

                    #diccionario con todos los datos de la caminata
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
                    walks_df = load_df(r'walks.csv')
                    # Convertir diccionario a DataFrame y guardar
                    walk_df = pd.DataFrame([walk])
                    walks_df = pd.concat([walks_df, walk_df], ignore_index=True)
                    save_df(walks_df, r'walks.csv')

                    

                    # Validar que el contacto existe
                    contacts = load_df(r'contacts.csv') #cargar base de datos 
                    contact_match = contacts[contacts['id'] == walk['contactId']]
                    if contact_match.empty:
                        status_container.error("❌ Contacto no encontrado en la base de datos")
                        st.session_state['active_walk_id'] = None  # Revertir
                        return

                    contact = contact_match.iloc[0]
                    
                    # Guardar el ID de la caminata y el wpp
                    st.session_state['active_walk_id'] = walk['id']
                    st.session_state['active_contact_phone'] = contact['whatsapp']

                    # Mostrar resumen de la caminata
                    resumen = (f"""
                    ### 🌟 Resumen de tu viaje
                
                    - 🚶‍♀️ **Distancia**: {distance:.2f} km
                    - ⏱️ **Tiempo estimado**: {time:.0f} minutos
                    - ⚡ **Tiempo extra**: {gracia} minutos
                    - 👤 **Contacto**: {st.session_state['default_contact_name']}
                    
                    > 💝 ¡Tu seguridad es nuestra prioridad! 
                    """)
                    st.session_state['walk_summary'] = resumen

                    # Limpiar mensajes de llegada anterior
                    st.session_state['arrival_message'] = None
                    st.session_state['arrival_status'] = None
                    
                    # Preparar y enviar mensaje de WhatsApp
                    contact_id = walk['contactId'] #obtener el id del contacto determinado
                    if contact_id:
                        phone = contact['whatsapp']
                        
                        mensaje = mensaje_salida(ruta_seleccionada, int(time), int(gracia))
                        try:
                            link = whatsapp_link(phone, mensaje)
                            whatsapp_container.markdown(f"[📱 Enviar mensaje de salida]({link})")
                            status_container.success('✨ ¡Recorrido iniciado!')
                            # Guardar en session_state para que persista
                            st.session_state['walk_message'] = f"[📱 Enviar mensaje de salida]({link})"
                            st.session_state['walk_status'] = 'ACTIVE'
                        except ValueError as e:
                            status_container.error(f"Error: {str(e)}")

        #4) Botón llegué a salvo
        with col2:
            walk_id = st.session_state.get('active_walk_id')
            phone = st.session_state.get('active_contact_phone')  

            if not walk_id:
                st.button("🏠 ¡Llegué a salvo!", disabled=True)
                st.info("Primero inicia una caminata.")
            else:
                if st.button("🏠 ¡Llegué a salvo!"):  
                    walks=load_df(r'walks.csv')
                  
                    if walk_id and phone is not None:
                        if walk_id in walks['id'].values:
                            walks.loc[walks['id'] == walk_id, 'status'] = 'ARRIVED' # Cambiar status en el DataFrame
                            save_df(walks, r'walks.csv') #Guardar el csv actualizado
                        else:
                            status_container.warning("⚠️ Caminata no encontrada en la base de datos")
                            


                        # Limpiar para permitir nueva caminata
                        st.session_state['active_walk_id'] = None
                        st.session_state['active_contact_phone'] = None
                        st.session_state['walk_message'] = None  
                        st.session_state['walk_status'] = None 
                        st.session_state['walk_summary'] = None
                    
                        
                        # Mensaje de WhatsApp de llegada
                        mensaje_llegada = '''Hola! Ya llegué a destino con Walk-Safe. Gracias por estar pendiente!'''
                        try:
                            link_llegada = whatsapp_link(phone, mensaje_llegada)
                            
                            st.success("✅ ¡Enlace de WhatsApp listo! Haz clic para notificar tu llegada")
                            # Guardar en session_state para que el mensaje persista
                            st.session_state['arrival_message'] = f"[📱 Enviar mensaje de llegada]({link_llegada})"
                            st.session_state['arrival_status'] = "🎉 ¡Has llegado a tu destino!"
                        except ValueError as e:
                            status_container.error(f"Error: {str(e)}")

        
    #Validaciones                               
    else:
            if a_lat == 0 and a_lng == 0 and b_lat == 0 and b_lng == 0:
                st.info("Ingresa las coordenadas para comenzar")
            elif distance == 0:
                st.warning("Origen y Destino deben ser diferentes")
    #Mostrar resumen del recorrido
    if st.session_state.get('active_walk_id') and 'walk_summary' in st.session_state:
            with st.expander("🌟 Detalles del recorrido", expanded=True):
                st.markdown(st.session_state['walk_summary'])
                if 'walk_message' in st.session_state:
                    st.markdown(st.session_state['walk_message'])

    #Mostrar mensaje de llegada
    if 'arrival_status' in st.session_state and st.session_state['arrival_status']:
        st.success(st.session_state['arrival_status'])
    if 'arrival_message' in st.session_state and st.session_state['arrival_message']:
        st.markdown(st.session_state['arrival_message'])
        

###Función para el temporizador

def show_walk_timer():
    if 'active_walk_id' not in st.session_state or st.session_state['active_walk_id'] is None:
        mins = 0
        secs = 0
        st.metric("Tiempo restante", "0:00")
        st.progress(0) 
        return
    #Cargar el csv actualizado 
    walks=load_df(r'walks.csv')
    walk_id = st.session_state.get('active_walk_id')
    walk= walks[walks['id'] == walk_id]


    # Si no existe la caminata, limpiar los datos
    if walk.empty:
        st.session_state['active_walk_id'] = None
        st.session_state['active_contact_phone'] = None
        st.rerun()
        return
    
    walk_data = walk.iloc[0]
    started = walk_data['startedAt']
    eta_min = int(walk_data['etaMin'])
    grace_min = int(walk_data['graceMin'])
    status = walk_data['status']

    #Si la caminata está activa    
    if status =='ACTIVE':
        st.subheader("Contador de seguridad")   
        st_autorefresh(interval=1000, key="timer_refresh")
        seconds= countdown_seconds(started,eta_min + grace_min)
        total_seconds = (eta_min + grace_min) * 60

        #Si el contador llega a 0
        if seconds<=0:
            walks.loc[walks['id'] == walk_id, 'status'] = 'ALERT_READY'
            save_df(walks, r'walks.csv')
            st.warning("⚠️ Tiempo agotado. Se activará la alerta.") 
            st.rerun()         
            return
    
        # 5) Mostrar contador
        mins = seconds // 60
        secs = seconds % 60
        st.metric("Tiempo restante", f"{mins}:{secs:02d}")
        st.progress(1 - seconds / total_seconds)
    
    elif status == 'ALERT_READY':
    # Prevenir bucle
        if st.session_state.get('alert_sent'):
            st.info("🔔 La alerta ya fue procesada")
            return 
        
        
        st.error('🚨 ¡ALERTA! Tiempo agotado - No se confirmó llegada')
        phone = st.session_state.get('active_contact_phone')
        mensaje = '''Alerta Walk-Safe
        No llegue a mi destino.
        El tiempo de ruta se agotó.
        Por favor, llámame.'''

        #6) Enviar mensaje automaticamente por WhatsApp si se acaba el tiempo. 
        # (Se debe tener previamente iniciada una sesión en WhatsApp Web)
        try:
            
            # Formateo simple
            phone_clean = str(phone).strip().replace(' ', '').replace('-', '').replace('+', '')
            if phone_clean.startswith('0'):
                phone_clean = '593' + phone_clean[1:]
            elif not phone_clean.startswith('593'):
                phone_clean = '593' + phone_clean
                
            international_phone = '+' + phone_clean
            st.info(f"📞 Número de contacto:  {international_phone}")
            
            #Abrir WhatsApp
            kit.sendwhatmsg_instantly(international_phone, mensaje, wait_time=10, tab_close=False)

            # Esperar y presionar ENTER para asegurar el envío
            #time.sleep(10)
            #pyautogui.press('enter')
            st.success("✅ Mensaje enviado exitosamente")
            st.session_state.alert_sent = True
            
        except Exception as e:
            st.error(f"❌ Error: {e}")
            
            st.session_state.alert_sent = True
          
     # Eliminar el archivo después de enviar
    if os.path.exists("PyWhatKit_DB.txt"):
            os.remove("PyWhatKit_DB.txt")

    
