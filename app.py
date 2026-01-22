import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Informe PDI Chinalco", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] {
        background-color: #F8F9F9;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        color: #1C2833;
    }
    .titulo-seccion {
        color: #1B2631;
        border-bottom: 2px solid #1A5276;
        padding-bottom: 5px;
        margin-top: 20px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE LOGOS
def get_image_base64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

col_logo1, col_titulo, col_logo2 = st.columns([1, 3, 1])
logo_spira = get_image_base64("images.png") 
logo_chinalco = get_image_base64("minera_chinalco_peru_sa_logo-Mayra-Fierro.jpg")

with col_logo1:
    if logo_spira: st.markdown(f'<img src="data:image/png;base64,{logo_spira}" width="180">', unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h1 style='text-align: center; color: #1B2631; font-size: 2.2rem; margin-top: 10px;'>INFORME GENERAL PDI'S CHINALCO</h1>", unsafe_allow_html=True)
with col_logo2:
    if logo_chinalco: st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_chinalco}" width="180"></div>', unsafe_allow_html=True)

# 3. CARGA DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=1)
        df.columns = df.columns.astype(str).str.strip().str.upper()
        df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        col_persona = [c for c in df.columns if 'MENTEE' in c][0]
        col_habilidad = [c for c in df.columns if 'HABILIDAD' in c][0]
        col_tipo = [c for c in df.columns if 'TIPO' in c][0]
        col_recurso_desc = [c for c in df.columns if 'RECURSO' in c and 'TIPO' not in c][0]
        col_accion_texto = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

        # PANEL LATERAL
        persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", ["TODOS"] + sorted(df[col_persona].unique()))
        df_final = df if persona_sel == "TODOS" else df[df[col_persona] == persona_sel]

        # INDICADORES
        txt_header = "Análisis Consolidado" if persona_sel == "TODOS" else f"Detalle Individual: {persona_sel}"
        st.markdown(f"<h2 class='titulo-seccion'>👤 {txt_header}</h2>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Cantidad de PDI's", len(df_final[col_persona].unique()))
        m2.metric("Cantidad de Habilidades", len(df_final[col_habilidad].unique()))
        m3.metric("Total de Acciones", len(df_final))

        # GRÁFICO
        st.markdown("<h3 class='titulo-seccion'>📊 Distribución de Acciones por PDI</h3>", unsafe_allow_html=True)
        df_counts = df_final[col_tipo].value_counts().reset_index()
        df_counts.columns = [col_tipo, 'CANTIDAD']
        fig_pie = px.pie(df_counts, values='CANTIDAD', names=col_
