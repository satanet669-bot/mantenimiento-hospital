import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuración de página (SIEMPRE PRIMERO)
st.set_page_config(page_title="HOSPITAL - Gestión", page_icon="🏥")

# 2. Conexión estable
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. Función para leer datos sin errores
def cargar_datos():
    return conn.read(ttl="0")

df = cargar_datos()

# --- INTERFAZ ---
st.title("🏥 Control de Mantenimiento")

# Menú lateral con clave única para evitar el error de 'removeChild'
menu = ["📝 Reportar Avería", "🔧 Panel de Ingeniería", "📊 Gestión"]
choice = st.sidebar.selectbox("Menú Principal", menu, key="menu_principal")

if choice == "📝 Reportar Avería":
    st.header("Nuevo Reporte")
    # Quitamos 'clear_on_submit' para dar estabilidad
    with st.form("form_reporte"):
        sector = st.selectbox("📍 Sector", ["Guardia Central", "Internado", "UTI1", "UTI2", "Consultorios", "Quirófano"], key="sel_sector")
        equipo = st.text_input("🏥 Equipo", key="input_equipo")
        problema = st.text_area("🛠️ Problema", key="input_problema")
        prioridad = st.select_slider("⚠️ Prioridad", options=["Baja", "Media", "Alta", "CRÍTICA"], key="slider_prioridad")
        
        submit = st.form_submit_button("Enviar Reporte")
        
        if submit:
            if equipo and problema:
                nuevo_id = int(df['ID'].max() + 1) if not df.empty else 1
                nueva_fila = pd.DataFrame([{
                    'ID': nuevo_id,
                    'Fecha': datetime.now().strftime("%d/%m %H:%M"),
                    'Sector': sector, 
                    'Equipo': equipo, 
                    'Problema': problema,
                    'Prioridad': prioridad, 
                    'Estado': 'PENDIENTE', 
                    'Solucion': '---'
                }])
                df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
                conn.update(data=df_actualizado)
                st.success(f"✅ Reporte #{nuevo_id} guardado correctamente.")
                # Forzamos una recarga limpia
                st.cache_data.clear()
            else:
                st.warning("⚠️ Por favor, completa todos los campos.")

# Las otras opciones (Ingeniería y Gestión) seguirlas con la misma lógica de 'key' única.

# --- OPCIÓN 2: INGENIERÍA ---
elif choice == "🔧 Panel de Ingeniería":
    password = st.text_input("Clave de Acceso", type="password")
    if password == CLAVE_ADMIN:
        pendientes = df[df['Estado'] == 'PENDIENTE']
        if pendientes.empty:
            st.info("Sin averías pendientes.")
        else:
            id_sel = st.selectbox("ID a resolver", pendientes['ID'].tolist())
            solucion_txt = st.text_input("📝 Diagnóstico Técnico")
            if st.button("Validar y Cerrar"):
                df.loc[df['ID'] == id_sel, 'Estado'] = 'REPARADO'
                df.loc[df['ID'] == id_sel, 'Solucion'] = solucion_txt
                conn.update(data=df)
                st.success("✅ Actualizado en Google Sheets.")
                st.rerun()

# --- OPCIÓN 3: GESTIÓN ---
elif choice == "📊 Gestión":
    password = st.text_input("Clave de Acceso", type="password")
    if password == CLAVE_ADMIN:
        st.metric("Total Averías", len(df))
        st.bar_chart(df['Sector'].value_counts())
        st.dataframe(df)
