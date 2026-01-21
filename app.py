import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

@st.cache_data
def load_data():
    # Usamos el nombre exacto que veo en tu carpeta
    df = pd.read_csv('datos.csv')
    # Limpieza de nombres por si acaso
    if 'LÍDER MENTOR' in df.columns:
        df['LÍDER MENTOR'] = df['LÍDER MENTOR'].str.replace('\n', ' ', regex=True)
    return df

try:
    df = load_data()

    # Filtro
    mentor = st.sidebar.selectbox("Selecciona Mentor", df["LÍDER MENTOR"].unique())
    df_filtro = df[df["LÍDER MENTOR"] == mentor]

    # Gráficos
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(px.pie(df_filtro, names='TIPO DE ACCIÓN', title='Modelo 70-20-10'), use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(df_filtro['CRITICIDAD'].value_counts().reset_index(), x='index', y='CRITICIDAD', title='Criticidad'), use_container_width=True)

    st.dataframe(df_filtro)

except Exception as e:
    st.error(f"Error al cargar los datos: {e}")
    st.write("Asegúrate de que el archivo 'datos.csv' esté en la raíz de GitHub junto a este archivo app.py")
