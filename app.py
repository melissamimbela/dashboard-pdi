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
        background-color: #F0F2F6;
        padding: 20px;
        border-radius: 10px;
        color: #1B2631;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE LOGOS
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

# ENCABEZADO
col_l1, col_tit, col_l2 = st.columns([1, 2, 1])
logo_sp = get_image_base64("images.png")
logo_ch = get_image_base64("minera_chinalco_peru_sa_logo-Mayra-Fierro.jpg")

with col_l1:
    if logo_sp: st.markdown(f'<img src="data:image/png;base64,{logo_sp}" width="150">', unsafe_allow_html=True)
with col_tit:
    st.markdown("<h1 style='text-align: center; color: #1B2631;'>ANÁLISIS ESTRATÉGICO PDI</h1>", unsafe_allow_html=True)
with col_l2:
    if logo_ch: st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_ch}" width="150"></div>', unsafe_allow_html=True)

# 3. PROCESAMIENTO DE DATOS
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=1) # Ajustado según tu estructura
        df.columns = df.columns.astype(str).str.strip().str.upper()
        # Limpiar columnas vacías
        df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
        # Recursos a entero
        if 'RECURSO' in df.columns:
            df['RECURSO'] = pd.to_numeric(df['RECURSO'], errors='coerce').fillna(0).astype(int)
        return df
    except: return pd.DataFrame()

df = load_data()

if not df.empty:
    # Identificar columnas
    c_per = [c for c in df.columns if 'MENTEE' in c][0]
    c_hab = [c for c in df.columns if 'HABILIDAD' in c][0]
    c_tip = [c for c in df.columns if 'TIPO' in c][0]
    c_sub = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

    # --- FILTRO LATERAL ---
    persona_sel = st.sidebar.selectbox("Filtrar por Colaborador:", ["TODOS"] + sorted(df[c_per].unique()))
    df_f = df if persona_sel == "TODOS" else df[df[c_per] == persona_sel]

    # --- SECCIÓN 1: RESUMEN DE INDICADORES (KPIs) ---
    st.markdown("### 📊 Indicadores Clave")
    k1, k2, k3 = st.columns(3)
    k1.metric("Cantidad de PDIs", len(df_f[c_per].unique()))
    k2.metric("Habilidades en Desarrollo", len(df_f[c_hab].unique()))
    k3.metric("Inversión Total Recursos", f"{int(df_f['RECURSO'].sum())}")

    st.markdown("---")

    # --- SECCIÓN 2: CUADRO RESUMEN DE RECURSOS Y ESTRATEGIA ---
    st.subheader("📌 Cuadro Resumen: Recursos y Tipología")
    
    # Agrupamos para mostrar el cuadro resumen solicitado
    resumen_cuadro = df_f.groupby([c_tip, c_sub]).agg({
        'RECURSO': 'sum',
        c_per: 'nunique'
    }).reset_index()
    resumen_cuadro.columns = ['TIPO', 'SUBTIPO', 'RECURSO ACUMULADO', 'PERSONAS']
    
    st.table(resumen_cuadro)

    # --- SECCIÓN 3: ANÁLISIS GRÁFICO ---
    st.markdown("---")
    st.subheader("📈 Análisis Gráfico de Distribución")
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        # Gráfico de Torta: % de Tipo de Acción
        fig_pie = px.pie(df_f, names=c_tip, title="Mix de Aprendizaje (%)", 
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with col_g2:
        # Gráfico de Barras: Recursos por Subtipo
        fig_bar = px.bar(resumen_cuadro, x='SUBTIPO', y='RECURSO ACUMULADO', color='TIPO',
                         title="Inversión por Subtipo de Acción",
                         text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

    # El detalle de acciones queda oculto al final solo por si necesitas consultarlo
    with st.expander("🔍 Ver detalle de acciones individuales"):
        st.dataframe(df_f[[c_per, c_hab, c_tip, c_sub]], use_container_width=True)
else:
    st.error("No se pudieron cargar los datos. Verifica el archivo Excel.")
