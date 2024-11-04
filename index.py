import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Função para calcular a Taxa de Crescimento da Cultura (TCC)
def calcular_TCC(TAL, IAF):
    return TAL * IAF

# Função para calcular a Taxa de Crescimento Relativo (TCR)
def calcular_TCR(TAL, RAF):
    return TAL * RAF

# Função para calcular a Razão de Área Foliar (RAF)
def calcular_RAF(AFE, RPF):
    return AFE * RPF

# Parâmetros fixos
TAL = 0.5
IAF = 0.8
AFE = 0.2
RPF = 0.6

# Título do aplicativo
st.title("Simulação de Crescimento da Planta Forrageira")

# Slider para entrada do usuário com atualização em tempo real
duracao = st.slider("Digite o tempo de análise em dias:", min_value=1, max_value=10000, value=100, step=1)

# Cálculo dos parâmetros de crescimento
TCC = calcular_TCC(TAL, IAF)
RAF = calcular_RAF(AFE, RPF)
TCR = calcular_TCR(TAL, RAF)

# Cálculo da biomassa acumulada
tempo = np.arange(0, duracao + 1)
biomassa = np.zeros(len(tempo))
biomassa[0] = 1  # Biomassa inicial

for i in range(1, len(tempo)):
    biomassa[i] = biomassa[i-1] * np.exp(TCR)

# Criação do gráfico
fig = go.Figure()
fig.add_trace(go.Scatter(x=tempo, y=biomassa, mode='lines', name='Biomassa'))
fig.update_layout(title="Crescimento da Planta Forrageira",
                  xaxis_title="Tempo (dias)",
                  yaxis_title="Biomassa acumulada")

# Exibição do gráfico no Streamlit
st.plotly_chart(fig)
