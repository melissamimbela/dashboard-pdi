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
logo_spira = get_image_base64("images.png")
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
    try:
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
        
        # Limpieza y conversión de Recursos a número entero
        if 'RECURSO' in df.columns:
            df['RECURSO'] = pd.to_numeric(df['RECURSO'], errors='coerce').fillna(0).astype(int)
        
        for col in df.columns:
            if col != 'RECURSO':
                df[col] = df[col].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        col_persona = [c for c in df.columns if 'MENTEE' in c][0]
        col_tipo = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]
        col_subtipo = [c for c in df.columns if 'ACCIÓN' in c or 'ACCION' in c][0]

        # --- PANEL LATERAL ---
        st.sidebar.header("Filtros Globales")
        persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", ["TODOS"] + sorted(df[col_persona].unique()))
        tipo_sel = st.sidebar.selectbox("Tipo de Acción:", ["TODOS"] + sorted(df[col_tipo].unique()))
        subtipo_sel = st.sidebar.selectbox("Subtipo de Acción:", ["TODOS"] + sorted(df[col_subtipo].unique()))

        # Filtrado lógico
        df_f = df.copy()
        if persona_sel != "TODOS": df_f = df_f[df_f[col_persona] == persona_sel]
        if tipo_sel != "TODOS": df_f = df_f[df_f[col_tipo] == tipo_sel]
        if subtipo_sel != "TODOS": df_f = df_f[df_f[col_subtipo] == subtipo_sel]

        # --- RESUMEN DE INICIO (RECURSOS Y ESTRATEGIA) ---
        st.markdown(f"### 📊 Resumen Ejecutivo: {persona_sel}")
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Personas con PDI", len(df[col_persona].unique()))
        m2.metric("Total Recursos", int(df_f['RECURSO'].sum()))
        m3.metric("Tipos de Acción", len(df_f[col_tipo].unique()))
        m4.metric("Subtipos Activos", len(df_f[col_subtipo].unique()))

        # --- ANÁLISIS POR TIPO Y SUBTIPO ---
        st.markdown("---")
        st.subheader("📌 Análisis de Inversión y Estrategia")
        
        # Tabla resumen por Tipo y Subtipo (Sin mostrar las acciones individuales)
        resumen_estrategia = df_f.groupby([col_tipo, col_subtipo]).agg({
            'RECURSO': 'sum',
            col_persona: 'nunique'
        }).reset_index()
        
        resumen_estrategia.columns = ['TIPO DE ACCIÓN', 'SUBTIPO DE ACCIÓN', 'RECURSOS TOTALES', 'CANT. PERSONAS']
        st.table(resumen_estrategia)

        # --- GRÁFICOS DE DISTRIBUCIÓN ---
        st.markdown("---")
        c1, c2 = st.columns(2)
        
        with c1:
            # Distribución por Subtipo (Cantidad)
            fig1 = px.pie(df_f, names=col_subtipo, title="Distribución por Subtipo de Acción", hole=0.4)
            fig1.update_traces(textinfo='percent+label')
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            # Recursos por Tipo de Acción
            fig2 = px.bar(resumen_estrategia, x='TIPO DE ACCIÓN', y='RECURSOS TOTALES', 
                          color='SUBTIPO DE ACCIÓN', title="Inversión de Recursos por Categoría")
            st.plotly_chart(fig2, use_container_width=True)

        # Las acciones solo se ven en un desplegable opcional al final
        with st.expander("Ver listado de acciones detalladas (opcional)"):
            st.dataframe(df_f[[col_persona, col_tipo, col_subtipo]], use_container_width=True)

except Exception as e:
    st.info("Cargando información del PDI...")
