import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.preprocessing import StandardScaler
import os
from pathlib import Path
import glob

st.set_page_config(page_title="Análise Completa de Sequestro de Carbono", layout="wide")
st.title("Análise Completa de Sequestro de Carbono")

# --- Etapa 1: Importação e leitura dos dados ---
st.header("1. Importação e Leitura dos Dados")

# Permite ao usuário escolher o dataset
opcoes_dados = {
    "Rebanhos": "data/dados_rebanho/br_ibge_ppm_efetivo_rebanhos.csv",
    "Agrícolas": "data/dados_agricolas/producao_qtde_produzida.xlsx",
    "Meteorológicos": "data/dados_meteorologicos/"  # Agora é o diretório
}
fonte = st.selectbox("Escolha a fonte de dados", list(opcoes_dados.keys()))
arquivo = opcoes_dados[fonte]

# Carrega o dataset selecionado
def carregar_dataset(arquivo, fonte):
    if fonte == "Meteorológicos":
        # Carregar e concatenar todos os CSVs do diretório
        arquivos_csv = glob.glob(os.path.join(arquivo, '*.csv'))
        dfs = []
        for arq in arquivos_csv:
            try:
                df_temp = pd.read_csv(arq, sep=None, engine='python')
            except Exception:
                df_temp = pd.read_csv(arq, sep=';')
            dfs.append(df_temp)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return None
    elif arquivo.endswith(".csv"):
        try:
            return pd.read_csv(arquivo, sep=None, engine='python')
        except Exception:
            return pd.read_csv(arquivo, sep=';')
    elif arquivo.endswith(".xlsx"):
        if fonte == "Agrícolas":
            # Carregar os dados
            df = pd.read_excel(arquivo, header=None)

            # Lista de produtos desejados
            produtos_desejados = ['Soja', 'Algodão', 'Café', 'Laranja', 'Cana de açúcar', 'Grãos', 'Madeira para papel', 'Milho']

            # Identificar a primeira coluna (que contém os anos)
            first_column = 0  # Primeira coluna é o índice 0

            # Obter o nome dos produtos na primeira linha
            produtos_row = df.iloc[0]

            # Filtrar colunas onde encontramos UF seguido de MS e o produto está na lista desejada
            uf_row = df.iloc[1]
            ms_columns = [col for col, value in uf_row.items() 
                        if value == 'MS' and any(prod.lower() in str(produtos_row[col]).lower() for prod in produtos_desejados)]

            # Incluir a primeira coluna e as colunas filtradas
            selected_columns = [first_column] + ms_columns

            # Criar o DataFrame filtrado
            df_ms = df[selected_columns]

            # Ajustar o cabeçalho
            df_ms.columns = df_ms.iloc[0]
            # Remove as duas primeiras linhas (produtos e UF), mantendo apenas os dados numéricos
            df_ms = df_ms.iloc[2:].reset_index(drop=True)

            return df_ms
        else:
            return pd.read_excel(arquivo, header=None)
    return None

df = carregar_dataset(arquivo, fonte)

if df is not None:
    st.write("Visualização dos dados:")
    st.dataframe(df.head())

    # --- Etapa 2: Seleção de variáveis ---
    st.header("2. Seleção de Variáveis para Análise")
    colunas = list(df.columns)
    variaveis_x = st.multiselect("Selecione as variáveis preditoras (X)", colunas)
    variavel_y = st.selectbox("Selecione a variável alvo (y)", [c for c in colunas if c not in variaveis_x])

    if variaveis_x and variavel_y:
        # --- Etapa 3: Análise Descritiva ---
        st.header("3. Análise Descritiva")
        st.write(df[variaveis_x + [variavel_y]].describe())
        st.write("Dados nulos por coluna:")
        st.write(df[variaveis_x + [variavel_y]].isnull().sum())

        # --- Etapa 4: Visualizações ---
        st.header("4. Visualizações")
        if st.checkbox("Mostrar heatmap de correlação"):
            plt.figure(figsize=(10, 8))
            sns.heatmap(df[variaveis_x + [variavel_y]].corr(), annot=True, cmap='viridis')
            st.pyplot(plt.gcf())
            plt.clf()
        if st.checkbox("Mostrar gráfico de dispersão (escolha eixos)"):
            if len(variaveis_x) >= 2:
                x = st.selectbox("Eixo X", variaveis_x)
                y = st.selectbox("Eixo Y", variaveis_x, index=1 if len(variaveis_x)>1 else 0)
                fig = px.scatter(df, x=x, y=y, color=variavel_y)
                st.plotly_chart(fig)
            else:
                st.info("Selecione pelo menos 2 variáveis preditoras para o gráfico de dispersão.")

        # --- Etapa 5: Pré-processamento ---
        st.header("5. Pré-processamento")
        if st.button("Remover linhas com valores nulos"):
            df = df.dropna(subset=variaveis_x + [variavel_y])
            st.success("Linhas removidas!")
            st.dataframe(df.head())
        if st.button("Normalizar dados numéricos"):
            scaler = StandardScaler()
            num_cols = df[variaveis_x].select_dtypes(include=np.number).columns
            df[num_cols] = scaler.fit_transform(df[num_cols])
            st.success("Dados normalizados!")
            st.dataframe(df.head())

        # --- Etapa 6: Modelagem ---
        st.header("6. Modelagem (Random Forest)")
        X = df[variaveis_x].select_dtypes(include=np.number)
        y = df[variavel_y]
        if st.button("Treinar modelo"):
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestRegressor(random_state=42)
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            st.write("---")
            st.subheader("Avaliação do Modelo")
            st.write(f"RMSE: {np.sqrt(mean_squared_error(y_test, y_pred)):.2f}")
            st.write(f"MAE: {mean_absolute_error(y_test, y_pred):.2f}")
            st.write(f"R²: {r2_score(y_test, y_pred):.2f}")
            importances = pd.Series(model.feature_importances_, index=X.columns)
            st.write("Importância das variáveis:")
            st.bar_chart(importances.sort_values())

            # --- Etapa extra: Visualizar uma árvore do Random Forest ---
            st.subheader("Visualizar uma árvore do Random Forest")
            st.write("Você pode visualizar uma das árvores individuais do modelo.")
            if st.button("Mostrar árvore 0 do Random Forest"):
                from sklearn.tree import export_graphviz
                import graphviz
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".dot") as tmp_file:
                    export_graphviz(model.estimators_[0], out_file=tmp_file.name, feature_names=X.columns, filled=True, rounded=True, special_characters=True)
                    tmp_file.flush()
                    with open(tmp_file.name) as f:
                        dot_graph = f.read()
                st.graphviz_chart(dot_graph)

            # --- Etapa 8: Simulação de cenário ---
            st.subheader("Simulação de Cenário")
            if len(X_test) > 0:
                idx = st.number_input("Índice de exemplo para simulação", min_value=0, max_value=len(X_test)-1, value=0)
                novo_exemplo = X_test.iloc[idx].copy()
                col_sim = st.selectbox("Coluna para simular aumento (%)", X_test.columns)
                pct = st.slider("Aumento (%)", 0, 100, 10)
                novo_exemplo[col_sim] *= (1 + pct/100)
                pred_simulado = model.predict([novo_exemplo])
                st.write(f"Predição com cenário simulado: {pred_simulado[0]:.2f}")

        # --- Etapa 9: Conclusão ---
        st.header("Conclusão")
        st.text_area("Escreva sua análise final:")
else:
    st.info("Selecione e carregue um conjunto de dados para iniciar a análise.")
