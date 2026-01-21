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

# 2. Función para cargar logos locales y convertirlos a base64
def get_image_base64(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# 3. Encabezado con Logos (Spira Izquierda - Chinalco Derecha)
col_logo1, col_titulo, col_logo2 = st.columns([1, 2, 1])

logo_spira = get_image_base64("logo_spira.png")
logo_chinalco = get_image_base64("logo_chinalco.jpg")

with col_logo1:
    if logo_spira:
        st.markdown(f'<img src="data:image/png;base64,{logo_spira}" width="150">', unsafe_allow_html=True)
    else:
        st.write("📌 Logo Spira")

with col_titulo:
    st.markdown("<h1 style='text-align: center; color: #31333F;'>Dashboard Interactivo PDI</h1>", unsafe_allow_html=True)

with col_logo2:
    if logo_chinalco:
        # Nota: usamos image/jpeg para el archivo jpg
        st.markdown(f'<div style="text-align: right;"><img src="data:image/jpeg;base64,{logo_chinalco}" width="150"></div>', unsafe_allow_html=True)
    else:
        st.write("📌 Logo Chinalco")

# 4. Carga de Datos
@st.cache_data
def load_data():
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS')
    
    # Limpieza de nombres de columnas
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    # Si los títulos no están en la primera fila, buscamos 'LÍDER MENTOR'
    if 'LÍDER MENTOR' not in df.columns:
        for i in range(len(df)):
            if 'LÍDER MENTOR' in df.iloc[i].astype(str).str.upper().values:
                df.columns = df.iloc[i].astype(str).str.strip().str.upper()
                df = df.iloc[i+1:].reset_index(drop=True)
                break

    # Limpiar columnas vacías de Plotly
    df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
    
    # Asegurar que RECURSO sea numérico
    if 'RECURSO' in df.columns:
        df['RECURSO'] = pd.to_numeric(df['RECURSO'], errors='coerce').fillna(0)
    else:
        # Si no existe la columna, creamos una de ejemplo con ceros para que no rompa el resumen
        df['RECURSO'] = 0
        
    return df

try:
    df = load_data()
    
    # Identificar columnas
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_tipo = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]
    col_recurso = 'RECURSO'

    # Filtro Lateral
    st.sidebar.header("Filtros")
    mentores = sorted([m for m in df[col_mentor].unique() if str(m).strip() != '' and str(m) != 'nan'])
    mentor_sel = st.sidebar.selectbox("Selecciona Líder Mentor", mentores)
    
    df_filtered = df[df[col_mentor] == mentor_sel]

    # --- CUADRO 1: RESUMEN GENERAL (PORTADA) ---
    st.markdown("### 📊 Portada: Resumen General")
    total_recursos_mentor = df_filtered[col_recurso].sum()
    total_global_recursos = df[col_recurso].sum()
    porcentaje_dist = (total_recursos_mentor / total_global_recursos * 100) if total_global_recursos > 0 else 0

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Tipo de Acción (Cant.)", len(df_filtered[col_tipo].unique()))
    with m2:
        st.metric("Recursos (Suma)", f"S/ {total_recursos_mentor:,.2f}")
    with m3:
        st.metric("% Distribución", f"{porcentaje_dist:.1f}%")

    # --- CUADRO 2: RESUMEN DETALLADO ---
    st.markdown("---")
    st.subheader("📋 Resumen por Tipo de Acción y Recursos")
    
    # Agrupación solicitada: Tipo de acción, Recursos por tipo y Suma Total
    resumen_detallado = df_filtered.groupby(col_tipo).agg({
        col_recurso: 'sum'
    }).reset_index()
    
    resumen_detallado.columns = ['Tipo de Acción', 'Recursos por Tipo']
    resumen_detallado['Suma Total Recursos'] = total_recursos_mentor
    
    # Mostrar tabla con formato
    st.table(resumen_detallado.style.format({
        'Recursos por Tipo': 'S/ {:,.2f}', 
        'Suma Total Recursos': 'S/ {:,.2f}'
    }))

    # Espacio para gráficos adicionales
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df_filtered, names=col_tipo, title="Distribución de Acciones", hole=0.3)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(resumen_detallado, x='Tipo de Acción', y='Recursos por Tipo', 
                         title="Presupuesto por Acción", color='Tipo de Acción')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla de datos crudos
    with st.expander("Ver detalle completo de registros"):
        st.dataframe(df_filtered, use_container_width=True)

except Exception as e:
    st.error(f"Error al configurar el dashboard: {e}")
    if 'df' in locals():
        st.write("Columnas detectadas:", df.columns.tolist())
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"Error final: {e}")
    if 'df' in locals():
        st.write("Columnas actuales:", df.columns.tolist())

