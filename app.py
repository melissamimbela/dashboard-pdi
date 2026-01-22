import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import os

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Informe PDI Chinalco", layout="wide")
st.markdown("<style>.stApp{background-color:#FFFFFF;} [data-testid='stMetricValue']{background-color:#F8F9F9;padding:15px;border-radius:10px;box-shadow:2px 2px 5px rgba(0,0,0,0.05);color:#1C2833;} .titulo-seccion{color:#1B2631;border-bottom:2px solid #1A5276;padding-bottom:5px;margin-top:20px;font-weight:bold;}</style>", unsafe_allow_html=True)

# 2. CARGA DE LOGOS
def get_img(path):
    if os.path.exists(path):
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    return None

c1, c2, c3 = st.columns([1, 3, 1])
l_sp = get_img("images.png")
l_ch = get_img("minera_chinalco_peru_sa_logo-Mayra-Fierro.jpg")

with c1: 
    if l_sp: st.markdown(f'<img src="data:image/png;base64,{l_sp}" width="180">', unsafe_allow_html=True)
with c2: 
    st.markdown("<h1 style='text-align:center;color:#1B2631;font-size:2.2rem;'>INFORME GENERAL PDI'S CHINALCO</h1>", unsafe_allow_html=True)
with c3: 
    if l_ch: st.markdown(f'<div style="text-align:right;"><img src="data:image/jpeg;base64,{l_ch}" width="180"></div>', unsafe_allow_html=True)

# 3. DATOS
@st.cache_data
def load():
    try:
        df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=1)
        df.columns = df.columns.astype(str).str.strip().str.upper()
        df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
        for c in df.columns: df[c] = df[c].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

df = load()
if not df.empty:
    c_per = [c for c in df.columns if 'MENTEE' in c][0]
    c_hab = [c for c in df.columns if 'HABILIDAD' in c][0]
    c_tip = [c for c in df.columns if 'TIPO' in c][0]
    c_rec = [c for c in df.columns if 'RECURSO' in c and 'TIPO' not in c][0]
    c_act = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

    # FILTROS
    sel = st.sidebar.selectbox("Seleccionar Colaborador:", ["TODOS"] + sorted(df[c_per].unique()))
    df_f = df if sel == "TODOS" else df[df[c_per] == sel]

    # INDICADORES ACTUALIZADOS (OCULTANDO PDI'S)
    header = "Análisis Consolidado" if sel == "TODOS" else f"Detalle Individual: {sel}"
    st.markdown(f"<h2 class='titulo-seccion'>👤 {header}</h2>", unsafe_allow_html=True)
    
    # Solo 2 columnas para que los indicadores se vean más grandes
    k1, k2 = st.columns(2)
    k1.metric("Cantidad de Habilidades", len(df_f[c_hab].unique()))
    k2.metric("Total de Acciones", len(df_f))

    # GRÁFICO DE TORTA
    st.markdown("<h3 class='titulo-seccion'>📊 Distribución de Acciones por PDI</h3>", unsafe_allow_html=True)
    counts = df_f[c_tip].value_counts().reset_index()
    counts.columns = [c_tip, 'CANT']
    fig = px.pie(counts, values='CANT', names=c_tip, color_discrete_sequence=['#1A5276', '#E67E22', '#1D8348'])
    fig.update_traces(textinfo='value+percent', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    # TABLA RESUMEN
    st.markdown("<h3 class='titulo-seccion'>📋 Cuadro Resumen de Recursos por Tipo</h3>", unsafe_allow_html=True)
    res = df_f.groupby([c_tip, c_rec]).size().reset_index(name='TOTAL')
    st.table(res)

    # DETALLE POR PERSONA
    if sel != "TODOS":
        st.markdown(f"<h3 class='titulo-seccion'>📝 Acciones Específicas: {sel}</h3>", unsafe_allow_html=True)
        det = df_f[[c_hab, c_tip, c_act]]
        det.columns = ['HABILIDAD', 'MODELO', 'ACCIÓN ESPECÍFICA']
        st.table(det)
    else:
        st.info("💡 Selecciona un colaborador para ver sus acciones detalladas.")
else:
    st.error("No se encontraron datos. Revisa el archivo 'datos.csv.xlsx'.")
