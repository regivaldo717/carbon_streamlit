import pandas as pd
import streamlit as st
import plotly.express as px

def load_and_prepare_data():
    df = pd.read_excel("data/dados_agricolas/producao_qtde_produzida.xlsx")
    
    # Filtrando apenas dados do MS
    df = df[df['UF'] == 'MS']
    
    # Renomeando as colunas para remover UF repetido
    df.columns = [col.replace(' UF', '') for col in df.columns]
    
    # Separando dados dos produtos
    algodao_cols = [col for col in df.columns if col.startswith('Algodão')]
    cafe_cols = [col for col in df.columns if col.startswith('Café')]
    cana_cols = [col for col in df.columns if col.startswith('Cana-de-açúcar')]
    soja_cols = [col for col in df.columns if col.startswith('Soja')]
    graos_cols = [col for col in df.columns if col.startswith('Grãos')]
    laranja_cols = [col for col in df.columns if col.startswith('Laranja')]
    madeira_cols = [col for col in df.columns if col.startswith('Madeira para Papel e Celulose')]
    milho_cols = [col for col in df.columns if col.startswith('Milho')]

    return df, algodao_cols, cafe_cols, cana_cols, soja_cols, graos_cols, laranja_cols, madeira_cols, milho_cols

def create_dashboard():
    st.title("Dashboard de Produção Agrícola e Pecuária")
    
    # Corrigindo o desempacotamento para receber todos os valores retornados
    df, algodao_cols, cafe_cols, cana_cols, soja_cols, graos_cols, laranja_cols, madeira_cols, milho_cols = load_and_prepare_data()
    
    # Alterando para usar as categorias corretas
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "Produção de Algodão", 
        "Produção de Café",
        "Produção de Cana-de-açúcar",
        "Produção de Soja",
        "Produção de Grãos",
        "Produção de Laranja",
        "Produção de Madeira",
        "Produção de Milho"
    ])
    with tab1:
        st.header("Análise da Produção de Algodão por Estado")
        
        # Gráfico de barras para comparação entre estados
        fig_algodao = px.bar(
            df,
            y=algodao_cols,
            title="Produção de Algodão por Estado",
            labels={'value': 'Quantidade Produzida', 'variable': 'Estado'},
            height=500
        )
        st.plotly_chart(fig_algodao, use_container_width=True)
        
        # Mapa de calor para visualizar correlações
        st.subheader("Correlação entre Estados - Produção de Algodão")
        corr_algodao = df[algodao_cols].corr()
        fig_corr = px.imshow(
            corr_algodao,
            title="Mapa de Correlação - Produção de Algodão",
            labels=dict(color="Correlação")
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    
    with tab2:
        st.header("Análise da Produção de Café")
        
        # Gráfico de barras para produção de café
        fig_cafe = px.bar(
            df,
            y=cafe_cols,
            title="Produção de Café em MS",
            labels={'value': 'Quantidade', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_cafe, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Café")
        st.dataframe(df[cafe_cols].describe())

if __name__ == "__main__":
    create_dashboard()