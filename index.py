import streamlit as st

st.set_page_config(page_title="Dashboard Principal", layout="wide")

st.title("Bem-vindo ao Sistema")
st.write("Escolha uma das opções abaixo para navegar:")

# Criando botões para navegação
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.page_link("pages/agricola.py", label="Agrícola", icon="🌱")

with col2:
    st.page_link("pages/meteorogg.py", label="Meteorologg", icon="☁️")

with col3:
    st.page_link("pages/rebanhos.py", label="Rebanhos", icon="🐄")

with col4:
    st.page_link("pages/analise_preditiva.py", label="Análise Preditiva", icon="📊")

with col5:
    st.page_link("pages/carbono.py", label="Carbono", icon="🟩")

