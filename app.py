import streamlit as st
import pandas as pd
import plotly.express as px
import base64

# 1. Configuración de página y Estilo CSS (Fondo Plomo Claro)
st.set_page_config(page_title="Dashboard PDI", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #F0F2F6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    div[data-testid="stTable"] {
        background-color: #ffffff;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Función para cargar logos
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# 3. Encabezado con Logos
col_logo1, col_titulo, col_logo2 = st.columns([1, 2, 1])
logo_spira = get_image_base64("logo_spira.png")
logo_chinalco = get_image_base64("logo_chinalco.jpg")

with col_logo1:
    if logo_spira:
        st.markdown(f'<img src="data:image/png;base64,{logo_spira}" width="150">', unsafe_allow_html=True)
with col_titulo:
    st.markdown("<h1 style='text-align: center; color: #31333F;'>Dashboard Interactivo PDI</h1>", unsafe_allow_html=True)
with col_logo2:
    if logo_chinalco:
        st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_chinalco}" width="150"></div>', unsafe_allow_html=True)

# 4. Carga de Datos
@st.cache_data
def load_data():
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS')
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    # Limpieza de columnas "Unnamed" o vacías
    df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
    df = df.dropna(how='all', axis=0)
    
    # Convertir a texto para evitar errores de tipo
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
    return df

try:
    df = load_data()
    
    # Definición de columnas clave basándome en tus capturas
    col_persona = "MENTEE"
    col_habilidad = "HABILIDAD A DESARROLLAR"
    col_accion = "ACCION"
    col_tipo_accion = "TIPO DE ACCIÓN"

    # --- PANEL LATERAL ---
    st.sidebar.header("Filtros de Búsqueda")
    lista_personas = sorted([p for p in df[col_persona].unique() if p != 'nan'])
    persona_sel = st.sidebar.selectbox("Selecciona a la Persona (Mentee)", lista_personas)
    
    # Filtrar datos por la persona seleccionada
    df_pers = df[df[col_persona] == persona_sel]

    # --- CUADRO 1: PORTADA RESUMEN POR PERSONA ---
    st.markdown(f"### 👤 Resumen de PDI: {persona_sel}")
    
    m1, m2, m3 = st.columns(3)
    
    # Cantidad de habilidades únicas
    cant_habilidades = len(df_pers[col_habilidad].unique())
    # Cantidad de acciones totales
    cant_acciones = len(df_pers)
    # Tipos de acciones únicas (Ej: 70, 20, 10)
    cant_tipos = len(df_pers[col_tipo_accion].unique())

    m1.metric("Cantidad de Habilidades", cant_habilidades)
    m2.metric("Total de Acciones", cant_acciones)
    m3.metric("Diversidad de Tipos", cant_tipos)

    # --- CUADRO 2: DETALLE DE HABILIDADES Y ACCIONES ---
    st.markdown("---")
    st.subheader("📋 Detalle de Habilidades y Tipos de Acciones")

    # Creamos una tabla que agrupe por Habilidad para ver cuántas acciones tiene cada una
    resumen_tabla = df_pers.groupby([col_habilidad, col_tipo_accion]).size().reset_index(name='CANTIDAD DE ACCIONES')
    
    # Mejoramos la visualización de la tabla
    st.table(resumen_tabla)

    # --- GRÁFICOS ---
    st.markdown("---")
    c1, c2 = st.columns(2)
    
    with c1:
        # Distribución de Tipos de Acciones para esta persona
        fig_pie = px.pie(df_pers, names=col_tipo_accion, title=f"Mix de Aprendizaje (70-20-10)", hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Acciones por Habilidad
        fig_bar = px.bar(resumen_tabla, x=col_habilidad, y='CANTIDAD DE ACCIONES', 
                         color=col_tipo_accion, title="Acciones por Habilidad")
        st.plotly_chart(fig_bar, use_container_width=True)

    # Detalle final
    with st.expander("Ver todas las acciones detalladas"):
        st.dataframe(df_pers[[col_habilidad, col_accion, col_tipo_accion]], use_container_width=True)

except Exception as e:
    st.error(f"Error al generar el dashboard: {e}")
    st.info("Asegúrate de que las columnas 'MENTEE', 'HABILIDAD A DESARROLLAR' y 'TIPO DE ACCIÓN' existan en tu Excel.")
