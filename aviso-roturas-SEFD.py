import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="HOSPITAL - Gestión Cloud", page_icon="🏥")
SECTORES = ["Guardia Central", "Internado", "UTI1", "UTI2", "Consultorios", "Quirófano"]
CLAVE_ADMIN = "1234"

# --- CONEXIÓN A GOOGLE SHEETS ---
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    return conn.read(ttl="0") # ttl="0" para que no guarde caché y lea siempre lo último

# --- INTERFAZ ---
st.title("🏥 Sistema de Gestión Hospitalaria")
menu = ["📝 Reportar Avería", "🔧 Panel de Ingeniería", "📊 Gestión"]
choice = st.sidebar.selectbox("Menú Principal", menu)

df = leer_datos()

# --- OPCIÓN 1: REPORTE ---
if choice == "📝 Reportar Avería":
    st.header("Nuevo Reporte de Fallo")
    with st.form("form_reporte", clear_on_submit=True):
        sector = st.selectbox("📍 Sector", SECTORES)
        equipo = st.text_input("🏥 Equipo")
        problema = st.text_area("🛠️ Descripción")
        prioridad = st.select_slider("⚠️ Prioridad", options=["Baja", "Media", "Alta", "CRÍTICA"])
        submit = st.form_submit_button("Enviar Reporte")
        
        if submit:
            nuevo_id = int(df['ID'].max() + 1) if not df.empty else 1
            nueva_fila = pd.DataFrame([{
                'ID': nuevo_id,
                'Fecha': datetime.now().strftime("%d/%m %Y %H:%M"),
                'Sector': sector, 'Equipo': equipo, 'Problema': problema,
                'Prioridad': prioridad, 'Estado': 'PENDIENTE', 'Solucion': '---'
            }])
            df_actualizado = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(data=df_actualizado)
            st.success(f"✅ Reporte #{nuevo_id} guardado en la nube.")

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
