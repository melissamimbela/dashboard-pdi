import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración básica
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

@st.cache_data
def load_data():
    # Leemos la pestaña específica
    df = pd.read_excel('datos.csv.xlsx', sheet_name='PDI_CONSOLIDADOS')
    
    # Si los títulos no están en la primera fila, buscamos 'LÍDER MENTOR'
    if not 'LÍDER MENTOR' in df.columns.astype(str).str.upper().values:
        for i in range(len(df)):
            if 'LÍDER MENTOR' in df.iloc[i].astype(str).str.upper().values:
                df.columns = df.iloc[i].astype(str).str.strip().str.upper()
                df = df.iloc[i+1:].reset_index(drop=True)
                break
    else:
        df.columns = df.columns.astype(str).str.strip().str.upper()

    # ELIMINAR COLUMNAS VACÍAS (Esto quita los 'NAN' que causan el error)
    df = df.loc[:, ~df.columns.str.contains('^NAMED|^NAN|UNNAMED', case=False, na=False)]
    df = df.dropna(how='all', axis=1) # Elimina columnas totalmente vacías
    df = df.dropna(how='all', axis=0) # Elimina filas totalmente vacías
    
    # Convertir todo a texto limpio
    df = df.astype(str).replace('nan', '')
    
    return df

try:
    df = load_data()

    # 2. Identificar columnas por palabra clave
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_tipo_accion = [c for c in df.columns if 'TIPO DE ACCIÓN' in c or 'TIPO DE ACCION' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- Filtros ---
    st.sidebar.header("Filtros")
    mentores = sorted([m for m in df[col_mentor].unique() if m.strip() != ''])
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", mentores)

    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- Visualización ---
    st.subheader(f"Análisis para: {mentor_sel}")
    
    c1, c2 = st.columns(2)
    with c1:
        # Gráfico Circular (Tipo de Acción)
        # Usamos .value_counts() para evitar problemas de nombres de columnas
        datos_pie = df_filtro[col_tipo_accion].value_counts().reset_index()
        datos_pie.columns = ['Tipo', 'Cantidad']
        fig_pie = px.pie(datos_pie, values='Cantidad', names='Tipo', title='Modelo 70-20-10')
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Gráfico de Barras (Criticidad)
        resumen_crit = df_filtro[col_crit].value_counts().reset_index()
        resumen_crit.columns = ['Nivel', 'Cantidad']
        fig_bar = px.bar(resumen_crit, x='Nivel', y='Cantidad', title='Criticidad', color='Nivel')
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla de datos
    st.write("### Detalle de Registros")
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"Error final: {e}")
    if 'df' in locals():
        st.write("Columnas actuales:", df.columns.tolist())
