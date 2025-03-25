import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
import glob

def carregar_dados_meteorologicos(ano_selecionado):
    # Carregar dados meteorológicos do ano selecionado
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
            return None
            
        # Combinar todos os dataframes
        df_meteo = pd.concat(dfs, ignore_index=True)
        
        # Ordenar por data
        df_meteo = df_meteo.sort_values('Data')
        
        return df_meteo
    except Exception as e:
        st.error(f'Erro ao carregar dados meteorológicos: {str(e)}')
        return None

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

def mostrar_dados_meteorologicos():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title('Análise Meteorológica do MS')
    with col2:
        if st.button('Voltar', use_container_width=True):
            st.switch_page('index.py')
            
    # Seletor de ano
    # Seletor de ano
    anos_disponiveis = ['2020', '2021', '2022', '2023', '2024']
    ano_selecionado = st.selectbox('Selecione o ano para análise', anos_disponiveis)

    # Carregar dados meteorológicos do ano selecionado
    df_meteo = carregar_dados_meteorologicos(ano_selecionado)

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
    
    return precipitacao_media