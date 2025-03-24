#pip install -r requirements.txt
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import folium
from streamlit_folium import folium_static

# Configuração da página
st.set_page_config(
    page_title="Simulação de Crescimento Agrícola",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("# Simulação do Crescimento Agrícola no MT")

# Criação do mapa do Mato Grosso
m = folium.Map(location=[-12.6819, -56.9211], zoom_start=6)

# Adicionar marcadores para principais regiões agrícolas
regioes_mt = {
    "Sinop": [-11.8607, -55.5094],
    "Sorriso": [-12.5425, -55.7211],
    "Lucas do Rio Verde": [-13.0588, -55.9042],
    "Nova Mutum": [-13.8374, -56.0743],
    "Campo Novo do Parecis": [-13.6589, -57.8903],
    "Primavera do Leste": [-15.5551, -54.2993],
    "Rondonópolis": [-16.4673, -54.6372]
}

for cidade, coords in regioes_mt.items():
    folium.Marker(
        coords,
        popup=cidade,
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

# Exibir o mapa
st.write("### Principais Regiões Agrícolas do Mato Grosso")
folium_static(m)

# Opções de culturas agrícolas no MS
culturas = {
    "Soja": {"TAL": 0.7, "IAF": 1.5, "AFE": 0.3, "RPF": 0.5, "Biomassa": 1.5, "Fator_Sequestro": 0.4, "Ciclo": (90, 120)},
    "Milho": {"TAL": 0.8, "IAF": 1.8, "AFE": 0.4, "RPF": 0.6, "Biomassa": 1.8, "Fator_Sequestro": 0.5, "Ciclo": (120, 180)},
    "Algodão": {"TAL": 0.6, "IAF": 1.2, "AFE": 0.3, "RPF": 0.4, "Biomassa": 1.2, "Fator_Sequestro": 0.35, "Ciclo": (140, 220)},
    "Cana-de-açúcar": {"TAL": 0.9, "IAF": 2.0, "AFE": 0.5, "RPF": 0.7, "Biomassa": 2.0, "Fator_Sequestro": 0.6, "Ciclo": (365, 365)},
    "Pastagem": {"TAL": 0.5, "IAF": 0.8, "AFE": 0.2, "RPF": 0.6, "Biomassa": 0.8, "Fator_Sequestro": 0.3, "Ciclo": (180, 180)},
    "Manual": None
}

# Sidebar para seleção da cultura agrícola
st.sidebar.header("Seleção da Cultura Agrícola")
cultura_selecionada = st.sidebar.selectbox("Escolha a cultura agrícola", list(culturas.keys()))

if cultura_selecionada == "Manual":
    st.sidebar.header("Parâmetros de Simulação")
    TAL = st.sidebar.slider("Taxa de Assimilação Líquida (TAL)", 0.1, 1.0, 0.5, 0.1)
    IAF = st.sidebar.slider("Índice de Área Foliar (IAF)", 0.1, 2.0, 1.0, 0.1)
    AFE = st.sidebar.slider("Área Foliar Específica (AFE)", 0.1, 1.0, 0.3, 0.1)
    RPF = st.sidebar.slider("Razão de Peso Foliar (RPF)", 0.1, 1.0, 0.5, 0.1)
    biomassa_inicial = st.sidebar.number_input("Biomassa Inicial (g/m²)", 0.1, 10.0, 1.0, 0.1)
    ciclo_colheita = st.sidebar.number_input("Ciclo de Colheita (dias)", 30, 365, 120, 1)
else:
    parametros = culturas[cultura_selecionada]
    TAL = parametros["TAL"]
    IAF = parametros["IAF"]
    AFE = parametros["AFE"]
    RPF = parametros["RPF"]
    biomassa_inicial = parametros["Biomassa"]
    ciclo_colheita = st.sidebar.slider("Escolha o ciclo de colheita (dias)", parametros["Ciclo"][0], parametros["Ciclo"][1], parametros["Ciclo"][0], 1)

# Tempo de análise
tempo_dias = st.sidebar.number_input("Tempo de análise (dias)", ciclo_colheita, 1000, 300, 1)

# Dados climáticos médios para MS
precipitacao_media = [200, 180, 160, 120, 80, 50, 30, 40, 90, 130, 170, 190] # mm/mês
meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

#plot dos dados climáticos Com escala de cores
fig_clima = go.Figure()
fig_clima.add_trace(go.Bar(x=meses, y=precipitacao_media, marker=dict(color=precipitacao_media, colorscale='viridis_r', showscale=True)))
fig_clima.update_layout(xaxis_title='Meses', yaxis_title='Precipitação (mm)')
st.plotly_chart(fig_clima, use_container_width=True)



# Cálculo de índices
RAF = AFE * RPF
TCR = TAL * RAF
TCC = TAL * IAF

# Ajuste do crescimento com base na precipitação
ajuste_precipitacao = np.interp(np.linspace(0, 11, tempo_dias + 1), range(12), precipitacao_media / np.max(precipitacao_media))

# Simulação do crescimento da biomassa
tempo = np.arange(0, tempo_dias + 1)
biomassa = np.zeros(len(tempo))
biomassa[0] = biomassa_inicial
sequestro_carbono = np.zeros(len(tempo))
periodo_reducao_carbono = 10  # Dias para reduzir o carbono após a colheita

for i in range(1, len(tempo)):
    fator_chuva = ajuste_precipitacao[i]
    biomassa[i] = biomassa[i-1] * (1 + TCR * fator_chuva)
    if i % ciclo_colheita == 0:
        biomassa[i] *= 0.7  # Redução proporcional da biomassa após colheita
        for j in range(periodo_reducao_carbono):
            if i + j < len(tempo):
                sequestro_carbono[i + j] = biomassa[i] * (parametros["Fator_Sequestro"] if cultura_selecionada != "Manual" else 0.4) * (1 - j / periodo_reducao_carbono)
    else:
        sequestro_carbono[i] = biomassa[i] * (parametros["Fator_Sequestro"] if cultura_selecionada != "Manual" else 0.4)

# Gráficos e saída
df = pd.DataFrame({"Dia": tempo, "Biomassa (g/m²)": biomassa, "Sequestro de Carbono (gC/m²)": sequestro_carbono})

fig = go.Figure()
fig.add_trace(go.Scatter(x=df["Dia"], y=df["Biomassa (g/m²)"], mode='lines', name='Biomassa', line=dict(color='#2e7d32', width=3)))
fig.update_layout(xaxis_title='Dias', yaxis_title='Biomassa (g/m²)')
st.plotly_chart(fig, use_container_width=True)

fig_carbono = go.Figure()
fig_carbono.add_trace(go.Scatter(x=df["Dia"], y=df["Sequestro de Carbono (gC/m²)"], mode='lines', name='Sequestro de Carbono', line=dict(color='#ff9800', width=3)))
fig_carbono.update_layout(xaxis_title='Dias', yaxis_title='Sequestro de Carbono (gC/m²)')
st.plotly_chart(fig_carbono, use_container_width=True)

# Opção de download
download_csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Baixar dados CSV", data=download_csv, file_name=f"crescimento_{cultura_selecionada.lower()}.csv", mime="text/csv")