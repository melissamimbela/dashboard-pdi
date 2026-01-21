import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

# 2. Función para cargar datos
@st.cache_data
def load_data():
    # Carga el archivo desde el repositorio
    df = pd.read_csv('datos.csv')
    # Limpia saltos de línea en la columna de mentores
    df['LÍDER MENTOR'] = df['LÍDER MENTOR'].str.replace('\n', ' ', regex=True)
    return df

# 3. Cargar el DataFrame
df = load_data()

# 4. Barra lateral con filtros
st.sidebar.header("Filtros")
mentor_list = sorted(df["LÍDER MENTOR"].unique())
mentor = st.sidebar.selectbox("Selecciona un Líder Mentor", mentor_list)

# Filtrar datos por el mentor seleccionado
df_filtro = df[df["LÍDER MENTOR"] == mentor]

# 5. Visualización de métricas y gráficos
col1, col2 = st.columns(2)

with col1:
    fig_pie = px.pie(
        df_filtro, 
        names='TIPO DE ACCIÓN', 
        title=f'Modelo 70-20-10: {mentor}',
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Contar criticidad
    counts = df_filtro['CRITICIDAD'].value_counts().reset_index()
    counts.columns = ['Nivel', 'Cantidad']
    
    fig_bar = px.bar(
        counts, 
        x='Nivel', 
        y='Cantidad', 
        title='Distribución por Criticidad',
        color='Nivel'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 6. Mostrar tabla de datos detallada
st.subheader(f"Detalle de acciones para: {mentor}")
st.dataframe(df_filtro, use_container_width=True)
