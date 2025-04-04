import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# Construir caminho compatível com todos os SOs
file_path = os.path.join("data", "dados_agricolas", "producao_qtde_produzida.xlsx")

# Verificar se o arquivo existe
if not os.path.exists(file_path):
    st.error(f"Arquivo não encontrado: {file_path}")
    st.stop()

# Carregar os dados
df = pd.read_excel(file_path, header=None)

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

# Título do aplicativo
st.title("Produção de Mato Grosso do Sul")

# Exibir os dados filtrados em uma tabela organizada
st.subheader("Dados da Produção por Produto em MS")

# Renomear as colunas para mostrar apenas o nome do produto
df_display = df_ms.copy()
for col in ms_columns:
    produto_nome = produtos_row[col]
    df_display = df_display.rename(columns={col: produto_nome})

# Exibir a tabela formatada
st.dataframe(df_display, use_container_width=True)

# Criar DataFrame para o gráfico de linhas múltiplas
df_plot = pd.DataFrame()
df_plot['Ano'] = pd.to_numeric(df_ms[first_column].iloc[2:], errors='coerce')

for produto in ms_columns:
    produto_nome = produtos_row[produto]
    valores = df_ms[produto].iloc[2:].astype(str)
    valores = valores.str.strip()
    valores = valores[valores != '']
    valores = pd.to_numeric(valores, errors='coerce')
    df_plot[produto_nome] = valores
    df_plot = df_plot.dropna(subset=[produto_nome])

# Gráfico de linhas múltiplas com Plotly
st.subheader("Evolução da Produção por Produto")
fig_lines = go.Figure()

for produto in ms_columns:
    produto_nome = produtos_row[produto]
    fig_lines.add_trace(
        go.Scatter(
            x=df_plot['Ano'],
            y=df_plot[produto_nome],
            name=produto_nome,
            mode='lines+markers'
        )
    )

fig_lines.update_layout(
    title='Evolução da Produção Agrícola no MS',
    xaxis_title='Ano',
    yaxis_title='Produção',
    hovermode='x unified',
    showlegend=True
)

st.plotly_chart(fig_lines, use_container_width=True)

# Criar gráfico de barras empilhadas
st.subheader("Composição da Produção Total por Ano")
fig_bar = go.Figure()

for produto in ms_columns:
    produto_nome = produtos_row[produto]
    fig_bar.add_trace(
        go.Bar(
            name=produto_nome,
            x=df_plot['Ano'],
            y=df_plot[produto_nome],
        )
    )

fig_bar.update_layout(
    title='Composição da Produção Agrícola no MS',
    xaxis_title='Ano',
    yaxis_title='Produção',
    barmode='stack',
    hovermode='x unified'
)

st.plotly_chart(fig_bar, use_container_width=True)