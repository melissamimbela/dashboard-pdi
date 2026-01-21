import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard PDI", layout="wide")
st.title("📊 Dashboard Interactivo PDI")

@st.cache_data
def load_data():
    # Buscamos el archivo en la misma carpeta
    df = pd.read_csv('data.csv')
    df['LÍDER MENTOR'] = df['LÍDER MENTOR'].str.replace('\n', ' ', regex=True)
    return df

df = load_data()

# Filtro simple
mentor = st.sidebar.selectbox("Selecciona Mentor", df["LÍDER MENTOR"].unique())
df_filtro = df[df["LÍDER MENTOR"] == mentor]

# Gráficos
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(px.pie(df_filtro, names='TIPO DE ACCIÓN', title='Modelo 70-20-10'), use_container_width=True)
with col2:
    st.plotly_chart(px.bar(df_filtro['CRITICIDAD'].value_counts().reset_index(), x='index', y='CRITICIDAD', title='Criticidad'), use_container_width=True)


st.dataframe(df_filtro)
