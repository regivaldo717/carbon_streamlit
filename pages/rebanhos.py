import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def mostrar_dados_rebanhos():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title('Análise dos Rebanhos no Mato Grosso do Sul')
    with col2:
        if st.button('Voltar', use_container_width=True):
            st.switch_page('index.py')

    # Carregar dados dos rebanhos
    def carregar_dados_rebanho():
        try:
            # Carregar dados do IBGE
            df_rebanho = pd.read_csv('data/dados_rebanho/br_ibge_ppm_efetivo_rebanhos.csv', sep=';')
            df_municipios = pd.read_csv('data/dados_rebanho/br_bd_diretorios_brasil_municipio.csv')
            
            # Filtrar apenas dados do MS
            df_rebanho = df_rebanho[df_rebanho['sigla_uf'] == 'MS']
            
            # Mesclar com dados dos municípios
            df_rebanho = pd.merge(df_rebanho, 
                                 df_municipios[['id_municipio', 'nome']], 
                                 on='id_municipio', 
                                 how='left')
            
            return df_rebanho
        except Exception as e:
            st.error(f'Erro ao carregar dados dos rebanhos: {str(e)}')
            return None

    def plot_evolucao_rebanho(df):
        # Agrupar por ano e tipo de rebanho
        df_evolucao = df.groupby(['ano', 'tipo_rebanho'])['quantidade'].sum().reset_index()
        
        # Criar gráfico de linhas
        fig = go.Figure()
        for tipo in df_evolucao['tipo_rebanho'].unique():
            dados_tipo = df_evolucao[df_evolucao['tipo_rebanho'] == tipo]
            fig.add_trace(go.Scatter(
                x=dados_tipo['ano'],
                y=dados_tipo['quantidade'],
                name=tipo,
                mode='lines+markers'
            ))
        
        fig.update_layout(
            title='Evolução do Efetivo dos Rebanhos ao Longo dos Anos',
            xaxis_title='Ano',
            yaxis_title='Quantidade de Cabeças',
            template='plotly_white'
        )
        
        return fig

    def plot_composicao_rebanho(df, ano):
        # Filtrar dados do ano selecionado
        df_ano = df[df['ano'] == ano]
        
        # Agrupar por tipo de rebanho
        df_composicao = df_ano.groupby('tipo_rebanho')['quantidade'].sum()
        
        # Criar gráfico de pizza
        fig = go.Figure(data=[go.Pie(
            labels=df_composicao.index,
            values=df_composicao.values,
            hole=0.3
        )])
        
        fig.update_layout(
            title=f'Composição do Rebanho em {ano}',
            template='plotly_white'
        )
        
        return fig

    def plot_taxa_crescimento(df):
        # Calcular taxa de crescimento ano a ano
        df_crescimento = df.groupby(['ano', 'tipo_rebanho'])['quantidade'].sum().reset_index()
        df_crescimento['taxa_crescimento'] = df_crescimento.groupby('tipo_rebanho')['quantidade'].pct_change() * 100
        
        # Criar gráfico de barras
        fig = go.Figure()
        for tipo in df_crescimento['tipo_rebanho'].unique():
            dados_tipo = df_crescimento[df_crescimento['tipo_rebanho'] == tipo]
            fig.add_trace(go.Bar(
                x=dados_tipo['ano'],
                y=dados_tipo['taxa_crescimento'],
                name=tipo
            ))
        
        fig.update_layout(
            title='Taxa de Crescimento Anual por Tipo de Rebanho',
            xaxis_title='Ano',
            yaxis_title='Taxa de Crescimento (%)',
            template='plotly_white',
            barmode='group'
        )
        
        return fig

    def plot_distribuicao_municipios(df, ano):
        # Filtrar dados do ano selecionado
        df_ano = df[df['ano'] == ano]
        
        # Agrupar por município
        df_municipios = df_ano.groupby(['nome', 'tipo_rebanho'])['quantidade'].sum().reset_index()
        
        # Criar gráfico de barras empilhadas
        fig = go.Figure()
        for tipo in df_municipios['tipo_rebanho'].unique():
            dados_tipo = df_municipios[df_municipios['tipo_rebanho'] == tipo]
            fig.add_trace(go.Bar(
                x=dados_tipo['nome'],
                y=dados_tipo['quantidade'],
                name=tipo
            ))
        
        fig.update_layout(
            title=f'Distribuição dos Rebanhos por Município em {ano}',
            xaxis_title='Município',
            yaxis_title='Quantidade de Cabeças',
            template='plotly_white',
            barmode='stack',
            xaxis_tickangle=-45,
            height=600
        )
        
        return fig

    # Carregar dados
    df = carregar_dados_rebanho()

    if df is not None:
        # Mostrar gráficos
        st.plotly_chart(plot_evolucao_rebanho(df), use_container_width=True)
        
        # Usar o ano mais recente para análises detalhadas
        ano_selecionado = df['ano'].max()
        
        st.plotly_chart(plot_composicao_rebanho(df, ano_selecionado), use_container_width=True)
        st.plotly_chart(plot_taxa_crescimento(df), use_container_width=True)
        
        st.plotly_chart(plot_distribuicao_municipios(df, ano_selecionado), use_container_width=True)
        
        # Adicionar estatísticas descritivas
        st.subheader('Estatísticas Descritivas')
        df_stats = df[df['ano'] == ano_selecionado].groupby('tipo_rebanho').agg({
            'quantidade': ['sum', 'mean', 'std', 'min', 'max']
        }).round(2)
        df_stats.columns = ['Total', 'Média por Município', 'Desvio Padrão', 'Mínimo', 'Máximo']
        st.dataframe(df_stats)

# Execute a função se este arquivo for executado diretamente
if __name__ == "__main__":
    mostrar_dados_rebanhos()