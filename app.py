import streamlit as st
import pandas as pd
import plotly.express as px
import os

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

# 2. Función para cargar datos (Corregida para Excel)
@st.cache_data
def load_data():
    # Usamos el nombre real que detectamos: datos.csv.xlsx
    # Se requiere la librería 'openpyxl' en requirements.txt
    df = pd.read_excel('datos.csv.xlsx')
    
    # Limpiamos la columna de texto para evitar errores en los filtros
    if 'LÍDER MENTOR' in df.columns:
        df['LÍDER MENTOR'] = df['LÍDER MENTOR'].astype(str).str.replace('\n', ' ', regex=True)
    return df

# 3. Lógica principal con manejo de errores
try:
    df = load_data()

    # --- BARRA LATERAL (Filtros) ---
    st.sidebar.header("Filtros")
    # Mostramos qué archivos ve el sistema para diagnóstico
    st.sidebar.write("Archivos en servidor:", os.listdir('.'))
    
    mentor_list = sorted(df["LÍDER MENTOR"].unique())
    mentor = st.sidebar.selectbox("Selecciona un Líder Mentor", mentor_list)

    # Filtrar datos
    df_filtro = df[df["LÍDER MENTOR"] == mentor]

    # --- CUERPO DEL DASHBOARD ---
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de Pastel (70-20-10)
        fig_pie = px.pie(
            df_filtro, 
            names='TIPO DE ACCIÓN', 
            title=f'Modelo 70-20-10: {mentor}',
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Gráfico de Barras (Criticidad)
        counts = df_filtro['CRITICIDAD'].value_counts().reset_index()
        counts.columns = ['Nivel', 'Cantidad']
        fig_bar = px.bar(
            counts, 
            x='Nivel', 
            y='Cantidad', 
            title='Distribución por Criticidad',
            color='Nivel'
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla detallada al final
    st.subheader(f"Detalle de acciones: {mentor}")
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"❌ Error al cargar el dashboard: {e}")
    st.info("Revisa que el archivo 'datos.csv.xlsx' esté en la raíz de tu GitHub.")
    st.write("Lista de archivos detectados:", os.listdir('.'))
