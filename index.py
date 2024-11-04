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

# Parâmetros fixos (ajustarei depois)
TAL = 0.5
IAF = 0.8
AFE = 0.2
RPF = 0.6

st.title("Simulação do Crescimento da Vegetação Forrageira")

tempo_dias = st.slider("Digite o tempo de análise em dias:", min_value=1, max_value=10000, value=100, step=1)

anos = tempo_dias // 365
meses = (tempo_dias % 365) // 30
semanas = ((tempo_dias % 365) % 30) // 7
dias_restantes = ((tempo_dias % 365) % 30) % 7

st.write("Valor de tempo inserido:", tempo_dias, "dias")
st.write(f"Isso equivale a: {anos} anos, {meses} meses, {semanas} semanas e {dias_restantes} dias.")

TCC = calcular_TCC(TAL, IAF)
RAF = calcular_RAF(AFE, RPF)
TCR = calcular_TCR(TAL, RAF)

tempo = np.arange(0, tempo_dias + 1)
biomassa = np.zeros(len(tempo))
biomassa[0] = 1  
for i in range(1, len(tempo)):
    biomassa[i] = biomassa[i-1] * np.exp(TCR)

fig = go.Figure()
fig.add_trace(go.Scatter(x=tempo, y=biomassa, mode='lines', name='Biomassa'))
fig.update_layout(title="Crescimento da Planta Forrageira",
                  xaxis_title="Tempo (dias)",
                  yaxis_title="Biomassa acumulada")

st.plotly_chart(fig)
