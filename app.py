import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

@st.cache_data
def load_data():
    file_path = 'datos.csv.xlsx'
    # Cargamos la hoja que me indicaste
    df = pd.read_excel(file_path, sheet_name='PDI_CONSOLIDADOS')
    
    # --- LIMPIEZA DE ESTRUCTURA ---
    # Si los nombres de las columnas son "Unnamed", buscamos la fila de encabezados real
    if df.columns.str.contains('Unnamed').any():
        # Buscamos la fila que contiene la palabra 'MENTOR'
        for i in range(len(df)):
            if df.iloc[i].astype(str).str.contains('MENTOR').any():
                df.columns = df.iloc[i].astype(str).str.strip().str.upper()
                df = df.iloc[i+1:].reset_index(drop=True)
                break
    else:
        df.columns = df.columns.astype(str).str.strip().str.upper()

    # Quitar filas totalmente vacías
    df = df.dropna(how='all').reset_index(drop=True)
    
    # Asegurar que las celdas de texto estén limpias
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
            
    return df

try:
    df = load_data()

    # 2. Identificación dinámica de columnas
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- Filtros ---
    st.sidebar.header("Filtros")
    # Quitamos valores nulos de la lista de mentores
    lista_mentores = sorted([m for m in df[col_mentor].unique() if m != 'nan' and m != 'None'])
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", lista_mentores)

    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- Visualización ---
    st.subheader(f"Análisis para: {mentor_sel}")
    
    c1, c2 = st.columns(2)
    with c1:
        # Gráfico Circular
        fig_pie = px.pie(df_filtro, names=col_accion, title='Modelo 70-20-10', hole=0.4)
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
    st.error(f"Error técnico: {e}")
    st.info("Revisando columnas detectadas...")
    if 'df' in locals():
        st.write("Columnas actuales:", df.columns.tolist())
        st.write("Vista previa de datos:", df.head(3))
