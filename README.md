Walk-Safe
Creado por: Daniela Castellanos y Vanessa Almagro

Descripción
Walk-Safe es una app en Streamlit pensada para chicas que caminan hacia sus hogares alrededor de la USFQ. Mapa (Folium) para trazar rutas y reportar incidentes. Las rutas cambian de color según horario seguro (verde/rojo) y si hay un incidente activo cercano se marcan en rojo. Incluye “Modo Seguro” con temporizador y contacto seguro.

Nota importante
El punto de entrada de la aplicación es el archivo streamlit_app.py.

Requisitos
- Python 3.12 (recomendado 3.10+)
- pip actualizado
- Windows/macOS/Linux
- (Opcional WhatsApp) Sesión iniciada en web.whatsapp.com

Instalación
1) Extraer el ZIP en una carpeta (ej: C:\Walk-Safe)
2) Abrir una terminal en esa carpeta
3) Crear y activar entorno virtual:
   Windows:
     python -m venv .venv
     .\.venv\Scripts\Activate
   macOS/Linux:
     python3 -m venv .venv
     source .venv/bin/activate
4) Instalar dependencias:
   pip install --upgrade pip
   pip install -r requirements.txt
5) Ejecutar:
   streamlit run streamlit_app.py
   (Si el puerto está ocupado: streamlit run streamlit_app.py --server.port 8502)

Uso
- Mapa/Editor: dibujar rutas (Polyline), reportar incidentes (Marker).
- Ajustar Día/Hora para ver estado de rutas (verde/rojo). Incidentes activos cercanos fuerzan rojo.
- Modo Seguro: configurar recorrido, usar temporizador, seleccionar contacto seguro.

Datos
- routes.json: rutas con id, name, polyline, schedule (HH:MM y days 0..6).
- incidents.csv: encabezado: id,createdAt,lat,lng,type,description,start,end,days

Notas WhatsApp
- Requiere sesión activa en web.whatsapp.com.
