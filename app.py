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
    .titulo-seccion {
        color: #1B2631;
        border-bottom: 2px solid #1A5276;
        padding-bottom: 5px;
        margin-top: 20px;
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
        # Cargamos saltando la primera fila de logos/títulos del Excel
        df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', skiprows=1)
        df.columns = df.columns.astype(str).str.strip().str.upper()
        df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
        
        # Limpieza de espacios en blanco
        for col in df.columns:
            df[col] = df[col].astype(str).str.strip()
        return df
    except: return pd.DataFrame()

try:
    df = load_data()
    if not df.empty:
        # Identificación dinámica de columnas
        col_persona = [c for c in df.columns if 'MENTEE' in c][0]
        col_habilidad = [c for c in df.columns if 'HABILIDAD' in c][0]
        col_tipo = [c for c in df.columns if 'TIPO' in c][0]
        col_recurso_desc = [c for c in df.columns if 'RECURSO' in c and 'TIPO' not in c][0]
        # Columna de la acción específica (el texto de la tarea)
        col_accion_texto = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]

        # --- PANEL LATERAL ---
        st.sidebar.header("Filtros")
        persona_sel = st.sidebar.selectbox("Seleccionar Colaborador:", ["TODOS"] + sorted(df[col_persona].unique()))
        
        # Filtrado de datos
        df_final = df if persona_sel == "TODOS" else df[df[col_persona] == persona_sel]

        # --- 1. RESUMEN DE INDICADORES CLAVE ---
        st.markdown(f"<h2 class='titulo-seccion'>👤 {'Vista General Organizacional' if persona_sel == 'TODOS' else 'Plan de Desarrollo: ' + persona_sel}</h2>", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("PDI's en pantalla", len(df_final[col_persona].unique()))
        m2.metric("Habilidades", len(df_final[col_habilidad].unique()))
        m3.metric("Total Acciones", len(df_final))

        # --- 2. GRÁFICO DE DISTRIBUCIÓN ---
        st.markdown("<h3 class='titulo-seccion'>📊 Distribución de Acciones por PDI</h3>", unsafe_allow_html=True)
        df_counts = df_final[col_tipo].value_counts().reset_index()
        df_counts.columns = [col_tipo, 'CANTIDAD']
        
        fig_pie = px.pie(df_counts, values='CANTIDAD', names=col_tipo, 
                         color_discrete_sequence=['#1A5276', '#E67E22', '#1D8348'])
        fig_pie.update_traces(textinfo='value+percent', textposition='outside')
        st.plotly_chart(fig_pie, use_container_width=True)

        # --- 3. CUADRO RESUMEN DE RECURSOS ---
        st.markdown("<h3 class='titulo-seccion'>📋 Cuadro Resumen de Recursos</h3>", unsafe_allow_html=True)
        resumen_tabla = df_final.groupby([col_tipo, col_recurso_desc]).size().reset_index(name='CONTEO')
        st.table(resumen_tabla)

        # --- 4. DETALLE DE ACCIONES (SOLO VISIBLE POR PERSONA O SELECCIÓN) ---
        if persona_sel != "TODOS":
            st.markdown(f"<h3 class='titulo-seccion'>📝 Acciones Detalladas para {persona_sel}</h3>", unsafe_allow_html=True)
            detalle = df_final[[col_habilidad, col_tipo, col_accion_texto]]
            detalle.columns = ['HABILIDAD A DESARROLLAR', 'MODELO', 'ACCIÓN ESPECÍFICA']
            
            # Mostramos las acciones en un formato de tabla más cómodo para leer texto largo
            st.dataframe(detalle.reset_index(drop=True), use_container_width=True)
        else:
            # En vista TODOS, podemos poner un buscador rápido por si quieren ver algo puntual
            with st.expander("🔍 Ver todas las acciones de la organización (Lista completa)"):
                st.dataframe(df[[col_persona, col_habilidad, col_accion_texto]], use_container_width=True)

except Exception as e:
    st.error(f"Error al cargar la vista: {e}")
