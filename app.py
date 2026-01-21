import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración básica
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

@st.cache_data
def load_data():
    # Leemos el archivo saltando posibles filas vacías al inicio (usando header=None primero)
    raw_df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS', header=None)
    
    # Buscamos la fila donde realmente están los títulos
    # Buscamos la primera fila que contenga la palabra 'MENTOR'
    for i, row in raw_df.iterrows():
        if row.astype(str).str.contains('MENTOR', case=False).any():
            df = raw_df.iloc[i:].copy()
            df.columns = df.iloc[0].astype(str).str.strip().str.upper()
            df = df.iloc[1:].reset_index(drop=True)
            break
    else:
        # Si no la encuentra, asumimos la primera fila como títulos
        df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS')
        df.columns = df.columns.astype(str).str.strip().str.upper()

    # Eliminar columnas y filas completamente vacías
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    # Convertir todo a texto para evitar errores de tipo 'dtype'
    df = df.astype(str)
    
    return df

try:
    df = load_data()

    # 2. Identificar columnas (Búsqueda por palabra clave)
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- Filtros ---
    st.sidebar.header("Filtros")
    mentores = sorted([m for m in df[col_mentor].unique() if m not in ['nan', 'None']])
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", mentores)

    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- Visualización ---
    st.subheader(f"Análisis para: {mentor_sel}")
    
    c1, c2 = st.columns(2)
    with c1:
        # Gráfico Circular
        fig_pie = px.pie(df_filtro, names=col_accion, title='Modelo 70-20-10')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Gráfico de Barras
        resumen_crit = df_filtro[col_crit].value_counts().reset_index()
        resumen_crit.columns = ['Nivel', 'Cantidad']
        fig_bar = px.bar(resumen_crit, x='Nivel', y='Cantidad', title='Criticidad', color='Nivel')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla de datos
    st.write("### Detalle de Registros")
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar: {e}")
    st.info("Revisando estructura interna...")
    # Si falla, mostramos qué leyó para poder ayudarte mejor
    st.write("Columnas detectadas actualmente:", df.columns.tolist() if 'df' in locals() else "No cargadas")
