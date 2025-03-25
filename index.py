#pip install -r requirements.txt
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium import plugins

# Configuração da página
st.set_page_config(
    page_title="Simulação de Crescimento Agrícola",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.markdown("# Simulação do Crescimento Agrícola no MS")

# Criação do mapa do Mato Grosso do Sul
m = folium.Map(location=[-20.4435, -54.6478], zoom_start=6)

# Adicionar marcadores para principais regiões agrícolas
regioes_ms = {
    "Campo Grande": [-20.4435, -54.6478],
    "Dourados": [-22.2211, -54.8056],
    "Três Lagoas": [-20.7849, -51.7019],
    "Corumbá": [-19.0077, -57.6511],
    "Ponta Porã": [-22.5296, -55.7203],
    "Aquidauana": [-20.4666, -55.7868]
}

for cidade, coords in regioes_ms.items():
    folium.Marker(
        coords,
        popup=cidade,
        icon=folium.Icon(color='green', icon='info-sign')
    ).add_to(m)

# Botões para controle do mapa
col1, col2 = st.columns(2)

# Botão para mapa de calor
if col1.button("Ver Mapa de Calor de Precipitação"):
    # Criar mapa de calor
    m_heat = folium.Map(location=[-20.4435, -54.6478], zoom_start=6)
    
    # Adicionar dados de precipitação como mapa de calor
    heat_data = []
    for cidade, coords in regioes_ms.items():
        # Usar precipitação média anual como peso
        peso = np.mean(precipitacao_media)
        heat_data.append([coords[0], coords[1], peso])
    
    # Adicionar mapa de calor
    folium.plugins.HeatMap(
        heat_data,
        min_opacity=0.4,
        max_val=200,
        radius=25,
        blur=15,
        gradient={'0.4': 'yellow', '0.6': 'orange', '0.8': 'red', '1': 'purple'}
    ).add_to(m_heat)
    
    # Exibir mapa de calor
    st.write("### Mapa de Calor - Intensidade de Precipitação")
    folium_static(m_heat)
else:
    # Exibir mapa padrão
    st.write("### Principais Regiões Agrícolas do Mato Grosso")
    folium_static(m)

# Botão para animação mensal
if col2.button("Ver Variação Mensal de Precipitação"):
    # Criar mapa para animação
    m_time = folium.Map(location=[-20.4435, -54.6478], zoom_start=6)
    
    # Criar dados para cada mês
    for mes, precipitacao in zip(meses, precipitacao_media):
        feature_group = folium.FeatureGroup(name=mes)
        
        for cidade, coords in regioes_ms.items():
            # Criar círculo com tamanho baseado na precipitação
            folium.CircleMarker(
                location=coords,
                radius=(precipitacao/10),  # Ajustar tamanho do círculo
                popup=f"{cidade}: {precipitacao}mm",
                color='purple',
                fill=True,
                fill_color='purple',
                fill_opacity=precipitacao/200  # Opacidade baseada na precipitação
            ).add_to(feature_group)
        
        feature_group.add_to(m_time)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(m_time)
    
    # Exibir mapa com animação
    st.write("### Variação Mensal de Precipitação")
    st.write("Selecione os meses na caixa de controle no canto superior direito do mapa")
    folium_static(m_time)

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

from datetime import datetime, timedelta

# Seletor de ano
anos_disponiveis = ['2020', '2021', '2022', '2023', '2024']
ano_selecionado = st.selectbox('Selecione o ano para análise', anos_disponiveis)

# Carregar dados meteorológicos do ano selecionado
df_meteo = pd.read_csv(f'precipitacao_MS/data/dados_meteorologicos_MS_{ano_selecionado}.csv')
df_meteo['Data'] = pd.to_datetime(df_meteo['Data'])

# Criar seção para análise individual de variáveis
st.markdown("## Análise Individual de Variáveis")

# Seletor de variável
variavel_selecionada = st.selectbox(
    'Selecione a variável para análise detalhada',
    ['Temperatura', 'Pressão', 'Umidade', 'Precipitação']
)

# Mapeamento de variáveis para colunas do DataFrame
var_map = {
    'Temperatura': {'col': 'Temperatura_C', 'unit': '°C', 'color': 'Reds'},
    'Pressão': {'col': 'Pressao_hPa', 'unit': 'hPa', 'color': 'Blues'},
    'Umidade': {'col': 'Umidade_Perc', 'unit': '%', 'color': 'Greens'},
    'Precipitação': {'col': 'Precipitacao_mm', 'unit': 'mm', 'color': 'Purples'}
}

# Obter informações da variável selecionada
var_info = var_map[variavel_selecionada]
var_col = var_info['col']
var_unit = var_info['unit']

# Criar abas para diferentes análises
tab1, tab2, tab3 = st.tabs(['Série Temporal', 'Estatísticas', 'Comparação por Cidade'])

# Função para criar gráfico de linha
def plot_variable(df, variable, title, y_label, color_scale):
    fig = go.Figure()
    for cidade in df['Cidade'].unique():
        cidade_data = df[df['Cidade'] == cidade]
        fig.add_trace(go.Scatter(
            x=cidade_data['Data'],
            y=cidade_data[variable],
            name=cidade,
            mode='lines',
            line=dict(width=2)
        ))
    fig.update_layout(
        title=title,
        xaxis_title='Data',
        yaxis_title=y_label,
        template='plotly_white',
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    return fig

# Aba de Série Temporal
with tab1:
    st.plotly_chart(plot_variable(
        df_meteo,
        var_col,
        f'{variavel_selecionada} por Cidade',
        f'{variavel_selecionada} ({var_unit})',
        var_info['color']
    ), use_container_width=True)

# Aba de Estatísticas
with tab2:
    # Calcular estatísticas por cidade
    stats = df_meteo.groupby('Cidade')[var_col].agg([
        ('Média', 'mean'),
        ('Mínima', 'min'),
        ('Máxima', 'max'),
        ('Desvio Padrão', 'std')
    ]).round(2)
    
    # Exibir estatísticas
    st.markdown(f"### Estatísticas de {variavel_selecionada}")
    st.dataframe(stats, use_container_width=True)
    
    # Criar gráfico de boxplot
    fig_box = go.Figure()
    for cidade in df_meteo['Cidade'].unique():
        fig_box.add_trace(go.Box(
            y=df_meteo[df_meteo['Cidade'] == cidade][var_col],
            name=cidade,
            boxpoints='outliers'
        ))
    fig_box.update_layout(
        title=f'Distribuição de {variavel_selecionada} por Cidade',
        yaxis_title=f'{variavel_selecionada} ({var_unit})',
        showlegend=False
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Aba de Comparação por Cidade
with tab3:
    # Seletor de cidades para comparação
    cidades_selecionadas = st.multiselect(
        'Selecione as cidades para comparar',
        df_meteo['Cidade'].unique(),
        default=list(df_meteo['Cidade'].unique())[:2]
    )
    
    if cidades_selecionadas:
        # Filtrar dados para as cidades selecionadas
        df_comparacao = df_meteo[df_meteo['Cidade'].isin(cidades_selecionadas)]
        
        # Criar gráfico de comparação
        fig_comp = go.Figure()
        for cidade in cidades_selecionadas:
            cidade_data = df_comparacao[df_comparacao['Cidade'] == cidade]
            fig_comp.add_trace(go.Scatter(
                x=cidade_data['Data'],
                y=cidade_data[var_col],
                name=cidade,
                mode='lines+markers'
            ))
        fig_comp.update_layout(
            title=f'Comparação de {variavel_selecionada} entre Cidades Selecionadas',
            xaxis_title='Data',
            yaxis_title=f'{variavel_selecionada} ({var_unit})',
            showlegend=True
        )
        st.plotly_chart(fig_comp, use_container_width=True)
        
        # Calcular correlação entre cidades
        if len(cidades_selecionadas) > 1:
            st.markdown("### Correlação entre Cidades")
            pivot_data = df_comparacao.pivot(index='Data', columns='Cidade', values=var_col)
            corr_matrix = pivot_data.corr().round(3)
            st.dataframe(corr_matrix, use_container_width=True)



# Cálculo da média mensal de precipitação para o ano selecionado
df_meteo['Mes'] = pd.to_datetime(df_meteo['Data']).dt.month
precipitacao_media = df_meteo.groupby('Mes')['Precipitacao_mm'].mean().values

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