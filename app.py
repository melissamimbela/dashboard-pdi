import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuración de la página
st.set_page_config(page_title="Dashboard PDI Chinalco", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

# 2. Función de carga de datos "Inteligente"
@st.cache_data
def load_data():
    file_path = 'datos.csv.xlsx'
    xl = pd.ExcelFile(file_path)
    
    # Buscamos la hoja correcta (la que tenga más datos)
    target_sheet = 'PDI_CONSOLIDADOS'
    if target_sheet in xl.sheet_names:
        df = pd.read_excel(file_path, sheet_name=target_sheet)
    else:
        # Si no la encuentra por nombre, intenta con la primera que tenga datos
        df = pd.read_excel(file_path, sheet_name=0)

    # Limpiamos nombres de columnas (quitar espacios y a MAYÚSCULAS)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    
    # Si la primera fila son "Unnamed", buscamos la primera fila con datos reales
    if "UNNAMED" in df.columns[0]:
        df.columns = df.iloc[0]
        df = df[1:]
        df.columns = df.columns.astype(str).str.strip().str.upper()

    # Quitar filas y columnas vacías
    df = df.dropna(how='all').reset_index(drop=True)
    
    # Limpiar textos de las celdas
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.replace('\n', ' ', regex=True).str.strip()
        
    return df

# 3. Lógica del Dashboard
try:
    df = load_data()

    # Buscamos columnas clave de forma flexible
    col_mentor = [c for c in df.columns if 'MENTOR' in c][0]
    col_accion = [c for c in df.columns if 'ACCION' in c or 'ACCIÓN' in c][0]
    col_crit = [c for c in df.columns if 'CRITICIDAD' in c][0]

    # --- Filtros ---
    st.sidebar.header("Configuración")
    mentores = sorted([m for m in df[col_mentor].unique() if str(m).lower() != 'nan'])
    mentor_sel = st.sidebar.selectbox("Selecciona un Líder Mentor", mentores)

    df_filtro = df[df[col_mentor] == mentor_sel]

    # --- Visualización ---
    st.subheader(f"Análisis de Gestión: {mentor_sel}")
    
    c1, c2 = st.columns(2)
    with c1:
        fig_pie = px.pie(df_filtro, names=col_accion, title='Modelo 70-20-10', hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        resumen = df_filtro[col_crit].value_counts().reset_index()
        resumen.columns = ['Nivel', 'Cantidad']
        fig_bar = px.bar(resumen, x='Nivel', y='Cantidad', title='Criticidad', color='Nivel')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("### Detalle de Registros")
    st.dataframe(df_filtro, use_container_width=True)

except Exception as e:
    st.error(f"Error de estructura: {e}")
    st.info("Revisando el contenido del archivo...")
    if 'df' in locals():
        st.write("Columnas detectadas:", df.columns.tolist())
        st.write("Vista previa de los datos:", df.head(5))
