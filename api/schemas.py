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
        dados: Array 2D com 60 dias de dados OHLCV (Open, High, Low, Close, Volume).
               Cada linha representa um dia com 5 valores: [Open, High, Low, Close, Volume]
    """
    dados: List[List[float]] = Field(
        ...,
        description="Array 2D: 60 dias × 5 features [Open, High, Low, Close, Volume]",
        min_length=60,
        max_length=60,
        examples=[[
            [12.5, 12.7, 12.4, 12.6, 1500000],
            [12.6, 12.8, 12.5, 12.7, 1600000]
        ]]  # Exemplo simplificado de 2 dias
    )
    
    @field_validator('dados')
    @classmethod
    def validar_dados(cls, v: List[List[float]]) -> List[List[float]]:
        """
        Valida estrutura e valores dos dados OHLCV.
        
        Args:
            v: Array 2D com dados a validar
            
        Returns:
            Array validado
            
        Raises:
            ValueError: Se formato ou valores inválidos
        """
        # Validar número de dias
        if len(v) != 60:
            raise ValueError(
                f'É necessário fornecer exatamente 60 dias de dados. Recebidos: {len(v)}'
            )
        
        # Validar cada dia
        for i, dia in enumerate(v):
            # Validar 5 features por dia
            if len(dia) != 5:
                raise ValueError(
                    f'Cada dia deve ter 5 features [Open, High, Low, Close, Volume]. '
                    f'Dia {i+1} tem {len(dia)} features'
                )
            
            # Validar valores positivos (OHLC devem ser > 0, Volume >= 0)
            open_val, high, low, close, volume = dia
            if open_val <= 0 or high <= 0 or low <= 0 or close <= 0:
                raise ValueError(
                    f'Valores OHLC devem ser positivos. Dia {i+1}: {dia[:4]}'
                )
            
            if volume < 0:
                raise ValueError(
                    f'Volume não pode ser negativo. Dia {i+1}: Volume={volume}'
                )
            
            # Validar lógica High >= Low
            if high < low:
                raise ValueError(
                    f'High deve ser >= Low. Dia {i+1}: High={high}, Low={low}'
                )
        
        return v


class PrevisaoAutoInput(BaseModel):
    """
    Modelo de dados para entrada do endpoint de previsão automática.
    
    Attributes:
        ticker: Símbolo do ticker para busca automática (ex: 'B3SA3.SA')
    """
    ticker: str = Field(
        ...,
        description="Símbolo do ticker Yahoo Finance (ex: B3SA3.SA, PETR4.SA)",
        min_length=2,
        max_length=10,
        examples=["B3SA3.SA", "PETR4.SA", "VALE3.SA"]
    )
    
    @field_validator('ticker')
    @classmethod
    def validar_ticker(cls, v: str) -> str:
        """
        Valida formato básico do ticker.
        
        Args:
            v: Ticker a validar
            
        Returns:
            Ticker normalizado (uppercase, sem espaços)
            
        Raises:
            ValueError: Se formato inválido
        """
        ticker = v.strip().upper()
        
        if not ticker:
            raise ValueError('Ticker não pode ser vazio')
        
        if len(ticker) < 2 or len(ticker) > 10:
            raise ValueError(
                f'Ticker deve ter entre 2 e 10 caracteres. Recebido: {ticker}'
            )
        
        return ticker


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
