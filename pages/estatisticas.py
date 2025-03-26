import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Importar função de carregamento de dados do arquivo rebanhos.py
from pages.rebanhos import carregar_dados_rebanho

# Importar funções do meteorogg.py
from pages.meteorogg import process_meteo_data, get_city_info
from pathlib import Path

# Carregar dados meteorológicos usando as funções existentes
data_dir = Path('data/dados_meteorologicos')
csv_files = [f for f in data_dir.glob('*.csv')]

# Criar dicionário com informações das cidades e seus dados
city_data = {}
for f in csv_files:
    info = get_city_info(f)
    if info['nome']:
        city_data[info['nome']] = process_meteo_data(f)

# Calcular médias anuais dos dados meteorológicos (usando a primeira cidade como exemplo)
first_city = list(city_data.keys())[0]
df_meteo_annual = city_data[first_city].groupby(city_data[first_city]['Data'].dt.year).agg({
    'TemperaturaMedia': 'mean',
    'PrecipitacaoTotal': 'sum',
    'PressaoAtmosferica': 'mean'
}).reset_index()
df_meteo_annual.columns = ['Ano', 'temperature', 'precipitation', 'pressure']

# Carregar dados de rebanho usando a função importada
df_rebanho_ms = carregar_dados_rebanho()
if df_rebanho_ms is None:
    st.error('Erro ao carregar dados dos rebanhos')
    st.stop()

# Interface do usuário
st.title('Análise Estatística Cruzada')

# Seleção de dados
st.sidebar.header('Selecione os Dados para Análise')

# Primeira variável
data_type_1 = st.sidebar.selectbox(
    'Selecione o primeiro tipo de dado:',
    ['Dados de Rebanho', 'Dados Meteorológicos']
)

if data_type_1 == 'Dados de Rebanho':
    var_1 = st.sidebar.selectbox('Selecione o tipo de rebanho:', df_rebanho_ms['tipo_rebanho'].unique())
    data_1 = df_rebanho_ms[df_rebanho_ms['tipo_rebanho'] == var_1].groupby('ano')['quantidade'].sum().reset_index()
    data_1.columns = ['Ano', var_1]
else:
    var_1 = st.sidebar.selectbox('Selecione a variável meteorológica:', 
                                ['temperature', 'precipitation', 'humidity'])
    data_1 = df_meteo_annual[['Ano', var_1]]

# Segunda variável
data_type_2 = st.sidebar.selectbox(
    'Selecione o segundo tipo de dado:',
    ['Dados de Rebanho', 'Dados Meteorológicos']
)

if data_type_2 == 'Dados de Rebanho':
    var_2 = st.sidebar.selectbox('Selecione o tipo de rebanho:', df_rebanho_ms['tipo_rebanho'].unique(), key='var2')
    data_2 = df_rebanho_ms[df_rebanho_ms['tipo_rebanho'] == var_2].groupby('ano')['quantidade'].sum().reset_index()
    data_2.columns = ['Ano', var_2]
else:
    var_2 = st.sidebar.selectbox('Selecione a variável meteorológica:', 
                                ['temperature', 'precipitation', 'humidity'], key='var2')
    data_2 = df_meteo_annual[['Ano', var_2]]

# Mesclar os dados
df_merged = pd.merge(data_1, data_2, on='Ano', how='inner')

# Exibir gráficos
st.subheader('Análise de Correlação')

# Gráfico de dispersão
fig_scatter = px.scatter(
    df_merged,
    x=var_1,
    y=var_2,
    trendline='ols',
    title=f'Correlação entre {var_1} e {var_2}'
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Série temporal
st.subheader('Série Temporal')

fig_time = go.Figure()

# Normalizar os dados para melhor visualização
df_merged_norm = df_merged.copy()
df_merged_norm[var_1] = (df_merged_norm[var_1] - df_merged_norm[var_1].mean()) / df_merged_norm[var_1].std()
df_merged_norm[var_2] = (df_merged_norm[var_2] - df_merged_norm[var_2].mean()) / df_merged_norm[var_2].std()

fig_time.add_trace(go.Scatter(
    x=df_merged_norm['Ano'],
    y=df_merged_norm[var_1],
    name=var_1,
    mode='lines+markers'
))

fig_time.add_trace(go.Scatter(
    x=df_merged_norm['Ano'],
    y=df_merged_norm[var_2],
    name=var_2,
    mode='lines+markers'
))

fig_time.update_layout(
    title='Evolução Temporal (Dados Normalizados)',
    xaxis_title='Ano',
    yaxis_title='Valor Normalizado'
)

st.plotly_chart(fig_time, use_container_width=True)

# Estatísticas descritivas
st.subheader('Estatísticas Descritivas')
col1, col2 = st.columns(2)

with col1:
    st.write(f'Estatísticas de {var_1}')
    st.write(df_merged[var_1].describe())

with col2:
    st.write(f'Estatísticas de {var_2}')
    st.write(df_merged[var_2].describe())

# Calcular correlação
corr = df_merged[var_1].corr(df_merged[var_2])
st.write(f'Correlação entre {var_1} e {var_2}: {corr:.2f}')
