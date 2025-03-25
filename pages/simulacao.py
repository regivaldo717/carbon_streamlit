import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium import plugins
from scipy import stats
import glob

def criar_mapa_base():
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
    
    return m

def criar_mapa_calor(m, precipitacao_media):
    # Coordenadas aproximadas dos pontos de medição no MS
    coordenadas = [
        [-20.4435, -54.6478],  # Campo Grande
        [-22.2211, -54.8056],  # Dourados
        [-20.7849, -51.7019],  # Três Lagoas
        [-19.0077, -57.6511],  # Corumbá
        [-22.5296, -55.7203],  # Ponta Porã
        [-20.4666, -55.7868]   # Aquidauana
    ]

    # Criar dados para o mapa de calor
    heat_data = []
    for i, coord in enumerate(coordenadas):
        # Usar precipitação média como peso para o mapa de calor
        heat_data.append([coord[0], coord[1], float(precipitacao_media[i % len(precipitacao_media)])])

    # Adicionar mapa de calor
    plugins.HeatMap(heat_data).add_to(m)
    return m

def carregar_dados_combinados(ano_selecionado):
    # Carregar dados meteorológicos
    try:
        # Lista todos os arquivos de dados meteorológicos
        arquivos = glob.glob('data/dados_meteorologicos/dados_A*_M_*.csv')
        
        # Criar lista para armazenar os dataframes
        dfs = []
        
        for arquivo in arquivos:
            # Carregar dados do arquivo
            df = pd.read_csv(arquivo, sep=';')
            
            # Converter data para datetime
            df['Data'] = pd.to_datetime(df['Data'])
            
            # Filtrar apenas dados do ano selecionado
            df = df[df['Data'].dt.year == int(ano_selecionado)]
            
            if not df.empty:
                dfs.append(df)
        
        if not dfs:
            st.error(f'Não foram encontrados dados meteorológicos para o ano {ano_selecionado}.')
            return None, None, None
            
        # Combinar todos os dataframes
        df_meteo = pd.concat(dfs, ignore_index=True)
        
        # Calcular médias anuais por cidade
        df_meteo_anual = df_meteo.groupby('Cidade').agg({
            'Temperatura_C': 'mean',
            'Precipitacao_mm': 'sum',
            'Umidade_Perc': 'mean'
        }).reset_index()
        
        # Carregar dados dos rebanhos
        df_rebanho = pd.read_csv('data/dados_rebanho/br_ibge_ppm_efetivo_rebanhos.csv', sep=';')
        df_municipios = pd.read_csv('data/dados_rebanho/br_bd_diretorios_brasil_municipio.csv')
        
        # Filtrar apenas dados do MS e do ano selecionado
        df_rebanho = df_rebanho[
            (df_rebanho['sigla_uf'] == 'MS') & 
            (df_rebanho['ano'] == int(ano_selecionado))
        ]
        
        # Mesclar com dados dos municípios
        df_rebanho = pd.merge(
            df_rebanho, 
            df_municipios[['id_municipio', 'nome']], 
            on='id_municipio', 
            how='left'
        )
        
        # Carregar dados agrícolas
        df_agricola = pd.read_excel('data/dados_agricolas/producao_qtde_produzida.xlsx')
        
        # Filtrar para o ano selecionado
        df_agricola = df_agricola[df_agricola['Ano'] == int(ano_selecionado)]
        
        return df_meteo_anual, df_rebanho, df_agricola
        
    except Exception as e:
        st.error(f'Erro ao carregar dados: {str(e)}')
        return None, None, None

def plot_correlacao_variaveis(df_meteo, df_rebanho, df_agricola):
    # Preparar dados para correlação
    dados_correlacao = pd.DataFrame()
    
    # Adicionar dados meteorológicos
    dados_correlacao['Temperatura'] = df_meteo['Temperatura_C']
    dados_correlacao['Precipitação'] = df_meteo['Precipitacao_mm']
    dados_correlacao['Umidade'] = df_meteo['Umidade_Perc']
    
    # Adicionar dados de rebanho (agregados por município)
    rebanho_total = df_rebanho.groupby('nome')['quantidade'].sum().reset_index()
    dados_correlacao['Rebanho Total'] = rebanho_total['quantidade']
    
    # Adicionar dados agrícolas
    dados_correlacao['Produção Agrícola'] = df_agricola['Quantidade']
    
    # Calcular matriz de correlação
    corr_matrix = dados_correlacao.corr()
    
    # Criar heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmin=-1,
        zmax=1
    ))
    
    fig.update_layout(
        title='Matriz de Correlação entre Variáveis',
        template='plotly_white'
    )
    
    return fig

def plot_analise_regional(df_meteo, df_rebanho, df_agricola):
    # Criar gráfico de dispersão 3D
    fig = go.Figure(data=go.Scatter3d(
        x=df_meteo['Temperatura_C'],
        y=df_meteo['Precipitacao_mm'],
        z=df_agricola['Quantidade'],
        mode='markers',
        marker=dict(
            size=10,
            color=df_rebanho.groupby('nome')['quantidade'].sum(),
            colorscale='Viridis',
            showscale=True
        ),
        text=df_meteo['Cidade']
    ))
    
    fig.update_layout(
        title='Análise Regional: Temperatura x Precipitação x Produção Agrícola',
        scene=dict(
            xaxis_title='Temperatura (°C)',
            yaxis_title='Precipitação (mm)',
            zaxis_title='Produção Agrícola'
        ),
        template='plotly_white'
    )
    
    return fig

def mostrar_simulacao_agricola(precipitacao_media):
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title('Análise Multivariada - MS')
    with col2:
        if st.button('Voltar', use_container_width=True):
            st.switch_page('index.py')
            
    # Seletor de ano
    anos_disponiveis = ['2020', '2021', '2022', '2023']
    ano_selecionado = st.selectbox('Selecione o ano para análise', anos_disponiveis)
    
    # Carregar dados combinados
    df_meteo, df_rebanho, df_agricola = carregar_dados_combinados(ano_selecionado)
    
    if df_meteo is not None and df_rebanho is not None and df_agricola is not None:
        # Criar abas para diferentes análises
        tab1, tab2, tab3 = st.tabs(['Correlações', 'Análise Regional', 'Simulação de Produção'])
        
        # Aba de Correlações
        with tab1:
            st.plotly_chart(plot_correlacao_variaveis(df_meteo, df_rebanho, df_agricola), use_container_width=True)
            
            # Análise estatística
            st.subheader('Análise Estatística')
            col1, col2 = st.columns(2)
            
            with col1:
                # Correlação entre temperatura e produção
                corr_temp_prod = stats.pearsonr(df_meteo['Temperatura_C'], df_agricola['Quantidade'])
                st.metric('Correlação Temperatura-Produção', f'{corr_temp_prod[0]:.3f}')
                
            with col2:
                # Correlação entre precipitação e produção
                corr_prec_prod = stats.pearsonr(df_meteo['Precipitacao_mm'], df_agricola['Quantidade'])
                st.metric('Correlação Precipitação-Produção', f'{corr_prec_prod[0]:.3f}')
        
        # Aba de Análise Regional
        with tab2:
            st.plotly_chart(plot_analise_regional(df_meteo, df_rebanho, df_agricola), use_container_width=True)
            
            # Estatísticas regionais
            st.subheader('Estatísticas por Região')
            df_regional = pd.DataFrame({
                'Cidade': df_meteo['Cidade'],
                'Temperatura Média': df_meteo['Temperatura_C'],
                'Precipitação Total': df_meteo['Precipitacao_mm'],
                'Rebanho Total': df_rebanho.groupby('nome')['quantidade'].sum(),
                'Produção Agrícola': df_agricola['Quantidade']
            })
            st.dataframe(df_regional, use_container_width=True)
        
        # Aba de Simulação de Produção
        with tab3:
            # Parâmetros da simulação
            st.subheader('Parâmetros da Simulação')
            col1, col2 = st.columns(2)

            with col1:
                area_plantada = st.number_input('Área Plantada (hectares)', min_value=1, value=100)
                tipo_cultura = st.selectbox('Tipo de Cultura', ['Soja', 'Milho', 'Algodão', 'Cana-de-açúcar'])

            with col2:
                irrigacao = st.slider('Nível de Irrigação (%)', 0, 100, 50)
                tecnologia = st.slider('Nível de Tecnologia (%)', 0, 100, 50)

            # Simulação de produtividade
            if st.button('Simular Produtividade'):
                # Fatores de produtividade base (toneladas por hectare)
                produtividade_base = {
                    'Soja': 3.5,
                    'Milho': 6.0,
                    'Algodão': 4.0,
                    'Cana-de-açúcar': 75.0
                }

                # Cálculo da produtividade estimada
                produtividade = produtividade_base[tipo_cultura]
                
                # Ajuste pela irrigação (até 20% de aumento)
                fator_irrigacao = 1 + (irrigacao / 100) * 0.2
                
                # Ajuste pela tecnologia (até 30% de aumento)
                fator_tecnologia = 1 + (tecnologia / 100) * 0.3
                
                # Ajuste pela precipitação (usando média de precipitação)
                precipitacao_media_valor = np.mean(precipitacao_media)
                fator_precipitacao = 1 + (precipitacao_media_valor / 100) * 0.1

                # Produtividade final estimada
                producao_estimada = area_plantada * produtividade * fator_irrigacao * fator_tecnologia * fator_precipitacao

                # Exibir resultados
                st.subheader('Resultados da Simulação')
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric('Produtividade Base', f'{produtividade:.2f} t/ha')
                    st.metric('Fator Irrigação', f'{fator_irrigacao:.2f}x')

                with col2:
                    st.metric('Fator Tecnologia', f'{fator_tecnologia:.2f}x')
                    st.metric('Fator Precipitação', f'{fator_precipitacao:.2f}x')

                with col3:
                    st.metric('Produção Total Estimada', f'{producao_estimada:.2f} t')

                # Gráfico de contribuição dos fatores
                fatores = ['Base', 'Irrigação', 'Tecnologia', 'Precipitação']
                contribuicoes = [
                    produtividade,
                    produtividade * (fator_irrigacao - 1),
                    produtividade * (fator_tecnologia - 1),
                    produtividade * (fator_precipitacao - 1)
                ]

                fig = go.Figure(data=[go.Bar(
                    x=fatores,
                    y=contribuicoes,
                    text=[f'{c:.2f}' for c in contribuicoes],
                    textposition='auto',
                )])

                fig.update_layout(
                    title='Contribuição dos Fatores na Produtividade',
                    yaxis_title='Produtividade (t/ha)',
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)

    # Criar mapa base
    m = criar_mapa_base()

    # Botões para controle do mapa
    col1, col2 = st.columns(2)

    # Botão para mapa de calor
    if col1.button("Ver Mapa de Calor de Precipitação"):
        m = criar_mapa_calor(m, precipitacao_media)

    # Botão para resetar mapa
    if col2.button("Resetar Mapa"):
        m = criar_mapa_base()

    # Exibir mapa
    folium_static(m)

    # Parâmetros da simulação
    st.subheader("Parâmetros da Simulação")
    col1, col2 = st.columns(2)

    with col1:
        area_plantada = st.number_input("Área Plantada (hectares)", min_value=1, value=100)
        tipo_cultura = st.selectbox("Tipo de Cultura", ["Soja", "Milho", "Algodão", "Cana-de-açúcar"])

    with col2:
        irrigacao = st.slider("Nível de Irrigação (%)", 0, 100, 50)
        tecnologia = st.slider("Nível de Tecnologia (%)", 0, 100, 50)

    # Simulação simples de produtividade
    if st.button("Simular Produtividade"):
        # Fatores de produtividade base (toneladas por hectare)
        produtividade_base = {
            "Soja": 3.5,
            "Milho": 6.0,
            "Algodão": 4.0,
            "Cana-de-açúcar": 75.0
        }

        # Cálculo da produtividade estimada
        produtividade = produtividade_base[tipo_cultura]
        
        # Ajuste pela irrigação (até 20% de aumento)
        fator_irrigacao = 1 + (irrigacao / 100) * 0.2
        
        # Ajuste pela tecnologia (até 30% de aumento)
        fator_tecnologia = 1 + (tecnologia / 100) * 0.3
        
        # Ajuste pela precipitação (usando média de precipitação)
        precipitacao_media_valor = np.mean(precipitacao_media)
        fator_precipitacao = 1 + (precipitacao_media_valor / 100) * 0.1

        # Produtividade final estimada
        producao_estimada = area_plantada * produtividade * fator_irrigacao * fator_tecnologia * fator_precipitacao

        # Exibir resultados
        st.subheader("Resultados da Simulação")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Produtividade Base", f"{produtividade:.2f} t/ha")
            st.metric("Fator Irrigação", f"{fator_irrigacao:.2f}x")

        with col2:
            st.metric("Fator Tecnologia", f"{fator_tecnologia:.2f}x")
            st.metric("Fator Precipitação", f"{fator_precipitacao:.2f}x")

        with col3:
            st.metric("Produção Total Estimada", f"{producao_estimada:.2f} t")

        # Gráfico de contribuição dos fatores
        fatores = ['Base', 'Irrigação', 'Tecnologia', 'Precipitação']
        contribuicoes = [
            produtividade,
            produtividade * (fator_irrigacao - 1),
            produtividade * (fator_tecnologia - 1),
            produtividade * (fator_precipitacao - 1)
        ]

        fig = go.Figure(data=[go.Bar(
            x=fatores,
            y=contribuicoes,
            text=[f"{c:.2f}" for c in contribuicoes],
            textposition='auto',
        )])

        fig.update_layout(
            title='Contribuição dos Fatores na Produtividade',
            yaxis_title='Produtividade (t/ha)',
            template='plotly_white'
        )

        st.plotly_chart(fig, use_container_width=True)