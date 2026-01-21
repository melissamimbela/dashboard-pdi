import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración visual
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

# 2. Función de carga de datos optimizada para tu archivo
@st.cache_data
def load_data():
    # Leemos la pestaña específica que me indicaste
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS')
    
    # Limpiamos nombres de columnas (quita espacios y pone todo en mayúsculas)
    df.columns = df.columns.str.strip().str.upper()
    
    # Eliminamos filas que estén totalmente vacías (por si hay basura al final del Excel)
    df = df.dropna(how='all').reset_index(drop=True)
    
    # Limpieza de textos en las celdas
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
        
    return df

# 3. Lógica principal
try:
    df = load_data()

    # Identificación automática de columnas clave
    # Esto busca columnas que contengan estas palabras sin importar tildes
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- PANEL LATERAL ---
    st.sidebar.header("Filtros de Análisis")
    
    # Selector de Mentor
    lista_mentores = sorted([m for m in df[col_mentor].unique() if m != 'nan'])
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", lista_mentores)

    # Aplicar Filtro
    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- DASHBOARD ---
    st.subheader(f"Resumen de Gestión: {mentor_sel}")
    
    # Métricas rápidas
    total_acciones = len(df_filtro)
    st.markdown(f"**Total de acciones registradas:** {total_acciones}")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico 70-20-10
        fig_pie = px.pie(
            df_filtro, 
            names=col_accion, 
            title='Distribución Modelo 70-20-10',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Gráfico de Barras de Criticidad
        resumen_crit = df_filtro[col_crit].value_counts().reset_index()
        resumen_crit.columns = ['Nivel', 'Cantidad']
        
        fig_bar = px.bar(
            resumen_crit, 
            x='Nivel', 
            y='Cantidad', 
            title='Acciones por Nivel de Criticidad',
            color='Nivel',
            text_auto=True,
