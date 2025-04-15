import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.preprocessing import StandardScaler
import os
import glob

st.set_page_config(page_title="Análise do Sequestro de Carbono", layout="wide")
st.title("Análise do Sequestro de Carbono")

# Funções para carregar cada dataset individualmente
def carregar_rebanhos():
    path = "data/dados_rebanho/br_ibge_ppm_efetivo_rebanhos.csv"
    try:
        return pd.read_csv(path, sep=None, engine='python')
    except Exception:
        return pd.read_csv(path, sep=';')

def carregar_agricolas():
    path = "data/dados_agricolas/producao_qtde_produzida.xlsx"
    df = pd.read_excel(path, header=None)
    produtos_desejados = ['Soja', 'Algodão', 'Café', 'Laranja', 'Cana de açúcar', 'Grãos', 'Madeira para papel', 'Milho']
    first_column = 0
    produtos_row = df.iloc[0]
    uf_row = df.iloc[1]
    ms_columns = [col for col, value in uf_row.items() 
                  if value == 'MS' and any(prod.lower() in str(produtos_row[col]).lower() for prod in produtos_desejados)]
    selected_columns = [first_column] + ms_columns
    df_ms = df[selected_columns]
    # Corrige nomes de colunas para string
    df_ms.columns = [str(c) for c in df_ms.iloc[0]]
    df_ms = df_ms.iloc[2:].reset_index(drop=True)
    # Garante que todas as colunas são string para evitar mixed types
    df_ms.columns = [str(col) for col in df_ms.columns]
    # Converte todas as colunas (exceto a primeira, que normalmente é ano/data) para string e depois para numérico quando possível
    for col in df_ms.columns[1:]:
        # Primeiro converte para string, depois para numérico (coerce erros)
        df_ms[col] = pd.to_numeric(df_ms[col].astype(str).str.replace(",", "."), errors='coerce')
    # Garante que a primeira coluna (ano/data) seja string
    df_ms[df_ms.columns[0]] = df_ms[df_ms.columns[0]].astype(str)
    return df_ms

def carregar_meteorologicos():
    pasta = "data/dados_meteorologicos/"
    arquivos_csv = glob.glob(os.path.join(pasta, '*.csv'))
    dfs = []
    for arq in arquivos_csv:
        try:
            df_temp = pd.read_csv(arq, skiprows=10, sep=';')
        except Exception:
            try:
                df_temp = pd.read_csv(arq, sep=';')
            except Exception:
                df_temp = pd.read_csv(arq, sep=None, engine='python')
        dfs.append(df_temp)
    if dfs:
        # Padroniza colunas e seleciona apenas as desejadas
        colunas_desejadas = [
            'Data Medicao',
            'NUMERO DE DIAS COM PRECIP. PLUV, MENSAL (AUT)(nÃºmero)',
            'PRECIPITACAO TOTAL, MENSAL (AUT)(mm)',
            'PRESSAO ATMOSFERICA, MEDIA MENSAL (AUT)(mB)',
            'TEMPERATURA MEDIA, MENSAL (AUT)(Â°C)',
            'VENTO, VELOCIDADE MAXIMA MENSAL (AUT)(m/s)',
            'VENTO, VELOCIDADE MEDIA MENSAL (AUT)(m/s)'
        ]
        def normalizar_nome(nome):
            return nome.strip().lower().replace(" ", "_").replace("ã", "a").replace("ú", "u").replace("Â", "a").replace("Ã", "a").replace("ç", "c").replace(".", "").replace("(", "").replace(")", "")
        colunas_desejadas_norm = [normalizar_nome(c) for c in colunas_desejadas]
        dfs_norm = []
        for df_temp in dfs:
            df_temp.columns = [normalizar_nome(c) for c in df_temp.columns]
            # Seleciona apenas as colunas desejadas que existem no arquivo
            cols_existentes = [c for c in colunas_desejadas_norm if c in df_temp.columns]
            if not cols_existentes or 'data_medicao' not in df_temp.columns:
                continue
            df_temp = df_temp[['data_medicao'] + [c for c in cols_existentes if c != 'data_medicao']]
            dfs_norm.append(df_temp)
        if not dfs_norm:
            return None
        df_concat = pd.concat(dfs_norm, ignore_index=True)
        # Extrai o ano da data_medicao
        df_concat['ano'] = pd.to_datetime(df_concat['data_medicao'], errors='coerce').dt.year
        # Agrupa por ano e faz média dos valores numéricos para o estado do MS
        col_ano = 'ano'
        df_estado = df_concat.groupby(col_ano).mean(numeric_only=True).reset_index()
        # Renomeia as colunas para garantir que estejam normalizadas no df final
        df_estado.columns = [str(c).lower() for c in df_estado.columns]
        return df_estado
    else:
        return None

# Carregar todos os datasets
df_rebanhos = carregar_rebanhos()
df_agricolas = carregar_agricolas()
df_meteo = carregar_meteorologicos()

# Padronizar nomes de colunas para facilitar merge
def padronizar_colunas(df):
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df

df_rebanhos = padronizar_colunas(df_rebanhos)
df_agricolas = padronizar_colunas(df_agricolas)
if df_meteo is not None:
    df_meteo = padronizar_colunas(df_meteo)

# Tentar identificar colunas comuns para merge (ano, município, uf, etc)
# Ajuste conforme necessário para seus dados reais
def merge_dfs(df1, df2):
    chaves = []
    for chave in ['ano', 'data', 'município', 'municipio', 'uf']:
        if chave in df1.columns and chave in df2.columns:
            chaves.append(chave)
    if chaves:
        # Garantir que os tipos das chaves sejam iguais (string)
        for chave in chaves:
            df1[chave] = df1[chave].astype(str)
            df2[chave] = df2[chave].astype(str)
        return pd.merge(df1, df2, on=chaves, how='outer')
    else:
        # Se não houver chaves comuns, faz concat horizontal (pode gerar NaN)
        return pd.concat([df1, df2], axis=1)

# Unir todos os dados
df_merged = df_rebanhos.copy()
df_merged = merge_dfs(df_merged, df_agricolas)
if df_meteo is not None:
    df_merged = merge_dfs(df_merged, df_meteo)

df = df_merged

if df is not None and not df.empty:
    # --- Grupos de variáveis por origem ---
    # Ajuste os padrões conforme necessário para seus dados reais
    padroes_agricolas = ['soja', 'algodão', 'café', 'laranja', 'cana', 'grão', 'milho', 'madeira', 'algodao']
    padroes_meteo = ['precip', 'chuva', 'temp', 'umid', 'vento', 'rad', 'evapo', 'meteo', 'clima']
    padroes_rebanho = ['bovino', 'gado', 'rebanho', 'vaca', 'boi', 'animal', 'suino', 'caprino', 'ovino', 'equino']

    def classificar_variavel(nome):
        nome_l = nome.lower()
        if any(p in nome_l for p in padroes_agricolas):
            return 'Agrícolas'
        if any(p in nome_l for p in padroes_meteo):
            return 'Meteorológicas'
        if any(p in nome_l for p in padroes_rebanho):
            return 'Rebanho'
        return 'Outras'

    # Identifica coluna de tempo
    col_tempo = None
    for c in ['ano', 'data', 'ano_referencia', 'ano_base']:
        if c in df.columns:
            col_tempo = c
            break

    if col_tempo:
        # Ajuste: Se existir coluna tipo_rebanho, mostrar seleção dos tipos diretamente
        tipo_rebanho_col = None
        for c in df.columns:
            if c.lower() == 'tipo_rebanho':
                tipo_rebanho_col = c
                break

        tipos_rebanho_disponiveis = [
            'bovino', 'bubalino', 'caprino', 'codornas', 'equino',
            'galinaceos', 'suino', 'total', 'suino matrizes'
        ]

        # Seleção de variáveis meteorológicas e agrícolas (apenas numéricas)
        # Ajuste: nomes normalizados para meteorológicos
        colunas_meteo_norm = [
            'numero_de_dias_com_precip_pluv_mensal_aut_numero',
            'precipitacao_total_mensal_aut_mm',
            'pressao_atmosferica_media_mensal_aut_mb',
            'temperatura_media_mensal_aut_ac',
            'vento_velocidade_maxima_mensal_aut_ms',
            'vento_velocidade_media_mensal_aut_ms'
        ]
        # Garante que as colunas meteorológicas estejam presentes
        # Corrige para garantir que as colunas estejam em minúsculo e sem espaços
        df.columns = [str(c).lower() for c in df.columns]
        variaveis_meteo = [col for col in colunas_meteo_norm if col in df.columns]
        variaveis_agricolas = [
            col for col in df.columns
            if col != col_tempo
            and col.lower() not in ['quantidade', 'sigla_uf', 'tipo_rebanho']
            and pd.api.types.is_numeric_dtype(df[col])
            and classificar_variavel(col) == 'Agrícolas'
        ]

        # Seleção dos tipos de rebanho
        filtro_tipos_rebanho = None
        if tipo_rebanho_col:
            filtro_tipos_rebanho = st.multiselect(
                "Selecione os tipos de rebanho para visualizar",
                tipos_rebanho_disponiveis
            )

        # Seleção dos dados meteorológicos
        selecao_meteo = st.multiselect(
            "Selecione os dados meteorológicos para visualizar",
            variaveis_meteo
        )

        # Seleção dos dados agrícolas
        selecao_agricolas = st.multiselect(
            "Selecione os dados agrícolas para visualizar",
            variaveis_agricolas
        )

        # Plot rebanho
        def plot_rebanho(tipo_rebanho_col, tipos_rebanho):
            if not tipo_rebanho_col or not tipos_rebanho:
                return
            df_plot = df[df[tipo_rebanho_col].str.lower().isin([t.lower() for t in tipos_rebanho])]
            if df_plot.empty:
                st.info("Não há dados para os tipos de rebanho selecionados.")
                return
            # Para cada tipo selecionado, plota uma linha
            import plotly.graph_objects as go
            st.header("Evolução dos Tipos de Rebanho")
            fig = go.Figure()
            for tipo in tipos_rebanho:
                df_tipo = df_plot[df_plot[tipo_rebanho_col].str.lower() == tipo.lower()]
                if df_tipo.empty:
                    continue
                # Procura coluna de valor numérico para plotar (exceto col_tempo e tipo_rebanho)
                valor_cols = [
                    col for col in df_tipo.columns
                    if col not in [col_tempo, tipo_rebanho_col]
                    and pd.api.types.is_numeric_dtype(df_tipo[col])
                ]
                if not valor_cols:
                    continue
                # Se houver mais de uma, pega a primeira
                col_valor = valor_cols[0]
                fig.add_trace(
                    go.Scatter(
                        x=df_tipo[col_tempo],
                        y=df_tipo[col_valor],
                        name=tipo,
                        mode='lines+markers'
                    )
                )
            fig.update_layout(
                title='Evolução dos Tipos de Rebanho',
                xaxis_title=col_tempo.capitalize(),
                yaxis_title='Quantidade',
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        # Plot meteorológicos
        def plot_meteo(variaveis):
            if not variaveis:
                return
            import plotly.graph_objects as go
            st.header("Evolução dos Dados Meteorológicos")
            # Usa 'ano' como eixo x se existir
            eixo_x = 'ano' if 'ano' in df.columns else col_tempo
            df_plot = df[[eixo_x] + variaveis].copy()
            df_plot = df_plot.dropna(subset=[eixo_x])
            df_plot = df_plot.sort_values(eixo_x)
            fig = go.Figure()
            for var in variaveis:
                fig.add_trace(
                    go.Scatter(
                        x=df_plot[eixo_x],
                        y=df_plot[var],
                        name=var,
                        mode='lines+markers'
                    )
                )
            fig.update_layout(
                title='Evolução dos Dados Meteorológicos',
                xaxis_title=eixo_x.capitalize(),
                yaxis_title='Valor',
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        # Plot agrícolas
        def plot_agricolas(variaveis):
            if not variaveis:
                return
            import plotly.graph_objects as go
            st.header("Evolução dos Dados Agrícolas")
            df_plot = df[[col_tempo] + variaveis].copy()
            try:
                df_plot[col_tempo] = pd.to_numeric(df_plot[col_tempo], errors='coerce')
            except Exception:
                try:
                    df_plot[col_tempo] = pd.to_datetime(df_plot[col_tempo], errors='coerce')
                except Exception:
                    pass
            df_plot = df_plot.dropna(subset=[col_tempo])
            df_plot = df_plot.sort_values(col_tempo)
            fig = go.Figure()
            for var in variaveis:
                fig.add_trace(
                    go.Scatter(
                        x=df_plot[col_tempo],
                        y=df_plot[var],
                        name=var,
                        mode='lines+markers'
                    )
                )
            fig.update_layout(
                title='Evolução dos Dados Agrícolas',
                xaxis_title=col_tempo.capitalize(),
                yaxis_title='Produção',
                hovermode='x unified',
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

        # Exibe gráficos conforme seleção
        if tipo_rebanho_col and filtro_tipos_rebanho:
            plot_rebanho(tipo_rebanho_col, filtro_tipos_rebanho)
        if selecao_meteo:
            plot_meteo(selecao_meteo)
        if selecao_agricolas:
            plot_agricolas(selecao_agricolas)
        if not (tipo_rebanho_col and filtro_tipos_rebanho) and not selecao_meteo and not selecao_agricolas:
            st.info("Selecione ao menos uma opção para visualizar.")

    else:
        st.warning("Nenhuma coluna de tempo identificada automaticamente para o gráfico de linha.")

else:
    st.info("Não foi possível carregar ou unir os dados. Verifique os arquivos de entrada.")
