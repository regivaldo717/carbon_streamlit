# carbon_streamlit

## Descrição
Este repositório contém uma aplicação Streamlit para análise e visualização de dados relacionados ao setor agropecuário e impactos ambientais.

## Estrutura do Projeto

### Arquivos Principais

#### `index.py`
Página inicial da aplicação. Este arquivo serve como ponto de entrada principal e contém a navegação entre as diferentes seções da aplicação. Ele gerencia o menu lateral e coordena o carregamento das diferentes páginas.

#### `agricola.py`
Módulo dedicado à análise de dados agrícolas. Este componente permite a visualização e análise de:
- Produção agrícola por região/estado
- Análise de diferentes culturas e safras
- Métricas de produtividade e área plantada
- Impacto ambiental das atividades agrícolas

#### `meteorogg.py`
Componente para análise e visualização de dados meteorológicos. Funcionalidades incluem:
- Visualização de séries temporais de dados climáticos
- Análise de temperatura, precipitação e outros indicadores meteorológicos
- Correlação entre variáveis climáticas e produção agrícola
- Previsão e avaliação de tendências meteorológicas

#### `rebanho.py`
Módulo para análise de dados de rebanho e pecuária. Este componente aborda:
- Distribuição de rebanhos por região/estado
- Análise de diferentes tipos de rebanho (bovino, suíno, etc.)
- Estatísticas de produção pecuária
- Avaliação da emissão de carbono relacionada à pecuária

## Como Executar
```
streamlit run index.py
```

## Requisitos
Consulte o arquivo `requirements.txt` para ver as dependências necessárias.