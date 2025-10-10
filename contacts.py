
import streamlit as st
import pandas as pd
from lib.utils import new_id, utc_now_iso, load_df, save_df

def contacts_component():
    st.subheader('Contacto de Emergencia')

#Cargar contactos existentes
    path= 'contacts.csv'
    contacts_df = load_df(path)
    if contacts_df.empty:
        contacts_df = pd.DataFrame(columns=['id', 'name', 'whatsapp', 'email'])

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



#Mostrar lista de los contactos existentes
    st.write('----') 
    if contacts_df.empty:
        st.info('No existe ningun contacto agregado')
    else:
        st.write('----') 
        st.subheader('Contactos')
# Mostrar informacion de cada contacto
        for i, contacto in contacts_df.iterrows():
            st.write(f"• **{contacto['name']}** | WhatsApp: {contacto['whatsapp']} | Email: {contacto['email']}")
 #Elegir contacto por defecto (favorito)
        st.write("---")
        lista_nombres = contacts_df['name'].tolist() #Convertir la columna nombres a una lista
        nombre_seleccionado = st.selectbox('Seleccionar contacto por defecto', lista_nombres) 

#Actualizar contacto por defecto en session state
        contacto_elegido = contacts_df[contacts_df['name'] == nombre_seleccionado].iloc[0]
        st.session_state['default_contact_id'] = contacto_elegido['id']
        st.session_state['default_contact_name'] = contacto_elegido['name'] 