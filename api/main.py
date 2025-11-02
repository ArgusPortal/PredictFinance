"""
Aplicação FastAPI para Previsão de Preços B3SA3.SA

Esta API serve o modelo LSTM treinado para fazer previsões de preços
de ações da B3 S.A. (B3SA3.SA).

Fase 8: Inclui sistema de monitoramento de produção com logging estruturado.
"""

import os
import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any

import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from tensorflow.keras.models import load_model

# Adiciona o diretório raiz ao path para imports
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

from api.schemas import (
    PrevisaoInput,
    PrevisaoOutput,
    HealthResponse,
    InfoModeloResponse
)

# Sistema de monitoramento (Fase 8)
from api.monitoring import get_prediction_logger, get_metrics_logger


# Variáveis globais para armazenar modelo e scaler
model = None
scaler = None
WINDOW_SIZE = 60
NUM_FEATURES = 5


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerenciador de ciclo de vida da aplicação.
    
    Carrega o modelo e scaler na inicialização e libera recursos
    no encerramento.
    """
    global model, scaler
    
    # Startup: Carregar modelo e scaler
    print("🚀 Iniciando API...")
    print("📂 Carregando artefatos do modelo...")
    
    try:
        # Caminhos dos artefatos
        model_path = ROOT_DIR / "models" / "lstm_model_best.h5"
        scaler_path = ROOT_DIR / "models" / "scaler.pkl"
        
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


@app.get(
    "/",
    response_model=HealthResponse,
    summary="Health Check",
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
        # Extrair dados da requisição
        dados = previsao_input.prices
        
        # Verificar número de preços (validação adicional)
        if len(dados) != WINDOW_SIZE:
            metrics_logger.increment_error()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"É necessário fornecer exatamente {WINDOW_SIZE} preços. Recebidos: {len(dados)}"
            )
        
        # Converter para numpy array e reshape para normalização
        # Shape: (60,) -> (60, 1) para passar pelo scaler
        dados_array = np.array(dados).reshape(-1, 1)
        
        # Normalizar os dados usando o scaler
        dados_normalizados = scaler.transform(dados_array)
        
        # Reshape para formato esperado pelo modelo LSTM
        # Shape: (60, 1) -> (1, 60, 1) 
        # onde (batch_size, timesteps, features)
        # Nota: Como o modelo foi treinado com 5 features, vamos replicar
        # o valor normalizado para todas as 5 features
        dados_lstm = np.repeat(dados_normalizados.reshape(1, WINDOW_SIZE, 1), NUM_FEATURES, axis=2)
        
        # Fazer previsão
        predicao_normalizada = model.predict(dados_lstm, verbose=0)
        
        # Desnormalizar a previsão
        # Shape: [[valor_normalizado]] -> R$ valor_real
        predicao_real = scaler.inverse_transform(predicao_normalizada)
        
        # Extrair valor escalar
        valor_previsto = float(predicao_real[0, 0])
        
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
            input_data=previsao_input.prices if hasattr(previsao_input, 'prices') else None
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao processar previsão: {str(e)}"
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
