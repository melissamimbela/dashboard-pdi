import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard PDI Chinalco", layout="wide")

# Título con logo o emoji
st.title("📊 Dashboard Interactivo PDI")

# 2. Función para cargar datos con detección automática de columnas
@st.cache_data
def load_data():
    # Cargamos el Excel que detectamos en tu servidor
    df = pd.read_excel('datos.csv.xlsx')
    
    # Limpiamos nombres de columnas: quitamos espacios y pasamos a MAYÚSCULAS
    # Esto evita errores por "Líder Mentor" vs "LIDER MENTOR"
    df.columns = df.columns.str.strip().str.upper()
    
    # Limpiamos los datos de las columnas de texto
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
        
    return df

# 3. Ejecución principal
try:
    df = load_data()

    # Identificar columnas automáticamente aunque cambien ligeramente de nombre
    # Buscamos columnas que contengan palabras clave
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- BARRA LATERAL ---
    st.sidebar.header("Panel de Filtros")
    lista_mentores = sorted(df[col_mentor].unique())
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", lista_mentores)

    # Filtrar datos
    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- VISUALIZACIÓN ---
    st.subheader(f"Análisis para: {mentor_sel}")
    
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico Modelo 70-20-10
        fig_pie = px.pie(
            df_filtro, 
            names=col_accion, 
            title='Distribución Modelo 70-20-10',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        # Gráfico de Criticidad
        resumen_crit = df_filtro[col_crit].value_counts().reset_index()
        resumen_crit.columns = ['Nivel', 'Cantidad']
        
        fig_bar = px.bar(
            resumen_crit, 
            x='Nivel', 
            y='Cantidad', 
            title='Acciones por Criticidad',
            color='Nivel',
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Tabla de datos al final
    st.markdown("---")
    st.write("### Detalle de Registros")
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"Se encontró un detalle técnico: {e}")
    st.info("Revisando la estructura de tu archivo Excel...")
    if 'df' in locals():
        st.write("Columnas encontradas en tu archivo:", df.columns.tolist())
    else:
        st.write("No se pudo cargar el DataFrame. Verifica el nombre del archivo en GitHub.")

