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
        df_raw = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=1)
        df = df_raw.copy()
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
        col_recurso_tipo = [c for c in df.columns if 'RECURSO' in c and 'TIPO' not in c][0] # La columna que tiene "Herramientas", "Mentoria", etc.

        # --- PANEL LATERAL ---
        st.sidebar.header("Filtros")
        persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", ["TODOS"] + sorted(df[col_persona].unique()))
        
        df_final = df if persona_sel == "TODOS" else df[df[col_persona] == persona_sel]

        # --- 1. RESUMEN DE INDICADORES CLAVE ---
        st.markdown(f"### 👤 { 'Análisis General' if persona_sel == 'TODOS' else 'Reporte: ' + persona_sel }")
        m1, m2, m3 = st.columns(3)
        m1.metric("Cantidad de PDI's", len(df_final[col_persona].unique()))
        m2.metric("Cantidad de Habilidades", len(df_final[col_habilidad].unique()))
        m3.metric("Total Acciones", len(df_final))

        # --- 2. GRÁFICO: DISTRIBUCIÓN DE ACCIONES POR PDI ---
        st.markdown("---")
        st.subheader("Distribución de Acciones por PDI")
        
        df_counts = df_final[col_tipo].value_counts().reset_index()
        df_counts.columns = [col_tipo, 'CANTIDAD']
        
        fig_pie = px.pie(df_counts, values='CANTIDAD', names=col_tipo, 
                         color_discrete_map={
                             '70% Experiencia Practica': '#1A5276',
                             '20% Mentoría y Retroalimentación': '#E67E22',
                             '10% Formación Formal': '#1D8348'
                         })
        fig_pie.update_traces(textinfo='value+percent', textposition='outside')
        fig_pie.update_layout(showlegend=True, legend_title="TIPO DE ACCIÓN")
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- 3. CUADRO RESUMEN: TIPO DE ACCIÓN Y RECURSO ---
        st.markdown("---")
        st.subheader("Cuadro Resumen de Recursos por Tipo")
        
        # Agrupación para imitar la tabla de la imagen
        resumen_tabla = df_final.groupby([col_tipo, col_recurso_tipo]).size().reset_index(name='Total')
        
        # Mostramos la tabla formateada
        st.table(resumen_tabla)

        # Totales por categoría principal
        st.markdown("**Totales por Tipo de Acción:**")
        st.write(df_final[col_tipo].value_counts())

except Exception as e:
    st.error(f"Error en la visualización: {e}")
