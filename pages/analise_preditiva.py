import streamlit as st
import pandas as pd
import numpy as np
from app_completo import carregar_agricolas, carregar_rebanhos
import os

st.title('Análise Preditiva de Carbono - MS')

# Carregar dados
df_agricola = carregar_agricolas()
df_agricola.columns = [str(col) for col in df_agricola.columns]
df_rebanhos = carregar_rebanhos()
df_rebanhos.columns = [str(col) for col in df_rebanhos.columns]

# NOVO: Gráfico de precipitação anual total de MS (soma das cidades)
pasta_meteo = os.path.join(os.path.dirname(__file__), '..', 'dados_meteorologicos')
if os.path.exists(pasta_meteo) and os.path.isdir(pasta_meteo):
    arquivos = [os.path.join(pasta_meteo, f) for f in os.listdir(pasta_meteo) if f.endswith('.csv')]
    dfs = []
    for arq in arquivos:
        df_tmp = pd.read_csv(arq)
        df_tmp.columns = [str(col) for col in df_tmp.columns]
        col_precip = 'PRECIPITACAO TOTAL, MENSAL (AUT)(mm)'
        if col_precip in df_tmp.columns and 'ano' in df_tmp.columns:
            df_tmp = df_tmp[['ano', col_precip]].copy()
            df_tmp = df_tmp.dropna(subset=[col_precip, 'ano'])
            df_tmp['ano'] = df_tmp['ano'].astype(str)
            dfs.append(df_tmp)
    if dfs:
        df_meteo = pd.concat(dfs)
        df_precip_total_ano = df_meteo.groupby('ano', as_index=False)[col_precip].sum(min_count=1)
        df_precip_total_ano['ano'] = df_precip_total_ano['ano'].astype(str)
        st.markdown("### Precipitação Total Anual em MS (Soma das cidades)")
        st.line_chart(
            data=df_precip_total_ano.set_index('ano')[col_precip].rename("Precipitação Total MS"),
            use_container_width=True
        )

with st.container():
    st.header("Simulação de Cenários")

    culturas = list(df_agricola.columns[1:])
    rebanhos = list(df_rebanhos['tipo_rebanho'].unique()) if 'tipo_rebanho' in df_rebanhos.columns else list(df_rebanhos.columns[1:])

    cultura_sel = st.selectbox('Escolha a cultura agrícola', culturas, index=0 if 'Algodão' not in culturas else culturas.index('Algodão'))
    rebanho_sel = st.selectbox('Escolha o tipo de rebanho', rebanhos, index=0 if 'Bovino' not in rebanhos else rebanhos.index('Bovino'))

    qtd_cultura = st.slider(f'Quantidade de {cultura_sel}', 0, int(df_agricola[cultura_sel].max()), int(df_agricola[cultura_sel].mean()))
    qtd_rebanho = st.slider(
        f'Quantidade de {rebanho_sel}',
        0,
        int(df_rebanhos[df_rebanhos["tipo_rebanho"]==rebanho_sel]["quantidade"].max()) if "tipo_rebanho" in df_rebanhos.columns else 1000,
        int(df_rebanhos[df_rebanhos["tipo_rebanho"]==rebanho_sel]["quantidade"].mean()) if "tipo_rebanho" in df_rebanhos.columns else 100
    )

    modelos = [
        "Regressão Linear",
        "ARIMA/SARIMA",
        "Prophet",
        "LSTM (Deep Learning)",
        "Random Forest"
    ]
    modelo_sel = st.selectbox("Escolha seu modelo de predição", modelos, index=0)

    # Cálculo de emissão (simplificado)
    if 'Ano' in df_agricola.columns:
        df_agricola_plot = df_agricola[['Ano', cultura_sel]].copy()
        df_agricola_plot['Ano'] = df_agricola_plot['Ano'].astype(str)
        df_agricola_plot['emissao_agricola'] = df_agricola_plot[cultura_sel] / df_agricola_plot[cultura_sel].max() * qtd_cultura
    else:
        df_agricola_plot = pd.DataFrame({'Ano': [], 'emissao_agricola': []})

    if 'tipo_rebanho' in df_rebanhos.columns and 'ano' in df_rebanhos.columns:
        df_rebanho_plot = df_rebanhos[df_rebanhos['tipo_rebanho'] == rebanho_sel][['ano', 'quantidade']].copy()
        df_rebanho_plot['ano'] = df_rebanho_plot['ano'].astype(str)
        df_rebanho_plot['emissao_rebanho'] = df_rebanho_plot['quantidade'] / df_rebanho_plot['quantidade'].max() * qtd_rebanho if not df_rebanho_plot['quantidade'].max() == 0 else 0
    else:
        df_rebanho_plot = pd.DataFrame({'ano': [], 'emissao_rebanho': []})

    df_emissao = pd.merge(
        df_agricola_plot[['Ano', 'emissao_agricola']].rename(columns={'Ano': 'ano'}),
        df_rebanho_plot[['ano', 'emissao_rebanho']],
        on='ano',
        how='outer'
    ).fillna(0)
    df_emissao['emissao_total'] = df_emissao['emissao_agricola'] + df_emissao['emissao_rebanho']
    df_emissao = df_emissao.sort_values('ano')

    # Predição baseada no modelo selecionado
    anos_hist = df_emissao['ano'].astype(int).values
    emissao_hist = df_emissao['emissao_total'].values
    df_emissao_plot = pd.DataFrame(columns=['emissao_total'])

    if len(anos_hist) >= 2:
        if modelo_sel == "Regressão Linear":
            coef = np.polyfit(anos_hist, emissao_hist, 1)
            poly = np.poly1d(coef)
            ano_max = anos_hist.max()
            anos_pred = np.arange(ano_max + 1, ano_max + 6)
            emissao_pred = poly(anos_pred)
            df_pred = pd.DataFrame({
                'ano': anos_pred.astype(str),
                'emissao_total': emissao_pred
            })
            df_emissao_plot = df_pred.set_index('ano')

        elif modelo_sel == "ARIMA/SARIMA":
            from statsmodels.tsa.arima.model import ARIMA
            try:
                model = ARIMA(emissao_hist, order=(1,1,1))
                model_fit = model.fit()
                forecast = model_fit.forecast(steps=5)
                ano_max = anos_hist.max()
                anos_pred = np.arange(ano_max + 1, ano_max + 6)
                df_pred = pd.DataFrame({
                    'ano': anos_pred.astype(str),
                    'emissao_total': forecast
                })
                df_emissao_plot = df_pred.set_index('ano')
            except Exception as e:
                st.warning(f"Erro ARIMA/SARIMA: {e}")

        elif modelo_sel == "Prophet":
            try:
                from prophet import Prophet
                df_prophet = pd.DataFrame({
                    'ds': pd.to_datetime(df_emissao['ano'], format='%Y'),
                    'y': df_emissao['emissao_total']
                })
                m = Prophet(yearly_seasonality=False, daily_seasonality=False, weekly_seasonality=False)
                m.fit(df_prophet)
                future = m.make_future_dataframe(periods=5, freq='Y')
                forecast = m.predict(future)
                forecast_pred = forecast.tail(5)
                anos_pred = forecast_pred['ds'].dt.year.astype(str).values
                emissao_pred = forecast_pred['yhat'].values
                df_pred = pd.DataFrame({
                    'ano': anos_pred,
                    'emissao_total': emissao_pred
                })
                df_emissao_plot = df_pred.set_index('ano')
            except Exception as e:
                st.warning(f"Erro Prophet: {e}")

        elif modelo_sel == "Random Forest":
            try:
                from sklearn.ensemble import RandomForestRegressor
                X = anos_hist.reshape(-1, 1)
                y = emissao_hist
                rf = RandomForestRegressor(n_estimators=100)
                rf.fit(X, y)
                ano_max = anos_hist.max()
                anos_pred = np.arange(ano_max + 1, ano_max + 6)
                emissao_pred = rf.predict(anos_pred.reshape(-1, 1))
                df_pred = pd.DataFrame({
                    'ano': anos_pred.astype(str),
                    'emissao_total': emissao_pred
                })
                df_emissao_plot = df_pred.set_index('ano')
            except Exception as e:
                st.warning(f"Erro Random Forest: {e}")

        elif modelo_sel == "LSTM (Deep Learning)":
            try:
                import importlib.util
                tf_spec = importlib.util.find_spec("tensorflow")
                if tf_spec is None:
                    st.warning("TensorFlow não está instalado. Para usar LSTM, adicione 'tensorflow' ao seu requirements.txt e instale.")
                else:
                    try:
                        # Testa se o TensorFlow pode ser importado e inicializado corretamente
                        import tensorflow as tf
                        from tensorflow import keras
                        from sklearn.preprocessing import MinMaxScaler

                        # Teste rápido de inicialização de sessão para evitar erro de DLL
                        try:
                            _ = tf.constant([0.0])
                        except Exception as e:
                            st.warning("TensorFlow está instalado, mas não pôde ser carregado corretamente (erro de ambiente/DLL). "
                                       "Considere reinstalar o TensorFlow ou usar um ambiente compatível. "
                                       f"Detalhe: {e}")
                            raise RuntimeError("TensorFlow DLL error")

                        scaler = MinMaxScaler()
                        y_scaled = scaler.fit_transform(emissao_hist.reshape(-1, 1))

                        X_lstm = []
                        y_lstm = []
                        for i in range(1, len(y_scaled)):
                            X_lstm.append(y_scaled[i-1:i, 0])
                            y_lstm.append(y_scaled[i, 0])
                        X_lstm, y_lstm = np.array(X_lstm), np.array(y_lstm)

                        X_lstm = X_lstm.reshape((X_lstm.shape[0], 1, 1))

                        model = keras.Sequential([
                            keras.layers.LSTM(10, input_shape=(1, 1)),
                            keras.layers.Dense(1)
                        ])
                        model.compile(optimizer='adam', loss='mse')
                        model.fit(X_lstm, y_lstm, epochs=100, verbose=0)

                        last_value = y_scaled[-1].reshape(1, 1, 1)
                        preds = []
                        for _ in range(5):
                            pred = model.predict(last_value, verbose=0)
                            preds.append(pred[0, 0])
                            last_value = pred.reshape(1, 1, 1)
                        emissao_pred = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
                        ano_max = anos_hist.max()
                        anos_pred = np.arange(ano_max + 1, ano_max + 6)
                        df_pred = pd.DataFrame({
                            'ano': anos_pred.astype(str),
                            'emissao_total': emissao_pred
                        })
                        df_emissao_plot = df_pred.set_index('ano')
                    except RuntimeError:
                        pass  # Mensagem já exibida acima
                    except ImportError as e:
                        st.warning("TensorFlow está instalado, mas não pôde ser carregado corretamente. "
                                   "Isso pode ser um problema de instalação, ambiente ou dependências de DLL. "
                                   "Considere reinstalar o TensorFlow ou verificar se sua instalação é compatível com seu sistema operacional.")
                    except Exception as e:
                        st.warning(f"Erro LSTM: {e}")
            except Exception as e:
                st.warning(f"Erro LSTM: {e}")

    st.subheader(f'Emissão de Carbono (Agrícola + Rebanho) - Modelo: {modelo_sel}')
    st.line_chart(
        df_emissao_plot[['emissao_total']],
        use_container_width=True
    )
    st.caption("Valores previstos para os próximos 5 anos:")
    st.dataframe(df_emissao_plot.reset_index().rename(columns={'ano': 'Ano', 'emissao_total': 'Emissão Prevista'}))
