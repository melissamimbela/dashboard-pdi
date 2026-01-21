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

# 4. CARGA DE DATOS ROBUSTA
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
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except Exception as e:
        return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        col_persona = [c for c in df.columns if 'MENTEE' in c][0]
        col_habilidad = [c for c in df.columns if 'HABILIDAD' in c][0]
        col_tipo = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]
        col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

        # --- PANEL LATERAL ---
        st.sidebar.header("Filtros")
        lista_personas = sorted([p for p in df[col_persona].unique() if p not in ['nan', 'None']])
        persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", lista_personas)
        df_persona = df[df[col_persona] == persona_sel]

        opciones_tipo = ["TODOS"] + sorted(list(df_persona[col_tipo].unique()))
        tipo_sel = st.sidebar.selectbox("Filtrar por Tipo de Acción:", opciones_tipo)

        df_final = df_persona if tipo_sel == "TODOS" else df_persona[df_persona[col_tipo] == tipo_sel]

        # --- PORTADA ---
        # AQUÍ ESTABA EL ERROR, AHORA ESTÁ CERRADO CORRECTAMENTE
        st.markdown(f"### 👤 Reporte de PDI: {persona_sel}")
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Habilidades", len(df_final[col_habilidad].unique()))
        m2.metric("Total Acciones", len(df_final))
        m3.metric("Filtro Actual", tipo_sel)

        # --- GRÁFICOS ---
        st.markdown("---")
        st.subheader("📊 Distribución de Acciones por PDI")
        
        df_counts = df_final[col_tipo].value_counts().reset_index()
        df_counts.columns = [col_tipo, 'CANTIDAD']
        
        g1, g2 = st.columns(2)
        with g1:
            fig_pie = px.pie(df_counts, values='CANTIDAD', names=col_tipo, title="Distribución (%)", hole=0.3)
            fig_pie.update_traces(textinfo='percent+value')
            st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            fig_bar = px.bar(df_counts, x=col_tipo, y='CANTIDAD', title="Cantidad por Tipo", text='CANTIDAD', color=col_tipo)
            st.plotly_chart(fig_bar, use_container_width=True)

        # --- TABLAS ---
        st.markdown("---")
        st.subheader("📌 Resumen de Habilidades")
        resumen_hab = df_final.groupby(col_habilidad).agg({col_tipo: lambda x: ', '.join(sorted(x.unique())), col_accion: 'count'}).reset_index()
        resumen_hab.columns = ['HABILIDAD', 'TIPO', 'ACCIONES']
        st.table(resumen_hab)

        st.markdown("---")
        st.subheader("📝 Listado Detallado de Acciones")
        detalle = df_final[[col_habilidad, col_tipo, col_accion]]
        detalle.columns = ['HABILIDAD', 'TIPO', 'ACCIÓN ESPECÍFICA']
        st.dataframe(detalle.reset_index(drop=True), use_container_width=True)

except Exception as e:
    st.info("Cargando datos... Verifique que los filtros coincidan con su archivo Excel.")
