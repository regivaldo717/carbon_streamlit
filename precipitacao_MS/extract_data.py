import os
import pandas as pd
from datetime import datetime, timedelta
from meteostat import Point, Daily

# Lista de principais cidades do MS
MS_CITIES = [
    'Campo Grande', 'Dourados', 'Três Lagoas', 'Corumbá',
    'Ponta Porã', 'Naviraí', 'Nova Andradina', 'Aquidauana'
]

def create_data_directory():
    """Cria o diretório para armazenar os dados se não existir"""
    os.makedirs('data', exist_ok=True)

# Coordenadas das cidades (latitude, longitude)
CITY_COORDS = {
    'Campo Grande': (-20.4697, -54.6201),
    'Dourados': (-22.2217, -54.8056),
    'Três Lagoas': (-20.7849, -51.7019),
    'Corumbá': (-19.0095, -57.6534),
    'Ponta Porã': (-22.5361, -55.7256),
    'Naviraí': (-23.0616, -54.1995),
    'Nova Andradina': (-22.2339, -53.3428),
    'Aquidauana': (-20.4666, -55.7868)
}

def get_weather_data(city, date):
    """Obtém dados meteorológicos históricos para uma cidade específica usando Meteostat"""
    try:
        lat, lon = CITY_COORDS[city]
        location = Point(lat, lon)
        
        # Definir período de busca (um dia)
        start = date
        end = date
        
        # Buscar dados diários
        data = Daily(location, start, end)
        data = data.fetch()
        
        if data.empty:
            print(f"Dados meteorológicos não disponíveis para {city} em {date.strftime('%Y-%m-%d')}")
            return None
        
        # Obter primeira (e única) linha dos dados
        daily_data = data.iloc[0]
        
        return {
            'temperatura': daily_data.get('tavg', 0),  # temperatura média
            'pressao': daily_data.get('pres', 0),      # pressão atmosférica
            'umidade': daily_data.get('rhum', 0),      # umidade relativa
            'precipitacao': daily_data.get('prcp', 0)  # precipitação
        }
    except Exception as e:
        print(f"Erro ao obter dados para {city}: {e}")
        return None

def extract_and_save_data():
    """Extrai dados meteorológicos históricos de 2020 a 2024 e salva em arquivos CSV separados por ano"""
    # Definir período de 2020 a 2024
    years = range(2020, 2025)
    
    for year in years:
        weather_data = []
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        current_date = start_date
        
        # Cache para armazenar dados já coletados
        data_cache = {}
        
        print(f"\nColetando dados para o ano {year}...")
        
        while current_date <= end_date:
            for city in MS_CITIES:
                cache_key = f"{city}_{current_date.strftime('%Y-%m-%d')}"
                
                # Verifica se os dados já estão em cache
                if cache_key in data_cache:
                    data = data_cache[cache_key]
                else:
                    data = get_weather_data(city, current_date)
                    if data:
                        data_cache[cache_key] = data
                
                if data:
                    weather_data.append({
                        'Data': current_date.strftime('%Y-%m-%d'),
                        'Cidade': city,
                        'Temperatura_C': data['temperatura'] if data['temperatura'] is not None else float('nan'),
                        'Pressao_hPa': data['pressao'] if data['pressao'] is not None else float('nan'),
                        'Umidade_Perc': data['umidade'] if data['umidade'] is not None else float('nan'),
                        'Precipitacao_mm': data['precipitacao'] if data['precipitacao'] is not None else 0.0
                    })
            
            current_date += timedelta(days=1)
        
        if weather_data:
            # Criar DataFrame com dados meteorológicos
            df_weather = pd.DataFrame(weather_data)
            
            # Salvar dados em arquivo CSV específico para o ano
            weather_file = os.path.join('data', f'dados_meteorologicos_MS_{year}.csv')
            
            try:
                df_weather.to_csv(weather_file, index=False)
                print(f'Dados meteorológicos de {year} salvos em {weather_file}')
            except Exception as e:
                print(f'Erro ao salvar arquivo CSV para {year}: {e}')
            
            # Atualizar arquivo de resumo
            with open('data/README.md', 'w', encoding='utf-8') as f:
                f.write('# Dados Meteorológicos - Mato Grosso do Sul\n\n')
                f.write(f'Última atualização: {datetime.now().strftime("%d/%m/%Y %H:%M")}\n\n')
                f.write('## Resumo dos Dados\n')
                f.write(f'- Anos disponíveis: 2020-2024\n')
                f.write(f'- Data da coleta: {datetime.now().strftime("%d/%m/%Y")}\n')
                f.write(f'- Temperatura média: {df_weather["Temperatura_C"].mean():.1f}°C\n')
                f.write(f'- Pressão média: {df_weather["Pressao_hPa"].mean():.1f} hPa\n')
                f.write(f'- Umidade média: {df_weather["Umidade_Perc"].mean():.1f}%\n')
                f.write('\n## Cidades monitoradas\n')
                for city in MS_CITIES:
                    f.write(f'- {city}\n')
        else:
            print(f'Não foi possível obter dados meteorológicos completos para {year}')

if __name__ == '__main__':
    # Mudar para o diretório do script
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    create_data_directory()
    extract_and_save_data()