import streamlit as st
import pandas as pd
import numpy as np
from app_completo import carregar_agricolas, carregar_rebanhos, carregar_meteorologicos

st.title('Análise Preditiva de Carbono - MS')

# Carregar dados
df_agricola = carregar_agricolas()
df_agricola.columns = [str(col) for col in df_agricola.columns]
df_meteo = carregar_meteorologicos()
if df_meteo is not None:
    df_meteo.columns = [str(col) for col in df_meteo.columns]
df_rebanhos = carregar_rebanhos()
df_rebanhos.columns = [str(col) for col in df_rebanhos.columns]

# Apenas a aba de Simulação de Cenários
with st.container():
    st.header("Simulação de Cenários")

    # Garantir que as chaves de merge estejam no mesmo tipo (string)
    if 'ano' in df_meteo.columns:
        df_meteo['ano'] = df_meteo['ano'].astype(str)
    if 'Ano' in df_agricola.columns:
        df_agricola['Ano'] = df_agricola['Ano'].astype(str)
    if 'ano' in df_rebanhos.columns:
        df_rebanhos['ano'] = df_rebanhos['ano'].astype(str)

    # Unificação dos dados
    if df_meteo is not None:
        df = pd.merge(df_meteo, df_agricola, left_on='ano', right_on='Ano', how='outer')
        df = pd.merge(df, df_rebanhos, left_on='ano', right_on='ano', how='outer')
    else:
        df = pd.merge(df_agricola, df_rebanhos, left_on='Ano', right_on='ano', how='outer')
    df = df.fillna(0)
    if 'ano' in df.columns:
        df['ano'] = df['ano'].astype(str)

    # Interface Interativa
    culturas = list(df_agricola.columns[1:])
    rebanhos = list(df_rebanhos['tipo_rebanho'].unique()) if 'tipo_rebanho' in df_rebanhos.columns else list(df_rebanhos.columns[1:])
    clima_vars = list(df_meteo.columns[1:]) if df_meteo is not None else []

    cultura_sel = st.selectbox('Escolha a cultura agrícola', culturas)
    rebanho_sel = st.selectbox('Escolha o tipo de rebanho', rebanhos)
    clima_sel = st.selectbox('Escolha a variável climática', clima_vars) if clima_vars else None

    qtd_cultura = st.slider(f'Quantidade de {cultura_sel}', 0, int(df_agricola[cultura_sel].max()*2), int(df_agricola[cultura_sel].mean()))
    qtd_rebanho = st.slider(f'Quantidade de {rebanho_sel}', 0, int(df_rebanhos[df_rebanhos["tipo_rebanho"]==rebanho_sel]["quantidade"].max()*2) if "tipo_rebanho" in df_rebanhos.columns else 1000, 100) if rebanhos else 0
    valor_clima = st.slider(f'Valor de {clima_sel}', float(df_meteo[clima_sel].min()), float(df_meteo[clima_sel].max()), float(df_meteo[clima_sel].mean())) if clima_vars else 0

    # Gráfico de emissão de carbono baseado nas escolhas
    st.subheader('Emissão de Carbono (Agrícola + Rebanho)')

    st.markdown("""
    **Como é feita a conta da predição:**
    - Para cada ano histórico, soma-se a emissão proporcional da cultura agrícola escolhida e do tipo de rebanho escolhido.
    - A emissão agrícola é ajustada conforme a quantidade selecionada no slider, proporcional ao valor histórico máximo.
    - A emissão de rebanho é ajustada conforme a quantidade selecionada no slider, proporcional ao valor histórico máximo.
    - Para prever os próximos 5 anos, é feita uma regressão linear simples (reta) sobre os anos históricos e a soma das emissões.
    - Os valores previstos são mostrados no gráfico e na tabela abaixo.
    """)

    # Calcular emissão agrícola (proporcional à quantidade escolhida)
    if 'Ano' in df_agricola.columns:
        df_agricola_plot = df_agricola[['Ano', cultura_sel]].copy()
        df_agricola_plot['Ano'] = df_agricola_plot['Ano'].astype(str)
        df_agricola_plot['emissao_agricola'] = df_agricola_plot[cultura_sel] / df_agricola_plot[cultura_sel].max() * qtd_cultura
    else:
        df_agricola_plot = pd.DataFrame({'Ano': [], 'emissao_agricola': []})

    # Calcular emissão de rebanho (proporcional à quantidade escolhida)
    if 'tipo_rebanho' in df_rebanhos.columns and 'ano' in df_rebanhos.columns:
        df_rebanho_plot = df_rebanhos[df_rebanhos['tipo_rebanho'] == rebanho_sel][['ano', 'quantidade']].copy()
        df_rebanho_plot['ano'] = df_rebanho_plot['ano'].astype(str)
        df_rebanho_plot['emissao_rebanho'] = df_rebanho_plot['quantidade'] / df_rebanho_plot['quantidade'].max() * qtd_rebanho if not df_rebanho_plot['quantidade'].max() == 0 else 0
    else:
        df_rebanho_plot = pd.DataFrame({'ano': [], 'emissao_rebanho': []})

    # Merge para alinhar anos
    df_emissao = pd.merge(
        df_agricola_plot[['Ano', 'emissao_agricola']].rename(columns={'Ano': 'ano'}),
        df_rebanho_plot[['ano', 'emissao_rebanho']],
        on='ano',
        how='outer'
    ).fillna(0)
    df_emissao['emissao_total'] = df_emissao['emissao_agricola'] + df_emissao['emissao_rebanho']
    df_emissao = df_emissao.sort_values('ano')

    # Predição para os próximos 5 anos usando regressão linear simples
    try:
        anos_hist = df_emissao['ano'].astype(int).values
        emissao_hist = df_emissao['emissao_total'].values

        # Apenas se houver pelo menos 2 anos de dados
        if len(anos_hist) >= 2:
            coef = np.polyfit(anos_hist, emissao_hist, 1)
            poly = np.poly1d(coef)
            ano_max = anos_hist.max()
            anos_pred = np.arange(ano_max + 1, ano_max + 6)
            emissao_pred = poly(anos_pred)

            df_pred = pd.DataFrame({
                'ano': anos_pred.astype(str),
                'emissao_total': emissao_pred
            })

            # Exibir apenas os próximos 5 anos previstos no gráfico
            df_emissao_plot = df_pred.set_index('ano')
        else:
            df_emissao_plot = pd.DataFrame(columns=['emissao_total'])
    except Exception:
        df_emissao_plot = pd.DataFrame(columns=['emissao_total'])

    st.line_chart(
        df_emissao_plot[['emissao_total']],
        use_container_width=True
    )

    # Mostrar tabela dos valores previstos
    st.caption("Valores previstos para os próximos 5 anos:")
    st.dataframe(df_emissao_plot.reset_index().rename(columns={'ano': 'Ano', 'emissao_total': 'Emissão Prevista'}))

    # Resultados e simulação
    st.subheader('Resultados')
    st.write('Emissão de carbono: (implementação futura)')

    st.subheader('Simulação de Cenários')
    st.write('Altere os valores acima para simular diferentes cenários.')

    st.subheader('Conclusão')
    st.write('Resumo automático da análise será exibido aqui.')
