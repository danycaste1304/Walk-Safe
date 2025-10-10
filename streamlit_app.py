import streamlit as st
from contacts import contacts_component
from walk import show_walk_ui
# ... otros imports

# ⬇️ ESTO VA AQUÍ (PRIMERO, antes de todo)
st.set_page_config(
    page_title="Walk-Safe",
    page_icon="🚶‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ⬇️ ESTO VA AQUÍ (SEGUNDO, después del set_page_config)
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 10px;
        padding: 10px 24px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# ⬇️ DESPUÉS VA EL RESTO DE TU APP
st.title("🚶‍♀️ Walk-Safe")

# Tu código actual...
pagina = st.sidebar.selectbox("Sección:", ["Contactos", "Recorrido"])

if pagina == "Contactos":
    contacts_component()

if pagina == "Recorrido":
    show_walk_ui()