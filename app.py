import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# 1. CONFIGURACIÓN DE PÁGINA (FONDO BLANCO PARA LOGOS)
st.set_page_config(page_title="Dashboard PDI Chinalco", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    [data-testid="stMetricValue"] {
        background-color: #F8F9F9;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
        color: #1C2833;
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNCIÓN PARA CARGAR LOGOS
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# 3. ENCABEZADO
col_logo1, col_titulo, col_logo2 = st.columns([1, 2, 1])
logo_spira = get_image_base64("logo_spira.png")
logo_chinalco = get_image_base64("minera_chinalco_peru_sa_logo-Mayra-Fierro.jpg")

with col_logo1:
    if logo_spira: st.markdown(f'<img src="data:image/png;base64,{logo_spira}" width="180">', unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h1 style='text-align: center; color: #1B2631;'>DASHBOARD INTERACTIVO PDI</h1>", unsafe_allow_html=True)
with col_logo2:
    if logo_chinalco: st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_chinalco}" width="180"></div>', unsafe_allow_html=True)

# 4. CARGA DE DATOS
@st.cache_data
def load_data():
    df_raw = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', header=None)
    header_row = 0
    for i in range(len(df_raw)):
        row_values = df_raw.iloc[i].astype(str).str.upper().values
        if 'MENTEE' in row_values:
            header_row = i
