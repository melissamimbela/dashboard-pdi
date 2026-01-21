import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# 1. CONFIGURACIÓN DE PÁGINA
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
            break
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=header_row)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    return df

try:
    df = load_data()
    col_persona = [c for c in df.columns if 'MENTEE' in c][0]
    col_habilidad = [c for c in df.columns if 'HABILIDAD' in c][0]
    col_tipo = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

    # --- PANEL LATERAL CON DESPLEGABLES ---
    st.sidebar.header("Filtros")
    
    # 1. Desplegable de Persona
    lista_personas = sorted([p for p in df[col_persona].unique() if p not in ['nan', 'None']])
    persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", lista_personas)
    df_persona = df[df[col_persona] == persona_sel]

    # 2. Desplegable de Tipo de Acción (NUEVO)
    opciones_tipo = ["TODOS"] + sorted(list(df_persona[col_tipo].unique()))
    tipo_sel = st.sidebar.selectbox("Filtrar por Tipo de Acción:", opciones_tipo)

    # Aplicar filtros
    if tipo_sel == "TODOS":
        df_final = df_persona
    else:
        df_final = df_persona[df_persona[col_tipo] == tipo_sel]

    # --- PORTADA ---
    st.markdown(f"### 👤 Reporte de PDI: {persona_sel}")
    m1, m2, m3 = st.columns(3)
    
    m1.metric("Habilidades", len(df_final[col_habilidad].unique()))
    m2.metric("Total de Acciones", len(df_final))
    
    tipos_presentes = ", ".join(sorted(df_final[col_tipo].unique()))
    m3.metric("Tipos en Pantalla", tipos_presentes)

    # --- TABLA RESUMEN ---
    st.markdown("---")
    st.subheader(f"📌 Resumen: {tipo_sel}")
    
    resumen_hab = df_final.groupby(col_habilidad).agg({
        col_tipo: lambda x: ', '.join(sorted(x.unique())),
        col_accion: 'count'
    }).reset_index()
    
    resumen_hab.columns = ['HABILIDAD', 'TIPO', 'ACCIONES']
    st.table(resumen_hab)

    # --- LISTADO DETALLADO ---
    st.markdown("---")
    st.subheader("📝 Listado Detallado de Acciones")
    
    detalle_acciones = df_final[[col_habilidad, col_tipo, col_accion]]
    detalle_acciones.columns = ['HABILIDAD', 'TIPO', 'ACCIÓN ESPECÍFICA']
    st.dataframe(detalle_acciones.reset_index(drop=True), use_container_width=True)

except Exception as e:
    st.error(f"Error al filtrar: {e}")
