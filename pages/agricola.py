import streamlit as st
import pandas as pd
import plotly.express as px

def carregar_dados_agricolas():
    try:
        df = pd.read_excel('data/dados_agricolas/producao_qtde_produzida.xlsx')
        
        # Verificar colunas obrigatórias
        colunas_necessarias = ['Estado', 'Município', 'Cultura', 'Quantidade', 'Ano']
        if not all(col in df.columns for col in colunas_necessarias):
            colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
            raise ValueError(f'Colunas obrigatórias faltantes: {colunas_faltantes}. Verifique o arquivo de dados.')
        
        df_ms = df[df['Estado'] == 'MS']
        return df_ms
    except Exception as e:
        st.error(f'Erro ao carregar dados agrícolas: {str(e)}')
        return None

def mostrar_analise_agricola():
    col1, col2 = st.columns([6, 1])
    with col1:
        st.title('Análise da Produção Agrícola do MS')
    with col2:
        if st.button('Voltar', use_container_width=True):
            st.switch_page('index.py')

    df = carregar_dados_agricolas()
    
    if df is not None:
        st.markdown('## Estatísticas Descritivas')
        st.dataframe(df.describe(), use_container_width=True)

        st.markdown('## Produção por Município')
        municipio_prod = df.groupby('Município')['Quantidade'].sum().reset_index()
        fig_bar = px.bar(municipio_prod, x='Município', y='Quantidade', 
                        title='Produção Agrícola por Município')
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('## Distribuição por Cultura')
        cultura_dist = df['Cultura'].value_counts().reset_index()
        fig_pie = px.pie(cultura_dist, values='count', names='Cultura', 
                        title='Distribuição das Culturas Agrícolas')
        st.plotly_chart(fig_pie, use_container_width=True)

    return df

if __name__ == '__main__':
    mostrar_analise_agricola()