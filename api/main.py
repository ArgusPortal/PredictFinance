"""
Aplicação FastAPI para Previsão de Preços B3SA3.SA

Esta API serve o modelo LSTM treinado para fazer previsões de preços
de ações da B3 S.A. (B3SA3.SA).

Fase 8: Inclui sistema de monitoramento de produção com logging estruturado.
"""

import os
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from tensorflow.keras.models import load_model

# Adiciona o diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from api.schemas import (
    PrevisaoInput,
    PrevisaoAutoInput,
    PrevisaoOutput,
    HealthResponse,
    InfoModeloResponse
)

# Sistema de monitoramento (Fase 8)
from api.monitoring import get_prediction_logger, get_metrics_logger

# Sistema de validação de performance (Fase 12)
from src.performance_monitor import PerformanceMonitor

# Módulo de busca automática de dados (Fase 9)
from api.data_fetcher import (
    buscar_dados_historicos,
    formatar_dados_para_modelo,
    validar_ticker_format,
    obter_info_ticker
)

# Módulo de banco de dados SQLite (Fase 10)
try:
    from database import get_db
    DB_DISPONIVEL = True
except ImportError:
    DB_DISPONIVEL = False
    print("⚠️  Módulo database não encontrado - endpoints de dados históricos desabilitados")


# Variáveis globais para armazenar modelo e scaler
model = None
scaler = None
example_data = None  # Dados de exemplo pré-carregados
WINDOW_SIZE = 60
NUM_FEATURES = 5


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    
    Carrega o modelo e scaler na inicialização e libera recursos
    no encerramento.
    """
    global model, scaler, example_data
    
    # Startup: Carregar modelo e scaler
    print("🚀 Iniciando API...")
    print("📂 Carregando artefatos do modelo...")
    
    try:
        # Caminhos dos artefatos
        model_path = ROOT_DIR / "models" / "lstm_model_best.h5"
        scaler_path = ROOT_DIR / "models" / "scaler.pkl"
        example_path = ROOT_DIR / "data" / "processed" / "example_input.npy"
        
        # Validar existência dos arquivos
        if not model_path.exists():
            raise FileNotFoundError(f"Modelo não encontrado: {model_path}")
        
        if not scaler_path.exists():
            raise FileNotFoundError(f"Scaler não encontrado: {scaler_path}")
        
        # Carregar modelo
        print(f"   └─ Carregando modelo: {model_path}")
        model = load_model(str(model_path))
        print(f"   ✅ Modelo carregado com sucesso!")
        
        # Carregar scaler
        print(f"   └─ Carregando scaler: {scaler_path}")
        scaler = joblib.load(str(scaler_path))
        print(f"   ✅ Scaler carregado com sucesso!")
        
        # Carregar dados de exemplo (opcional)
        if example_path.exists():
            print(f"   └─ Carregando dados de exemplo: {example_path}")
            example_data = np.load(str(example_path))
            print(f"   ✅ Dados de exemplo carregados! Shape: {example_data.shape}")
        else:
            print(f"   ⚠️  Dados de exemplo não encontrados (opcional)")
        
        print("✅ API pronta para receber requisições!\n")
        
    except Exception as e:
        print(f"❌ Erro ao carregar artefatos: {e}")
        raise
    
    yield
    
    # Shutdown: Limpar recursos
    print("\n🛑 Encerrando API...")
    model = None
    scaler = None
    print("✅ Recursos liberados.")


# Inicializar aplicação FastAPI
app = FastAPI(
    title="API de Previsão B3SA3.SA",
    description="API REST para previsão de preços de ações da B3 S.A. usando LSTM",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Montar diretório de arquivos estáticos (interface web)
static_dir = ROOT_DIR / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get(
    "/",
    summary="Página Inicial",
    description="Redireciona para interface web ou retorna status",
    include_in_schema=False
)
async def root():
    """
    Redireciona para interface web se disponível, senão retorna health check.
    """
    index_file = ROOT_DIR / "static" / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    else:
        return await health_check()


@app.get(
    "/api",
    response_model=HealthResponse,
    summary="Health Check API",
    description="Verifica se a API está ativa e operacional",
    tags=["Status"]
)
async def health_check() -> HealthResponse:
    """
    Endpoint de health check.
    
    Returns:
        HealthResponse: Status da API e informações básicas
    """
    return HealthResponse(
        status="ativo",
        mensagem="API de previsão B3SA3.SA operacional",
        versao="1.0.0",
        modelo_carregado=(model is not None and scaler is not None)
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check Alternativo",
    description="Endpoint alternativo para verificação de saúde da API",
    tags=["Status"]
)
async def health() -> HealthResponse:
    """
    Endpoint alternativo de health check.
    
    Returns:
        HealthResponse: Status da API
    """
    return await health_check()


@app.get(
    "/info",
    response_model=InfoModeloResponse,
    summary="Informações do Modelo",
    description="Retorna informações detalhadas sobre o modelo LSTM",
    tags=["Modelo"]
)
async def info_modelo() -> InfoModeloResponse:
    """
    Retorna informações sobre o modelo carregado.
    
    Returns:
        InfoModeloResponse: Detalhes do modelo e métricas de performance
    """
    if model is None or scaler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não está carregado. Aguarde a inicialização da API."
        )
    
    return InfoModeloResponse(
        nome="LSTM_B3SA3_Predictor",
        arquitetura="LSTM - 2 camadas (64 → 32 unidades) + Dropout (0.2)",
        parametros=30369,
        metricas={
            "RMSE": "R$ 0.26",
            "MAE": "R$ 0.20",
            "MAPE": "1.53%",
            "R2": "0.9351"
        },
        window_size=60,
        features=["Open", "High", "Low", "Close", "Volume"]
    )


@app.get(
    "/data/historical/{ticker}",
    summary="Dados Históricos do Banco de Dados",
    description="Retorna dados históricos OHLCV do cache SQLite para um período específico",
    tags=["Dados"],
    status_code=status.HTTP_200_OK
)
async def obter_dados_historicos(
    ticker: str,
    start_date: str,  # YYYY-MM-DD
    end_date: str     # YYYY-MM-DD
) -> JSONResponse:
    """
    Retorna dados históricos do banco de dados SQLite.
    
    Este endpoint permite consultar qualquer período de dados históricos
    armazenados no cache local, sem depender do Yahoo Finance.
    
    Args:
        ticker: Símbolo da ação (ex: B3SA3.SA)
        start_date: Data inicial no formato YYYY-MM-DD
        end_date: Data final no formato YYYY-MM-DD
        
    Returns:
        JSONResponse com:
        - ticker: Símbolo consultado
        - period: {"start": start_date, "end": end_date}
        - count: Número de registros retornados
        - data: Array de objetos com date, open, high, low, close, volume
        
    Raises:
        HTTPException 503: Se banco de dados não estiver disponível
        HTTPException 400: Se datas forem inválidas
        HTTPException 404: Se não houver dados para o período
    """
    if not DB_DISPONIVEL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco de dados SQLite não está disponível. Execute: python database/populate_db.py"
        )
    
    # Valida formato das datas
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start_dt > end_dt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date deve ser anterior a end_date"
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de data inválido. Use YYYY-MM-DD. Erro: {str(e)}"
        )
    
    # Busca dados do banco
    try:
        db = get_db()
        df = db.get_data_by_period(ticker, start_dt, end_dt)
        
        if df is None or df.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Nenhum dado encontrado para {ticker} entre {start_date} e {end_date}. "
                       f"Execute: python database/populate_db.py --ticker {ticker}"
            )
        
        # Converte DataFrame para lista de dicionários
        data = []
        for idx, row in df.iterrows():
            # idx pode ser string ou datetime, normalizar para string
            if hasattr(idx, 'strftime'):
                date_str = idx.strftime("%Y-%m-%d")
            else:
                date_str = str(idx)
            
            data.append({
                "date": date_str,
                "open": float(row['Open']),
                "high": float(row['High']),
                "low": float(row['Low']),
                "close": float(row['Close']),
                "volume": int(row['Volume'])
            })
        
        return JSONResponse(
            content={
                "ticker": ticker,
                "period": {
                    "start": start_date,
                    "end": end_date
                },
                "count": len(data),
                "data": data
            },
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        print(f"❌ Erro ao buscar dados históricos: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao consultar banco de dados: {str(e)}"
        )


@app.post(
    "/predict",
    response_model=PrevisaoOutput,
    summary="Fazer Previsão",
    description="Gera previsão de preço para o próximo dia com base em 60 preços históricos",
    tags=["Previsão"],
    status_code=status.HTTP_200_OK
)
async def fazer_previsao(previsao_input: PrevisaoInput) -> PrevisaoOutput:
    """
    Endpoint principal para fazer previsões.
    
    Recebe uma lista de 60 preços de fechamento consecutivos e retorna
    a previsão do próximo preço.
    
    FASE 8: Inclui logging detalhado para monitoramento em produção.
    
    Args:
        previsao_input: Objeto contendo lista de 60 preços
        
    Returns:
        PrevisaoOutput: Previsão do próximo preço
        
    Raises:
        HTTPException: Se o modelo não estiver carregado ou ocorrer erro na previsão
    """
    # Inicializa loggers
    pred_logger = get_prediction_logger()
    metrics_logger = get_metrics_logger()
    
    # Incrementa contador de requisições
    metrics_logger.increment_request()
    
    # Marca início do processamento
    start_time = time.time()
    
    # Validar se modelo e scaler estão carregados
    if model is None or scaler is None:
        metrics_logger.increment_error()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não está carregado. Aguarde a inicialização da API."
        )
    
    try:
        # Extrair dados da requisição (agora é 2D array: 60 dias x 5 features)
        dados = previsao_input.dados
        
        # Verificar dimensões (validação adicional)
        if len(dados) != WINDOW_SIZE:
            metrics_logger.increment_error()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"É necessário fornecer exatamente {WINDOW_SIZE} dias de dados. Recebidos: {len(dados)}"
            )
        
        # Converter para numpy array
        # Shape: (60, 5) - 60 dias com 5 features cada [Open, High, Low, Close, Volume]
        dados_array = np.array(dados)
        
        # Validar shape
        if dados_array.shape != (WINDOW_SIZE, NUM_FEATURES):
            metrics_logger.increment_error()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shape esperado: ({WINDOW_SIZE}, {NUM_FEATURES}). Recebido: {dados_array.shape}"
            )
        
        # Normalizar os dados usando o scaler
        # Scaler espera shape (60, 5)
        dados_normalizados = scaler.transform(dados_array)
        
        # Reshape para formato esperado pelo modelo LSTM
        # Shape: (60, 5) -> (1, 60, 5) onde (batch_size, timesteps, features)
        dados_lstm = dados_normalizados.reshape(1, WINDOW_SIZE, NUM_FEATURES)
        
        # Fazer previsão
        predicao_normalizada = model.predict(dados_lstm, verbose=0)
        
        # Desnormalizar a previsão
        # O modelo retorna shape (1, 1) mas scaler espera (1, 5)
        # Criar array com shape correto onde apenas Close (índice 3) importa
        predicao_array = np.zeros((1, NUM_FEATURES))
        predicao_array[0, 3] = predicao_normalizada[0, 0]  # Close é feature index 3
        
        # Desnormalizar
        predicao_real = scaler.inverse_transform(predicao_array)
        
        # Extrair valor previsto de Close
        valor_previsto = float(predicao_real[0, 3])
        
        # Calcula tempo de processamento
        processing_time = (time.time() - start_time) * 1000  # em ms
        
        # FASE 8: Log estruturado da previsão
        # Converte dados para formato adequado (shape 60x5 -> lista de listas)
        input_for_log = dados_lstm[0].tolist()  # Shape: (60, 5)
        
        request_id = pred_logger.log_prediction(
            input_data=input_for_log,
            prediction=valor_previsto,
            processing_time_ms=processing_time
        )
        
        # Retornar resposta
        return PrevisaoOutput(
            preco_previsto=round(valor_previsto, 2),
            confianca="alta",
            mensagem=f"Previsão gerada com sucesso. Modelo com MAPE de 1.53% no teste. [ID: {request_id}]"
        )
        
    except HTTPException:
        # Re-lançar exceções HTTP
        raise
        
    except Exception as e:
        # Capturar qualquer outro erro
        metrics_logger.increment_error()
        
        # Log do erro
        pred_logger.log_error(
            error_message=str(e),
            input_data=previsao_input.dados if hasattr(previsao_input, 'dados') else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar previsão: {str(e)}"
        )


@app.post(
    "/predict/auto",
    response_model=PrevisaoOutput,
    summary="Previsão Automática via Ticker",
    description="Busca automaticamente dados OHLCV do Yahoo Finance e gera previsão",
    tags=["Previsão"],
    status_code=status.HTTP_200_OK
)
async def fazer_previsao_auto(previsao_input: PrevisaoAutoInput) -> PrevisaoOutput:
    """
    Endpoint de previsão automática com busca de dados via Yahoo Finance.
    
    Recebe apenas um ticker (ex: 'B3SA3.SA') e automaticamente:
    1. Busca últimos 60 dias de dados OHLCV via yfinance
    2. Normaliza os dados
    3. Gera previsão do próximo preço de fechamento
    
    Args:
        previsao_input: Objeto contendo ticker symbol
        
    Returns:
        PrevisaoOutput: Previsão do próximo preço
        
    Raises:
        HTTPException: Se ticker inválido, dados insuficientes ou erro na previsão
    """
    # Inicializa loggers
    pred_logger = get_prediction_logger()
    metrics_logger = get_metrics_logger()
    
    # Incrementa contador de requisições
    metrics_logger.increment_request()
    
    # Marca início do processamento
    start_time = time.time()
    
    # Validar se modelo e scaler estão carregados
    if model is None or scaler is None:
        metrics_logger.increment_error()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não está carregado. Aguarde a inicialização da API."
        )
    
    try:
        # Validar e normalizar ticker
        ticker = validar_ticker_format(previsao_input.ticker)
        
        # Buscar dados históricos do Yahoo Finance (retorna fonte também)
        dados_array, df_original, data_source = buscar_dados_historicos(
            ticker=ticker,
            dias=WINDOW_SIZE,
            validar=True
        )
        
        # Validar shape dos dados
        if dados_array.shape != (WINDOW_SIZE, NUM_FEATURES):
            metrics_logger.increment_error()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Dados retornados com shape incorreto: {dados_array.shape}"
            )
        
        # Normalizar os dados usando o scaler
        dados_normalizados = scaler.transform(dados_array)
        
        # Reshape para formato esperado pelo modelo LSTM
        # Shape: (60, 5) -> (1, 60, 5)
        dados_lstm = dados_normalizados.reshape(1, WINDOW_SIZE, NUM_FEATURES)
        
        # Fazer previsão
        predicao_normalizada = model.predict(dados_lstm, verbose=0)
        
        # Desnormalizar a previsão
        # Criar array com shape correto para inverse_transform
        # Precisamos passar array (1, 5) onde apenas Close (índice 3) importa
        predicao_array = np.zeros((1, NUM_FEATURES))
        predicao_array[0, 3] = predicao_normalizada[0, 0]  # Close é feature index 3
        
        # Desnormalizar
        predicao_real = scaler.inverse_transform(predicao_array)
        
        # Extrair valor previsto de Close
        valor_previsto = float(predicao_real[0, 3])
        
        # Calcular tempo de processamento
        processing_time = (time.time() - start_time) * 1000  # em ms
        
        # Obter informações do ticker
        info_ticker = obter_info_ticker(ticker)
        ticker_info_str = f" ({info_ticker['nome']})" if info_ticker else ""
        
        # Formatar data dos dados (verificar se index é datetime)
        try:
            if hasattr(df_original.index[-1], 'strftime'):
                data_str = df_original.index[-1].strftime('%Y-%m-%d')
            else:
                data_str = "dados de fallback"
        except:
            data_str = "dados históricos"
        
        # Log estruturado da previsão
        input_for_log = dados_lstm[0].tolist()  # Shape: (60, 5)
        
        request_id = pred_logger.log_prediction(
            input_data=input_for_log,
            prediction=valor_previsto,
            processing_time_ms=processing_time,
            data_source=data_source  # Adicionar fonte dos dados
        )
        
        # Registrar previsão no sistema de monitoramento (Fase 12)
        try:
            monitor = PerformanceMonitor(ticker=ticker)
            monitor.register_prediction(
                prediction_value=valor_previsto,
                prediction_date=datetime.now().isoformat(),
                request_id=request_id
            )
        except Exception as mon_error:
            # Não falhar a previsão se monitoramento falhar
            print(f"⚠️  Erro ao registrar no monitoramento: {mon_error}")
        
        # Retornar resposta
        return PrevisaoOutput(
            preco_previsto=round(valor_previsto, 2),
            confianca="alta",
            mensagem=f"Previsão para {ticker}{ticker_info_str} gerada com sucesso. "
                    f"Modelo MAPE 1.53%. Dados até: {data_str} "
                    f"[ID: {request_id}]"
        )
        
    except HTTPException:
        # Re-lançar exceções HTTP (já tratadas)
        raise
        
    except Exception as e:
        # Capturar qualquer outro erro
        metrics_logger.increment_error()
        
        # Log do erro
        pred_logger.log_error(
            error_message=str(e),
            input_data={"ticker": previsao_input.ticker}
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar previsão automática: {str(e)}"
        )


@app.get(
    "/predict/example",
    response_model=PrevisaoOutput,
    summary="Previsão com Dados de Exemplo",
    description="Gera previsão usando dados de exemplo pré-carregados (demonstração)",
    tags=["Previsão"],
    status_code=status.HTTP_200_OK
)
async def fazer_previsao_exemplo() -> PrevisaoOutput:
    """
    Endpoint de demonstração com dados de exemplo pré-carregados.
    
    Não requer nenhum input - usa dados de teste reais salvos.
    Ideal para testar rapidamente a API sem precisar fornecer dados.
    
    Returns:
        PrevisaoOutput: Previsão do próximo preço
        
    Raises:
        HTTPException: Se modelo não carregado ou dados de exemplo não disponíveis
    """
    # Inicializa loggers
    pred_logger = get_prediction_logger()
    metrics_logger = get_metrics_logger()
    
    # Incrementa contador
    metrics_logger.increment_request()
    
    # Marca início
    start_time = time.time()
    
    # Validar se modelo e dados estão carregados
    if model is None or scaler is None:
        metrics_logger.increment_error()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não está carregado. Aguarde a inicialização da API."
        )
    
    if example_data is None:
        metrics_logger.increment_error()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dados de exemplo não disponíveis. Execute: python generate_example_data.py"
        )
    
    try:
        # Usar dados de exemplo (já estão normalizados)
        # Shape: (60, 5) -> (1, 60, 5)
        dados_lstm = example_data.reshape(1, WINDOW_SIZE, NUM_FEATURES)
        
        # Fazer previsão
        predicao_normalizada = model.predict(dados_lstm, verbose=0)
        
        # Desnormalizar
        predicao_array = np.zeros((1, NUM_FEATURES))
        predicao_array[0, 3] = predicao_normalizada[0, 0]
        predicao_real = scaler.inverse_transform(predicao_array)
        valor_previsto = float(predicao_real[0, 3])
        
        # Tempo de processamento
        processing_time = (time.time() - start_time) * 1000
        
        # Log
        input_for_log = dados_lstm[0].tolist()
        request_id = pred_logger.log_prediction(
            input_data=input_for_log,
            prediction=valor_previsto,
            processing_time_ms=processing_time
        )
        
        # Retornar resposta
        return PrevisaoOutput(
            preco_previsto=round(valor_previsto, 2),
            confianca="alta",
            mensagem=f"Previsão de exemplo gerada com sucesso. "
                    f"Usando dados reais do conjunto de teste. "
                    f"Modelo MAPE 1.53%. [ID: {request_id}]"
        )
        
    except Exception as e:
        metrics_logger.increment_error()
        pred_logger.log_error(
            error_message=str(e),
            input_data=None
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar previsão de exemplo: {str(e)}"
        )


@app.get(
    "/metrics",
    summary="Métricas do Modelo",
    description="Retorna as métricas de performance do modelo no conjunto de teste",
    tags=["Modelo"]
)
async def obter_metricas() -> Dict[str, Any]:
    """
    Retorna as métricas de performance do modelo.
    
    Returns:
        Dict contendo as métricas de avaliação
    """
    if model is None or scaler is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modelo não está carregado."
        )
    
    return {
        "metricas_teste": {
            "RMSE": {
                "valor": "R$ 0.26",
                "descricao": "Raiz do Erro Quadrático Médio"
            },
            "MAE": {
                "valor": "R$ 0.20",
                "descricao": "Erro Absoluto Médio"
            },
            "MAPE": {
                "valor": "1.53%",
                "descricao": "Erro Percentual Absoluto Médio",
                "interpretacao": "EXCELENTE (< 2%)"
            },
            "R2": {
                "valor": "0.9351",
                "descricao": "Coeficiente de Determinação",
                "interpretacao": "Modelo explica 93.51% da variância"
            }
        },
        "parametros_modelo": {
            "window_size": 60,
            "num_features": 5,
            "camadas": "LSTM(64) + Dropout(0.2) + LSTM(32) + Dense(1)",
            "total_parametros": 30369
        },
        "dados_treinamento": {
            "periodo": "2020-11-03 a 2025-10-31",
            "total_dias": 1246,
            "sequencias_geradas": 1186,
            "divisao": {
                "treino": "70% (830 sequências)",
                "validacao": "15% (177 sequências)",
                "teste": "15% (179 sequências)"
            }
        }
    }


# ============================================================
# ENDPOINTS DE MONITORAMENTO DE PERFORMANCE
# ============================================================

@app.post(
    "/monitoring/register",
    summary="Registrar Previsão para Monitoramento",
    description="Registra uma previsão para validação futura contra dados reais",
    tags=["Monitoramento"]
)
async def registrar_previsao_monitoramento(
    prediction_value: float,
    ticker: str = "B3SA3.SA",
    request_id: str = None
) -> Dict[str, Any]:
    """
    Registra uma previsão no sistema de monitoramento para validação posterior.
    
    Args:
        prediction_value: Valor previsto
        ticker: Símbolo da ação
        request_id: ID da requisição
    
    Returns:
        Confirmação do registro
    """
    try:
        monitor = PerformanceMonitor(ticker=ticker)
        monitor.register_prediction(
            prediction_value=prediction_value,
            prediction_date=datetime.now().isoformat(),
            request_id=request_id
        )
        
        return {
            "status": "success",
            "message": "Previsão registrada para monitoramento",
            "prediction_value": prediction_value,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar previsão: {str(e)}"
        )


@app.get(
    "/monitoring/performance",
    summary="Métricas de Performance em Produção",
    description="Retorna métricas de validação de previsões contra valores reais",
    tags=["Monitoramento"]
)
async def obter_performance_producao(ticker: str = "B3SA3.SA") -> Dict[str, Any]:
    """
    Retorna métricas de performance do modelo em produção.
    
    Compara previsões realizadas com valores reais do mercado.
    
    Args:
        ticker: Símbolo da ação
    
    Returns:
        Métricas de performance e histórico
    """
    try:
        monitor = PerformanceMonitor(ticker=ticker)
        
        # Carrega histórico de métricas
        metrics_history = monitor.metrics_history
        
        # Carrega previsões (validadas e pendentes)
        predictions_db = monitor.predictions_db
        
        # Conta previsões por status
        validated = [p for p in predictions_db.get("predictions", []) if p.get("validated")]
        pending = [p for p in predictions_db.get("predictions", []) if not p.get("validated")]
        
        # Calcula estatísticas das validadas
        if validated:
            errors = [p.get("error", 0) for p in validated if p.get("error") is not None]
            error_pcts = [p.get("error_pct", 0) for p in validated if p.get("error_pct") is not None]
            
            stats = {
                "total_validated": len(validated),
                "total_pending": len(pending),
                "mae": float(np.mean(errors)) if errors else None,
                "mape": float(np.mean(error_pcts)) if error_pcts else None,
                "rmse": float(np.sqrt(np.mean([e**2 for e in errors]))) if errors else None,
                "min_error_pct": float(min(error_pcts)) if error_pcts else None,
                "max_error_pct": float(max(error_pcts)) if error_pcts else None,
                "avg_predicted": float(np.mean([p.get("predicted_value", 0) for p in validated])),
                "avg_actual": float(np.mean([p.get("actual_value", 0) for p in validated if p.get("actual_value")])) if any(p.get("actual_value") for p in validated) else None
            }
        else:
            stats = {
                "total_validated": 0,
                "total_pending": len(pending),
                "mae": None,
                "mape": None,
                "rmse": None,
                "min_error_pct": None,
                "max_error_pct": None,
                "avg_predicted": None,
                "avg_actual": None
            }
        
        return {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "summary": metrics_history.get("summary", {}),
            "statistics": stats,
            "daily_metrics": metrics_history.get("daily_metrics", [])[-30:],  # Últimos 30 dias
            "recent_predictions": [
                {
                    "request_id": p.get("request_id"),
                    "timestamp": p.get("timestamp"),
                    "predicted": p.get("predicted_value"),
                    "actual": p.get("actual_value"),
                    "error_pct": p.get("error_pct"),
                    "validated": p.get("validated")
                }
                for p in sorted(
                    predictions_db.get("predictions", []),
                    key=lambda x: x.get("timestamp", ""),
                    reverse=True
                )[:20]  # Últimas 20 previsões
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao obter métricas de performance: {str(e)}"
        )


@app.post(
    "/monitoring/validate",
    summary="Validar Previsões Pendentes",
    description="Executa validação de previsões pendentes contra dados reais do mercado",
    tags=["Monitoramento"]
)
async def validar_previsoes_pendentes(
    ticker: str = "B3SA3.SA",
    days_back: int = 7
) -> Dict[str, Any]:
    """
    Valida previsões pendentes comparando com dados reais.
    
    Args:
        ticker: Símbolo da ação
        days_back: Quantos dias atrás buscar dados reais
    
    Returns:
        Resultado da validação
    """
    try:
        monitor = PerformanceMonitor(ticker=ticker)
        result = monitor.validate_predictions(days_back=days_back)
        
        # Detecta degradação
        degradation = monitor.detect_degradation(threshold_mape=5.0)
        
        return {
            "status": "success",
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "validation_result": result,
            "degradation_detected": degradation,
            "message": "Validação concluída com sucesso"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao validar previsões: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("   API de Previsão B3SA3.SA - LSTM")
    print("=" * 60)
    print("\n🚀 Iniciando servidor de desenvolvimento...\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
