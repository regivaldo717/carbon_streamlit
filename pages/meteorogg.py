import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import re
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="Análise Meteorológica", layout="wide")
st.title("Análise Meteorológica por Cidade")

# Função para extrair informações da cidade do arquivo
def get_city_info(file_path):
    info = {'nome': None, 'latitude': None, 'longitude': None}
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_lower = line.lower()
            if 'nome:' in line_lower:
                info['nome'] = line.split(':')[1].strip()
            elif 'latitude:' in line_lower:
                info['latitude'] = float(line.split(':')[1].strip())
            elif 'longitude:' in line_lower:
                info['longitude'] = float(line.split(':')[1].strip())
    return info

# Função para ler e processar os dados meteorológicos
def process_meteo_data(file_path):
    # Pular as primeiras 10 linhas e ler o restante como CSV
    df = pd.read_csv(file_path, skiprows=10, sep=';')
    
    # Mapear os nomes das colunas corretamente
    colunas_esperadas = {
        'Data Medicao': 'Data',
        'NUMERO DE DIAS COM PRECIP. PLUV, MENSAL (AUT)(número)': 'DiasPrecipitacao',
        'PRECIPITACAO TOTAL, MENSAL (AUT)(mm)': 'PrecipitacaoTotal',
        'PRESSAO ATMOSFERICA, MEDIA MENSAL (AUT)(mB)': 'PressaoAtmosferica',
        'TEMPERATURA MEDIA, MENSAL (AUT)(°C)': 'TemperaturaMedia',
        'VENTO, VELOCIDADE MAXIMA MENSAL (AUT)(m/s)': 'VentoVelocidadeMaxima',
        'VENTO, VELOCIDADE MEDIA MENSAL (AUT)(m/s)': 'VentoVelocidadeMedia'
    }
    
    # Renomear as colunas usando o mapeamento
    df = df.rename(columns=colunas_esperadas)
    
    # Converter a coluna de data
    df['Data'] = pd.to_datetime(df['Data'])
    df['Mes'] = df['Data'].dt.month
    
    # Converter valores nulos ('null') para NaN
    df = df.replace('null', pd.NA)
    
    # Converter colunas para tipo numérico
    colunas_numericas = df.columns.drop(['Data', 'Mes'])
    for col in colunas_numericas:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# Caminho para a pasta de dados meteorológicos
data_dir = Path('data/dados_meteorologicos')

# Listar todos os arquivos CSV
csv_files = [f for f in data_dir.glob('*.csv')]

# Criar dicionário com informações das cidades
city_info = {}
for f in csv_files:
    info = get_city_info(f)
    if info['nome']:
        city_info[info['nome']] = {
            'file': f,
            'latitude': info['latitude'],
            'longitude': info['longitude']
        }

city_names = sorted(list(city_info.keys()))

selected_cities = st.multiselect('Selecione as cidades para comparação:', city_names)

if selected_cities:
    # Processar dados das cidades selecionadas
    city_data = {}
    for city in selected_cities:
        city_data[city] = process_meteo_data(city_info[city]['file'])
    
    # Criar mapa com as cidades selecionadas usando Folium
    m = folium.Map(location=[-20, -55], zoom_start=6)
    
    # Adicionar marcadores para cada cidade selecionada
    for city in selected_cities:
        folium.Marker(
            location=[city_info[city]['latitude'], city_info[city]['longitude']],
            popup=f"<b>{city}</b>",
            tooltip=city
        ).add_to(m)
    
    # Ajustar o zoom para mostrar todas as cidades selecionadas
    if selected_cities:
        lats = [city_info[city]['latitude'] for city in selected_cities]
        lons = [city_info[city]['longitude'] for city in selected_cities]
        m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])
    
    # Exibir o mapa
    st.write('Localização das Cidades Selecionadas')
    folium_static(m)
    
    # Criar layout com 3 colunas
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Gráfico 1: Boxplot de temperatura por mês
        fig_temp = go.Figure()
        for city in selected_cities:
            df = city_data[city]
            fig_temp.add_trace(go.Box(
                x=df['Mes'],
                y=df['TemperaturaMedia'],
                name=city
            ))
        fig_temp.update_layout(
            title='Distribuição de Temperatura Média por Mês',
            xaxis_title='Mês',
            yaxis_title='Temperatura Média (°C)'
        )
        st.plotly_chart(fig_temp, use_container_width=True)
    
    with col2:
        # Gráfico 2: Linha temporal de velocidade média do vento
        fig_wind = go.Figure()
        for city in selected_cities:
            df = city_data[city]
            fig_wind.add_trace(go.Scatter(
                x=df['Data'],
                y=df['VentoVelocidadeMedia'],
                name=city,
                mode='lines'
            ))
        fig_wind.update_layout(
            title='Velocidade Média do Vento ao Longo do Tempo',
            xaxis_title='Data',
            yaxis_title='Velocidade Média do Vento (m/s)'
        )
        st.plotly_chart(fig_wind, use_container_width=True)
    
    with col3:
        # Gráfico 3: Dispersão entre vento e precipitação
        fig_scatter = go.Figure()
        for city in selected_cities:
            df = city_data[city]
            fig_scatter.add_trace(go.Scatter(
                x=df['VentoVelocidadeMedia'],
                y=df['PrecipitacaoTotal'],
                mode='markers',
                name=city
            ))
        fig_scatter.update_layout(
            title='Relação entre Vento e Precipitação',
            xaxis_title='Velocidade Média do Vento (m/s)',
            yaxis_title='Precipitação Total (mm)'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Mostrar estatísticas básicas para cada cidade
    for city in selected_cities:
        st.subheader(f'Estatísticas Básicas - {city}')
        df = city_data[city]
        stats = df[['TemperaturaMedia', 'PrecipitacaoTotal', 'PressaoAtmosferica', 
                    'VentoVelocidadeMaxima', 'VentoVelocidadeMedia']].describe()
        stats.columns = ['Temperatura Média (°C)', 'Precipitação Total (mm)', 
                        'Pressão Atmosférica (mB)', 'Velocidade Máxima do Vento (m/s)',
                        'Velocidade Média do Vento (m/s)']
        st.dataframe(stats)