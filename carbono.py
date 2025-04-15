import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Emissão de Carbono - MS", layout="wide")
st.title("Emissão de Carbono - Mato Grosso do Sul")

# Caminho do arquivo e sheet
arquivo = os.path.join("data", "dados_carbono", "BRA.xlsx")
sheet = "Subnational 2 carbon data"

# Leitura do arquivo
df = pd.read_excel(arquivo, sheet_name=sheet)

# Filtra apenas Mato Grosso do Sul
df_ms = df[df['subnational1'] == 'Mato Grosso do Sul']

# Agrupa as linhas de MS somando os valores de emissão (caso haja mais de uma linha preenchida)
if not df_ms.empty:
    df_ms_agg = df_ms.copy()
    # Soma os valores das colunas de emissão de carbono
    colunas_emissao = [
        f"gfw_forest_carbon_gross_emissions_{ano}__Mg_CO2e"
        for ano in range(2001, 2024)
    ]
    colunas_existentes = [col for col in colunas_emissao if col in df_ms_agg.columns]
    df_ms_agg = df_ms_agg[colunas_existentes].apply(pd.to_numeric, errors='coerce')
    emissoes = df_ms_agg.sum(skipna=True).values
    anos = [int(col.split("_")[5]) for col in colunas_existentes]
else:
    emissoes = []
    anos = []

df_plot = pd.DataFrame({
    "Ano": anos,
    "Emissão de Carbono (Mg CO2e)": emissoes
})

# Plot
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_plot["Ano"],
    y=df_plot["Emissão de Carbono (Mg CO2e)"],
    mode='lines+markers',
    name="Emissão de Carbono"
))
fig.update_layout(
    title="Emissão de Carbono Florestal (GFW) - Mato Grosso do Sul",
    xaxis_title="Ano",
    yaxis_title="Emissão de Carbono (Mg CO2e)",
    hovermode='x unified'
)
st.plotly_chart(fig, use_container_width=True)
