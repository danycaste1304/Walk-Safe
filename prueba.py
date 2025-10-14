import streamlit as st
import sys
import os
sys.path.insert(0, os.getcwd())

# Importar componentes
from contacts import  contacts_component
from walk import show_walk_ui, show_walk_timer

# Configuración de la página
st.set_page_config(
    page_title="Walk-Safe",
    page_icon="🚶",
    layout="wide"
)

# Título principal
st.title("🚶 Walk-Safe")
st.caption("Tu asistente de seguridad para caminatas seguras")

# Sidebar con navegación
st.sidebar.header("Navegación")
pagina = st.sidebar.selectbox(
    "Selecciona una sección:",
    ["Inicio", "Contactos", "Mi caminata"]
)

# Inicializar session_state si no existe
if 'default_contact_id' not in st.session_state:
    st.session_state['default_contact_id'] = None
if 'default_contact_name' not in st.session_state:
    st.session_state['default_contact_name'] = None
if 'active_walk_id' not in st.session_state:
    st.session_state['active_walk_id'] = None
if 'active_contact_phone' not in st.session_state:
    st.session_state['active_contact_phone'] = None

# Mostrar contenido según la página seleccionada
if pagina == "Inicio":
    st.markdown("""
    ### Bienvenido a Walk-Safe
    
    Walk-Safe es una aplicación diseñada para mejorar tu seguridad personal durante tus caminatas.
    
    **Características principales:**
    - 📞 Gestiona contactos de emergencia
    - 🚶 Inicia caminatas seguras
    - ⏱️ Temporizador de seguridad
    - 🚨 Alertas automáticas a contactos de confianza
    
    **¿Cómo usar?**
    1. Ve a "Contactos" y agrega a alguien de confianza
    2. Ve a "Mi caminata" e ingresa tu origen y destino
    3. Presiona "Iniciar mi camino"
    4. El temporizador te alertará si no llegas a tiempo
    
    ¡Tu seguridad es nuestra prioridad! 💝
    """)

elif pagina == "Contactos":
    st.header("Gestión de Contactos")
    contacts_component()



elif pagina == "Mi caminata":
    st.header("Tu caminata segura")
    
    tab1, tab2 = st.tabs(["🚶 Configurar Caminata", "⏱️ Temporizador"])
    
    with tab1:
        # ✅ Todo lo de la caminata en UNA pestaña
        show_walk_ui()
        
    with tab2:
        # ✅ Solo el temporizador en la OTRA pestaña  
        show_walk_timer()