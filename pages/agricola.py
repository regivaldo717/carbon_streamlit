import pandas as pd
import streamlit as st
import plotly.express as px

def load_and_prepare_data():
    df = pd.read_excel("data/dados_agricolas/producao_qtde_produzida.xlsx")
    
    # Removendo espaços extras e caracteres especiais dos nomes das colunas
    df.columns = [col.strip() for col in df.columns]
    
    # Filtrando apenas as colunas do MS
    ms_cols = [col for col in df.columns if 'MS' in col]
    
    # Separando dados dos produtos apenas para MS
    algodao_cols = [col for col in ms_cols if col.startswith('Algodão')]
    cafe_cols = [col for col in ms_cols if col.startswith('Café')]
    cana_cols = [col for col in ms_cols if col.startswith('Cana-de-açúcar')]
    soja_cols = [col for col in ms_cols if col.startswith('Soja')]
    graos_cols = [col for col in ms_cols if col.startswith('Grãos')]
    laranja_cols = [col for col in ms_cols if col.startswith('Laranja')]
    madeira_cols = [col for col in ms_cols if col.startswith('Madeira para Papel e Celulose')]
    milho_cols = [col for col in ms_cols if col.startswith('Milho')]

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
        st.header("Análise da Produção de Algodão em MS")
        
        # Gráfico de barras para produção em MS
        fig_algodao = px.bar(
            df,
            y=algodao_cols,
            title="Produção de Algodão em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_algodao, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Algodão em MS")
        if len(algodao_cols) > 0:
            st.dataframe(df[algodao_cols].describe())
        else:
            st.warning("Nenhuma coluna de algodão encontrada para análise.")
    
    with tab2:
        st.header("Análise da Produção de Café em MS")
        
        # Gráfico de barras para produção de café
        fig_cafe = px.bar(
            df,
            y=cafe_cols,
            title="Produção de Café em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_cafe, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Café em MS")
        st.dataframe(df[cafe_cols].describe())
    
    with tab3:
        st.header("Análise da Produção de Cana-de-açúcar em MS")
        
        # Gráfico de barras para produção de cana
        fig_cana = px.bar(
            df,
            y=cana_cols,
            title="Produção de Cana-de-açúcar em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_cana, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Cana-de-açúcar em MS")
        st.dataframe(df[cana_cols].describe())
    
    with tab4:
        st.header("Análise da Produção de Soja em MS")
        
        # Gráfico de barras para produção de soja
        fig_soja = px.bar(
            df,
            y=soja_cols,
            title="Produção de Soja em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_soja, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Soja em MS")
        st.dataframe(df[soja_cols].describe())
    
    with tab5:
        st.header("Análise da Produção de Grãos em MS")
        
        # Gráfico de barras para produção de grãos
        fig_graos = px.bar(
            df,
            y=graos_cols,
            title="Produção de Grãos em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_graos, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Grãos em MS")
        st.dataframe(df[graos_cols].describe())
    
    with tab6:
        st.header("Análise da Produção de Laranja em MS")
        
        # Gráfico de barras para produção de laranja
        fig_laranja = px.bar(
            df,
            y=laranja_cols,
            title="Produção de Laranja em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_laranja, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Laranja em MS")
        st.dataframe(df[laranja_cols].describe())
    
    with tab7:
        st.header("Análise da Produção de Madeira em MS")
        
        # Gráfico de barras para produção de madeira
        fig_madeira = px.bar(
            df,
            y=madeira_cols,
            title="Produção de Madeira em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_madeira, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Madeira em MS")
        st.dataframe(df[madeira_cols].describe())
    
    with tab8:
        st.header("Análise da Produção de Milho em MS")
        
        # Gráfico de barras para produção de milho
        fig_milho = px.bar(
            df,
            y=milho_cols,
            title="Produção de Milho em MS",
            labels={'value': 'Quantidade Produzida', 'variable': 'Tipo'},
            height=500
        )
        st.plotly_chart(fig_milho, use_container_width=True)
        
        # Estatísticas descritivas
        st.subheader("Estatísticas da Produção de Milho em MS")
        st.dataframe(df[milho_cols].describe())

if __name__ == "__main__":
    create_dashboard()