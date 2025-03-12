import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Simulação de Crescimento Forrageiro",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("# Simulação do Crescimento da Vegetação Forrageira")

# Sidebar para parâmetros
st.sidebar.header("Parâmetros de Simulação")
TAL = st.sidebar.slider("Taxa de Assimilação Líquida (TAL)", 0.1, 1.0, 0.5, 0.1)
IAF = st.sidebar.slider("Índice de Área Foliar (IAF)", 0.1, 2.0, 0.8, 0.1)
AFE = st.sidebar.slider("Área Foliar Específica (AFE)", 0.1, 1.0, 0.2, 0.1)
RPF = st.sidebar.slider("Razão de Peso Foliar (RPF)", 0.1, 1.0, 0.6, 0.1)
biomassa_inicial = st.sidebar.number_input("Biomassa Inicial (g/m²)", 0.1, 10.0, 1.0, 0.1)
tempo_dias = st.sidebar.number_input("Tempo de análise (dias)", 1, 1000, 100, 1)

# Cálculo de índices
RAF = AFE * RPF
TCR = TAL * RAF
TCC = TAL * IAF

# Simulação do crescimento da biomassa
tempo = np.arange(0, tempo_dias + 1)
biomassa = np.zeros(len(tempo))
biomassa[0] = biomassa_inicial
for i in range(1, len(tempo)):
    biomassa[i] = biomassa[i-1] * (1 + TCR)  # Ajuste no cálculo para evitar crescimento excessivo

df = pd.DataFrame({
    'Dia': tempo,
    'Biomassa (g/m²)': biomassa,
    'Data': [datetime.now() + timedelta(days=int(t)) for t in tempo]
})

# Gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(x=tempo, y=biomassa, mode='lines', name='Biomassa', line=dict(color='#2e7d32', width=3)))
fig.update_layout(title="Crescimento da Planta Forrageira", xaxis_title="Tempo (dias)", yaxis_title="Biomassa (g/m²)")
st.plotly_chart(fig, use_container_width=True)

# Exibição das métricas
st.metric("Taxa de Crescimento da Cultura (TCC)", f"{TCC:.3f} g/m²/dia")
st.metric("Taxa de Crescimento Relativo (TCR)", f"{TCR:.3f} g/g/dia")
st.metric("Razão de Área Foliar (RAF)", f"{RAF:.3f} m²/g")

# Opção de download
download_csv = df.to_csv(index=False).encode('utf-8')
st.download_button("Baixar dados CSV", data=download_csv, file_name="crescimento_forrageira.csv", mime="text/csv")
