
import streamlit as st
import pandas as pd
import time
from lib.utils import new_id, utc_now_iso, load_df, save_df
from config import CONTACTS_PATH, CONTACT_FIELDS

def contacts_component():
    st.subheader('Contacto de Emergencia')
    st.caption('Agrega un nuevo contacto que recibirá alertas de emergencia')

#Cargar contactos existentes
    path = CONTACTS_PATH
    contacts_df = load_df(path, CONTACT_FIELDS)

 #Crear formulario para agregar un nuevo contacto
    if "default_contact_id" not in st.session_state:
        st.session_state["default_contact_id"] = None
    if "default_contact_name" not in st.session_state:
        st.session_state["default_contact_name"] = None
    with st.form("Nuevo contacto de emergencia"):
        nombre= st.text_input('Nombre:')
        whatsapp = st.text_input('WhatsApp:')
        email= st.text_input('Email:')
        submitted= st.form_submit_button()

#Diccionario con la informacion del nuevo contacto
    if submitted:
        if not nombre.strip(): 
            st.error('Por favor complete el nombre')
        else:
            new_contact={
                'id': new_id('ct'), #ct = contact
                'name': nombre.strip(),
                'whatsapp': whatsapp.strip(),
                'email': email.strip()
         }
            new_row = pd.DataFrame([new_contact])
    #Concatenar ambos DataFrames
            contacts_df = pd.concat([contacts_df, new_row], ignore_index=True)
    #Guardar cambios
            save_df(contacts_df, path)
            st.success('Contacto agregado exitosamente!')
            time.sleep(1)
            st.rerun()
            
#Mostrar lista de los contactos existentes 
    if contacts_df.empty:
        st.info('No existe ningun contacto agregado')
    else:
        st.write('----') 
        st.subheader('Contactos Agregados')
# Mostrar informacion de cada contacto
        for i, contacto in contacts_df.iterrows():
            st.write(f"• **{contacto['name']}** | WhatsApp: {contacto['whatsapp']} | Email: {contacto['email']}")
 #Elegir contacto por defecto (favorito)
        st.write("---")
        
        lista_nombres = contacts_df['name'].tolist() #Convertir la columna nombres a una lista
        nombre_seleccionado = st.selectbox('Seleccionar contacto por defecto', lista_nombres) 

#Actualizar contacto por defecto en session state
    if st.button('Asignar contacto'):
        contacto_elegido = contacts_df[contacts_df['name'] == nombre_seleccionado].iloc[0]
        st.session_state['default_contact_id'] = contacto_elegido['id']
        st.session_state['default_contact_name'] = contacto_elegido['name']
        st.success('Contacto asignado con exito!')
        time.sleep(1.5)
        st.rerun()