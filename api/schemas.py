"""
Esquemas Pydantic para Validação de Dados da API

Define os modelos de dados para requisições e respostas da API.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List


class PrevisaoInput(BaseModel):
    """
    Modelo de dados para entrada do endpoint de previsão.
    
    Attributes:
        prices: Lista de 60 valores de preços de fechamento consecutivos
                (os mais recentes) para gerar a previsão do próximo dia.
    """
    prices: List[float] = Field(
        ...,
        description="Lista de 60 preços de fechamento consecutivos (valores em R$)",
        min_length=60,
        max_length=60,
        examples=[[12.5, 12.6, 12.7, 12.8]]  # Exemplo simplificado
    )
    
    @field_validator('prices')
    @classmethod
    def validar_precos(cls, v: List[float]) -> List[float]:
        """
        Valida que todos os preços são valores positivos.
        
        Args:
            v: Lista de preços a validar
            
        Returns:
            Lista de preços validada
            
        Raises:
            ValueError: Se algum preço for negativo ou zero
        """
        if len(v) != 60:
            raise ValueError(f'É necessário fornecer exatamente 60 preços. Recebidos: {len(v)}')
        
        if any(p <= 0 for p in v):
            raise ValueError('Todos os preços devem ser valores positivos maiores que zero')
        
        return v


class PrevisaoOutput(BaseModel):
    """
    Modelo de dados para resposta do endpoint de previsão.
    
    Attributes:
        preco_previsto: Valor previsto para o próximo preço de fechamento (R$)
        confianca: Indicador de confiança baseado nas métricas do modelo
        mensagem: Mensagem informativa sobre a previsão
    """
    preco_previsto: float = Field(
        ...,
        description="Preço previsto para o próximo dia (R$)",
        examples=[13.45]
    )
    confianca: str = Field(
        default="alta",
        description="Nível de confiança da previsão (baseado em MAPE 1.53%)",
        examples=["alta"]
    )
    mensagem: str = Field(
        default="Previsão gerada com sucesso",
        description="Mensagem informativa sobre o resultado",
        examples=["Previsão gerada com sucesso"]
    )


class HealthResponse(BaseModel):
    """
    Modelo de dados para resposta do endpoint de health check.
    
    Attributes:
        status: Status da API
        mensagem: Mensagem informativa
        versao: Versão da API
        modelo_carregado: Indica se o modelo está carregado em memória
    """
    status: str = Field(
        default="ativo",
        description="Status atual da API",
        examples=["ativo"]
    )
    mensagem: str = Field(
        default="API de previsão B3SA3.SA operacional",
        description="Mensagem de status",
        examples=["API de previsão B3SA3.SA operacional"]
    )
    versao: str = Field(
        default="1.0.0",
        description="Versão da API",
        examples=["1.0.0"]
    )
    modelo_carregado: bool = Field(
        default=True,
        description="Indica se o modelo LSTM foi carregado com sucesso",
        examples=[True]
    )


class InfoModeloResponse(BaseModel):
    """
    Modelo de dados para informações sobre o modelo.
    
    Attributes:
        nome: Nome do modelo
        arquitetura: Tipo de arquitetura neural
        parametros: Número de parâmetros treináveis
        metricas: Métricas de performance no conjunto de teste
        window_size: Tamanho da janela temporal (número de dias)
        features: Lista de features utilizadas
    """
    nome: str = Field(
        default="LSTM_B3SA3_Predictor",
        description="Nome do modelo",
        examples=["LSTM_B3SA3_Predictor"]
    )
    arquitetura: str = Field(
        default="LSTM - 2 camadas (64 → 32 unidades)",
        description="Descrição da arquitetura",
        examples=["LSTM - 2 camadas (64 → 32 unidades)"]
    )
    parametros: int = Field(
        default=30369,
        description="Número de parâmetros treináveis",
        examples=[30369]
    )
    metricas: dict = Field(
        default={
            "RMSE": "R$ 0.26",
            "MAE": "R$ 0.20",
            "MAPE": "1.53%",
            "R2": "0.9351"
        },
        description="Métricas de performance no conjunto de teste",
        examples=[{
            "RMSE": "R$ 0.26",
            "MAE": "R$ 0.20",
            "MAPE": "1.53%",
            "R2": "0.9351"
        }]
    )
    window_size: int = Field(
        default=60,
        description="Tamanho da janela temporal (dias)",
        examples=[60]
    )
    features: List[str] = Field(
        default=["Open", "High", "Low", "Close", "Volume"],
        description="Features utilizadas no modelo",
        examples=[["Open", "High", "Low", "Close", "Volume"]]
    )
