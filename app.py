import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# 1. CONFIGURACIÓN DE PÁGINA Y COLOR DE FONDO (PLOMO CLARO)
st.set_page_config(page_title="Dashboard PDI Chinalco", layout="wide")

st.markdown("""
    <style>
    /* Forzar fondo plomo claro en toda la aplicación */
    .stApp {
        background-color: #E5E7E9;
    }
    
    /* Estilo para las tarjetas de métricas */
    [data-testid="stMetricValue"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
        color: #1C2833;
    }
    
    /* Estilo para los títulos de las métricas */
    [data-testid="stMetricLabel"] {
        font-weight: bold;
        color: #566573;
    }

    /* Fondo blanco para las tablas */
    .stTable {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA CARGAR LOGOS
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# 3. ENCABEZADO CON LOGOS
col_logo1, col_titulo, col_logo2 = st.columns([1, 2, 1])
logo_spira = get_image_base64("logo_spira.png")
logo_chinalco = get_image_base64("logo_chinalco.jpg")

with col_logo1:
    if logo_spira: 
        st.markdown(f'<img src="data:image/png;base64,{logo_spira}" width="180">', unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h1 style='text-align: center; color: #1B2631; padding-top: 10px;'>DASHBOARD INTERACTIVO PDI</h1>", unsafe_allow_html=True)
with col_logo2:
    if logo_chinalco: 
        st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_chinalco}" width="180"></div>', unsafe_allow_html=True)

# 4. CARGA DE DATOS ROBUSTA
@st.cache_data
def load_data():
    df_raw = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', header=None)
    header_row = 0
    for i in range(len(df_raw)):
        row_values = df_raw.iloc[i].astype(str).str.upper().values
        if 'MENTEE' in row_values or 'LÍDER MENTOR' in row_values:
            header_row = i
            break
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=header_row)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
    df = df.dropna(how='all', axis=0).reset_index(drop=True)
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
    return df

try:
    df = load_data()
    
    # Identificación de columnas
    col_persona = [c for c in df.columns if 'MENTEE' in c][0]
    col_habilidad = [c for c in df.columns if 'HABILIDAD' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_tipo_accion = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]

    # --- PANEL LATERAL ---
    st.sidebar.markdown("### 🔍 Filtros")
    lista_personas = sorted([p for p in df[col_persona].unique() if p not in ['nan', 'None', '']])
    persona_sel = st.sidebar.selectbox("Seleccionar Colaborador (Mentee):", lista_personas)
    
    df_pers = df[df[col_persona] == persona_sel]

    # --- CUADRO 1: RESUMEN DE PORTADA ---
    st.markdown(f"### 📋 Resumen Profesional: {persona_sel}")
    
    m1, m2, m3 = st.columns(3)
    
    habilidades_count = len([h for h in df_pers[col_habilidad].unique() if h != 'nan'])
    m1.metric("HABILIDADES", habilidades_count)
    m2.metric("ACCIONES TOTALES", len(df_pers))
    m3.metric("TIPOS DE ACCIÓN", len(df_pers[col_tipo_accion].unique()))

    # --- CUADRO 2: TABLA DE RESUMEN ---
    st.markdown("---")
    st.subheader("📌 Desglose por Habilidad y Acciones")
    
    resumen_per = df_pers.groupby(col_habilidad).agg({
        col_accion: 'count',
        col_tipo_accion: lambda x: ', '.join(sorted(x.unique()))
    }).reset_index()
    
    resumen_per.columns = ['HABILIDAD A DESARROLLAR', 'CANTIDAD DE ACCIONES', 'TIPOS DE ACCIONES (MIX)']
    
    # Mostrar tabla centrada
    st.table(resumen_per)

    # --- GRÁFICOS ---
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df_pers, names=col_tipo_accion, 
                         title="Mix de Aprendizaje (70-20-10)", 
                         color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(resumen_per, x='HABILIDAD A DESARROLLAR', y='CANTIDAD DE ACCIONES', 
                         title="Acciones por Habilidad", 
                         color='HABILIDAD A DESARROLLAR',
                         text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

except Exception as e:
    st.error(f"Error en la visualización: {e}")
