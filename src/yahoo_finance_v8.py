"""
Yahoo Finance API v8 - Acesso Direto
Função otimizada para coletar dados sem dependência do yfinance
Usa endpoint v8 que comprovadamente funciona
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict
import time


def coletar_dados_yahoo_v8(
    ticker: str,
    period: str = "5y",
    interval: str = "1d",
    timeout: int = 10,
    retry_attempts: int = 3,
    backoff_factor: float = 2.0
) -> pd.DataFrame:
    """
    Coleta dados diretamente da API v8 do Yahoo Finance.
    Bypass do yfinance para maior controle e confiabilidade.
    
    Endpoint testado e funcional em 20/11/2025:
    https://query2.finance.yahoo.com/v8/finance/chart/B3SA3.SA
    
    Parâmetros:
    -----------
    ticker : str
        Código da ação (ex: B3SA3.SA)
    period : str
        Período: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max
    interval : str
        Intervalo: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    timeout : int
        Timeout da requisição em segundos
    retry_attempts : int
        Número de tentativas em caso de falha
    backoff_factor : float
        Fator multiplicador do tempo de espera entre tentativas
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame com colunas: Open, High, Low, Close, Volume, Adj Close
        Index: Date (datetime)
        
    Raises:
    -------
    ValueError
        Se o ticker não retornar dados
    requests.exceptions.RequestException
        Se todas as tentativas de requisição falharem
        
    Exemplos:
    ---------
    >>> # Coletar 5 anos de dados diários
    >>> df = coletar_dados_yahoo_v8("B3SA3.SA", period="5y")
    >>> print(df.head())
    
    >>> # Coletar 1 mês de dados horários
    >>> df = coletar_dados_yahoo_v8("AAPL", period="1mo", interval="1h")
    """
    
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    # Headers realistas para simular navegador
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
    }
    
    params = {
        'interval': interval,
        'range': period
    }
    
    last_exception = None
    
    # Retry com backoff exponencial
    for attempt in range(retry_attempts):
        try:
            # Fazer requisição
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout
            )
            
            # Verificar status code
            response.raise_for_status()
            
            # Parse JSON
            data = response.json()
            
            # Verificar se há erro na resposta
            if 'chart' not in data:
                raise ValueError(f"Resposta inesperada: {data}")
            
            chart = data['chart']
            
            if chart.get('error'):
                error = chart['error']
                raise ValueError(f"Erro da API: {error.get('description', error)}")
            
            if not chart.get('result'):
                raise ValueError(f"Nenhum dado encontrado para {ticker}")
            
            # Extrair dados
            result = chart['result'][0]
            
            # Metadata
            meta = result.get('meta', {})
            currency = meta.get('currency', 'N/A')
            exchange = meta.get('exchangeName', 'N/A')
            
            # Timestamps e cotações
            timestamps = result.get('timestamp', [])
            if not timestamps:
                raise ValueError(f"Nenhum timestamp encontrado para {ticker}")
            
            indicators = result.get('indicators', {})
            quote = indicators.get('quote', [{}])[0]
            
            # Criar DataFrame
            df = pd.DataFrame({
                'Date': pd.to_datetime(timestamps, unit='s'),
                'Open': quote.get('open', []),
                'High': quote.get('high', []),
                'Low': quote.get('low', []),
                'Close': quote.get('close', []),
                'Volume': quote.get('volume', []),
            })
            
            # Adicionar Adj Close se disponível
            adjclose_data = indicators.get('adjclose', [{}])
            if adjclose_data and len(adjclose_data) > 0:
                adjclose = adjclose_data[0].get('adjclose', [])
                df['Adj Close'] = adjclose
            else:
                df['Adj Close'] = df['Close']
            
            # Definir Date como index
            df.set_index('Date', inplace=True)
            
            # Remover linhas com todos os valores NaN
            df.dropna(how='all', inplace=True)
            
            # Log de sucesso
            print(f"✅ API v8: {len(df)} registros coletados para {ticker}")
            print(f"   Período: {df.index[0].strftime('%Y-%m-%d')} a {df.index[-1].strftime('%Y-%m-%d')}")
            print(f"   Moeda: {currency} | Bolsa: {exchange}")
            
            return df
            
        except requests.exceptions.Timeout:
            last_exception = f"Timeout após {timeout}s"
            print(f"⏱️  Tentativa {attempt + 1}/{retry_attempts}: Timeout")
            
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            last_exception = f"HTTP {status_code}"
            
            if status_code in [403, 429, 999]:
                print(f"🚫 Tentativa {attempt + 1}/{retry_attempts}: Rate limit/Bloqueado (HTTP {status_code})")
            else:
                print(f"❌ Tentativa {attempt + 1}/{retry_attempts}: HTTP Error {status_code}")
            
        except (ValueError, KeyError) as e:
            last_exception = str(e)
            print(f"⚠️  Tentativa {attempt + 1}/{retry_attempts}: {e}")
            
        except Exception as e:
            last_exception = str(e)
            print(f"❌ Tentativa {attempt + 1}/{retry_attempts}: Erro inesperado - {e}")
        
        # Aguardar antes da próxima tentativa (exceto na última)
        if attempt < retry_attempts - 1:
            wait_time = backoff_factor ** attempt
            print(f"   ⏳ Aguardando {wait_time:.1f}s antes da próxima tentativa...")
            time.sleep(wait_time)
    
    # Se chegou aqui, todas as tentativas falharam
    raise requests.exceptions.RequestException(
        f"Todas as {retry_attempts} tentativas falharam. Último erro: {last_exception}"
    )


def coletar_dados_yahoo_v8_custom_range(
    ticker: str,
    start_date: str,
    end_date: str,
    interval: str = "1d",
    **kwargs
) -> pd.DataFrame:
    """
    Coleta dados com range customizado (datas específicas).
    Converte datas para Unix timestamp para a API v8.
    
    Parâmetros:
    -----------
    ticker : str
        Código da ação
    start_date : str
        Data inicial (formato: YYYY-MM-DD)
    end_date : str
        Data final (formato: YYYY-MM-DD)
    interval : str
        Intervalo dos dados
    **kwargs
        Argumentos adicionais passados para coletar_dados_yahoo_v8
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame com dados históricos
    """
    # Converter datas para Unix timestamp
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    period1 = int(start_dt.timestamp())
    period2 = int(end_dt.timestamp())
    
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    params = {
        'period1': period1,
        'period2': period2,
        'interval': interval
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        result = data['chart']['result'][0]
        
        timestamps = result['timestamp']
        quote = result['indicators']['quote'][0]
        
        df = pd.DataFrame({
            'Date': pd.to_datetime(timestamps, unit='s'),
            'Open': quote['open'],
            'High': quote['high'],
            'Low': quote['low'],
            'Close': quote['close'],
            'Volume': quote['volume'],
        })
        
        # Adj Close
        adjclose_data = result['indicators'].get('adjclose', [{}])
        if adjclose_data:
            df['Adj Close'] = adjclose_data[0].get('adjclose', df['Close'])
        else:
            df['Adj Close'] = df['Close']
        
        df.set_index('Date', inplace=True)
        df.dropna(how='all', inplace=True)
        
        print(f"✅ Coletados {len(df)} registros de {start_date} a {end_date}")
        return df
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados customizados: {e}")
        raise


# ===================================================================
# FUNÇÃO DE TESTE
# ===================================================================

if __name__ == "__main__":
    """Teste da função"""
    
    print("=" * 70)
    print("TESTE: Yahoo Finance API v8 - Acesso Direto")
    print("=" * 70)
    
    # Teste 1: Período padrão
    print("\n📊 Teste 1: Coletar 5 anos de B3SA3.SA")
    try:
        df = coletar_dados_yahoo_v8("B3SA3.SA", period="5y")
        print(f"\n✅ Sucesso! DataFrame shape: {df.shape}")
        print(f"\nPrimeiras 5 linhas:")
        print(df.head())
        print(f"\nÚltimas 5 linhas:")
        print(df.tail())
        print(f"\nInfo:")
        print(df.info())
    except Exception as e:
        print(f"\n❌ Falhou: {e}")
    
    # Teste 2: Range customizado
    print("\n" + "=" * 70)
    print("\n📊 Teste 2: Range customizado (últimos 30 dias)")
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        df = coletar_dados_yahoo_v8_custom_range(
            "B3SA3.SA",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d")
        )
        print(f"\n✅ Sucesso! {len(df)} dias coletados")
        print(df.tail())
    except Exception as e:
        print(f"\n❌ Falhou: {e}")
    
    # Teste 3: Ticker inválido (deve falhar gracefully)
    print("\n" + "=" * 70)
    print("\n📊 Teste 3: Ticker inválido (teste de erro)")
    try:
        df = coletar_dados_yahoo_v8("INVALID_TICKER_XYZ", period="1mo")
        print(f"\n⚠️  Inesperado: {len(df)} registros")
    except Exception as e:
        print(f"\n✅ Erro capturado corretamente: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 TESTES CONCLUÍDOS")
    print("=" * 70)
