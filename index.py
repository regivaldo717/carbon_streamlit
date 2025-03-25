import streamlit as st

st.set_page_config(page_title="Dashboard Principal", layout="wide")

st.title("Bem-vindo ao Sistema")
st.write("Escolha uma das opções abaixo para navegar:")

# Criando botões para navegação
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.page_link("pages/agricola.py", label="Agrícola", icon="🌱")

with col2:
    st.page_link("pages/meteorologicos.py", label="Meteorológg", icon="☁️")

with col3:
    st.page_link("pages/rebanhos.py", label="Rebanhos", icon="🐄")


