import streamlit as st
from contacts import contacts_component
from walk import show_walk_ui



st.set_page_config(
    page_title="Walk-Safe",
    page_icon="🚶‍♀️",
    layout="wide",
    initial_sidebar_state="expanded"
)


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


st.title("🚶‍♀️ Walk-Safe")


pagina = st.sidebar.selectbox("Sección:", ["Contactos", "Recorrido"])

if pagina == "Contactos":
    contacts_component()

if pagina == "Recorrido":
    show_walk_ui()