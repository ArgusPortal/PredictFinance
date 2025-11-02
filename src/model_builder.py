"""
===================================================================
PredictFinance - Módulo de Construção do Modelo LSTM
Definição da arquitetura da rede neural
===================================================================

Este módulo é responsável pela construção da arquitetura LSTM:
- Definição das camadas LSTM com Dropout
- Compilação do modelo com otimizador Adam
- Configuração da função de perda MSE e métrica MAE
- Geração do resumo da arquitetura

Autor: ArgusPortal
Data: 02/11/2025
Versão: 1.0.0
"""

import os
import json
import warnings
from datetime import datetime
from typing import Tuple

import numpy as np
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

warnings.filterwarnings('ignore')

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

# Diretórios
PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
DOCS_DIR = "docs/model_architecture"

# Parâmetros da arquitetura
TIMESTEPS = 60  # Janela de entrada
FEATURES = 5    # Número de features (Open, High, Low, Close, Volume)

# Arquitetura LSTM
LSTM_UNITS_1 = 64   # Neurônios na primeira camada LSTM
LSTM_UNITS_2 = 32   # Neurônios na segunda camada LSTM
DROPOUT_RATE = 0.2  # Taxa de dropout (20%)

# Compilação
OPTIMIZER = 'adam'
LOSS_FUNCTION = 'mse'  # Mean Squared Error
METRICS = ['mae']      # Mean Absolute Error

# Criar diretórios
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)


# ===================================================================
# FUNÇÕES
# ===================================================================

def construir_modelo_lstm(timesteps: int = TIMESTEPS, 
                          features: int = FEATURES,
                          lstm1_units: int = LSTM_UNITS_1,
                          lstm2_units: int = LSTM_UNITS_2,
                          dropout: float = DROPOUT_RATE) -> Sequential:
    """
    Constrói a arquitetura do modelo LSTM conforme especificações.
    
    Arquitetura:
    -----------
    1. LSTM Layer 1: 64 unidades, return_sequences=True
    2. Dropout: 0.2
    3. LSTM Layer 2: 32 unidades, return_sequences=False
    4. Dense Output: 1 unidade (previsão do preço)
    
    Parâmetros:
    -----------
    timesteps : int
        Número de passos de tempo na entrada (60 dias)
    features : int
        Número de features por timestep (5: OHLCV)
    lstm1_units : int
        Número de neurônios na primeira camada LSTM
    lstm2_units : int
        Número de neurônios na segunda camada LSTM
    dropout : float
        Taxa de dropout (0.0 a 1.0)
        
    Retorna:
    --------
    Sequential
        Modelo Keras compilado
    """
    print(f"\n{'='*70}")
    print(f"CONSTRUÇÃO DO MODELO LSTM")
    print(f"{'='*70}\n")
    
    print(f"🔨 Construindo Arquitetura:")
    print(f"{'─'*70}\n")
    
    # Inicializar modelo sequencial
    print(f"   1️⃣  Inicializando modelo Sequential...")
    model = Sequential(name='LSTM_B3SA3_Predictor')
    print(f"      ✅ Modelo inicializado\n")
    
    # Camada LSTM 1
    print(f"   2️⃣  Adicionando Camada LSTM 1:")
    print(f"      • Unidades: {lstm1_units}")
    print(f"      • Return sequences: True")
    print(f"      • Input shape: ({timesteps}, {features})")
    
    model.add(LSTM(
        units=lstm1_units,
        return_sequences=True,
        input_shape=(timesteps, features),
        name='lstm_layer_1'
    ))
    print(f"      ✅ LSTM Layer 1 adicionada\n")
    
    # Camada Dropout
    print(f"   3️⃣  Adicionando Camada Dropout:")
    print(f"      • Taxa: {dropout} ({dropout*100:.0f}%)")
    print(f"      • Função: Reduzir overfitting")
    
    model.add(Dropout(dropout, name='dropout_layer'))
    print(f"      ✅ Dropout Layer adicionada\n")
    
    # Camada LSTM 2
    print(f"   4️⃣  Adicionando Camada LSTM 2:")
    print(f"      • Unidades: {lstm2_units}")
    print(f"      • Return sequences: False (camada final recorrente)")
    
    model.add(LSTM(
        units=lstm2_units,
        return_sequences=False,
        name='lstm_layer_2'
    ))
    print(f"      ✅ LSTM Layer 2 adicionada\n")
    
    # Camada Densa de Saída
    print(f"   5️⃣  Adicionando Camada Dense de Saída:")
    print(f"      • Unidades: 1 (previsão do preço)")
    print(f"      • Ativação: Linear (regressão)")
    
    model.add(Dense(1, name='output_layer'))
    print(f"      ✅ Dense Output Layer adicionada\n")
    
    print(f"{'─'*70}")
    print(f"✅ Arquitetura construída com sucesso!\n")
    
    return model


def compilar_modelo(model: Sequential, 
                   optimizer: str = OPTIMIZER,
                   loss: str = LOSS_FUNCTION,
                   metrics: list = None) -> Sequential:
    """
    Compila o modelo LSTM com otimizador, função de perda e métricas.
    
    Parâmetros:
    -----------
    model : Sequential
        Modelo Keras a ser compilado
    optimizer : str
        Nome do otimizador ('adam', 'sgd', etc.)
    loss : str
        Função de perda ('mse', 'mae', etc.)
    metrics : list
        Lista de métricas para monitoramento
        
    Retorna:
    --------
    Sequential
        Modelo compilado
    """
    if metrics is None:
        metrics = METRICS
    
    print(f"⚙️  Compilando Modelo:")
    print(f"{'─'*70}\n")
    
    print(f"   🔧 Configurações de Compilação:")
    print(f"      • Otimizador: {optimizer.upper()}")
    print(f"        └─ Adam: Otimizador adaptativo eficiente")
    print(f"      • Função de Perda: {loss.upper()}")
    print(f"        └─ MSE: Apropriada para regressão")
    print(f"      • Métricas: {[m.upper() for m in metrics]}")
    print(f"        └─ MAE: Erro médio absoluto (interpretação fácil)\n")
    
    model.compile(
        optimizer=optimizer,
        loss=loss,
        metrics=metrics
    )
    
    print(f"   ✅ Modelo compilado com sucesso!\n")
    
    return model


def exibir_resumo_modelo(model: Sequential) -> dict:
    """
    Exibe o resumo da arquitetura do modelo e retorna informações.
    
    Parâmetros:
    -----------
    model : Sequential
        Modelo Keras compilado
        
    Retorna:
    --------
    dict
        Dicionário com informações do modelo
    """
    print(f"📊 Resumo da Arquitetura:")
    print(f"{'─'*70}\n")
    
    # Exibir resumo do Keras
    model.summary()
    
    print(f"\n{'─'*70}\n")
    
    # Contar parâmetros
    total_params = model.count_params()
    trainable_params = sum([keras.backend.count_params(w) for w in model.trainable_weights])
    non_trainable_params = total_params - trainable_params
    
    print(f"📈 Estatísticas do Modelo:")
    print(f"   • Total de parâmetros:      {total_params:,}")
    print(f"   • Parâmetros treináveis:    {trainable_params:,}")
    print(f"   • Parâmetros não-treináveis: {non_trainable_params:,}")
    print(f"   • Número de camadas:        {len(model.layers)}")
    print(f"   • Input shape:              {model.input_shape}")
    print(f"   • Output shape:             {model.output_shape}\n")
    
    # Informações das camadas
    info = {
        'timestamp': datetime.now().isoformat(),
        'model_name': model.name,
        'architecture': {
            'layers': [],
            'total_params': int(total_params),
            'trainable_params': int(trainable_params),
            'non_trainable_params': int(non_trainable_params)
        },
        'compilation': {
            'optimizer': model.optimizer.get_config()['name'],
            'loss': model.loss,
            'metrics': [m.name for m in model.metrics]
        },
        'input_shape': list(model.input_shape[1:]),
        'output_shape': list(model.output_shape[1:])
    }
    
    # Detalhes das camadas
    for layer in model.layers:
        layer_info = {
            'name': layer.name,
            'type': layer.__class__.__name__,
            'output_shape': list(layer.output_shape[1:]),
            'params': int(layer.count_params())
        }
        
        # Adicionar configurações específicas
        if isinstance(layer, LSTM):
            layer_info['units'] = layer.units
            layer_info['return_sequences'] = layer.return_sequences
        elif isinstance(layer, Dropout):
            layer_info['rate'] = float(layer.rate)
        elif isinstance(layer, Dense):
            layer_info['units'] = layer.units
            layer_info['activation'] = layer.activation.__name__
        
        info['architecture']['layers'].append(layer_info)
    
    return info


def salvar_arquitetura(model: Sequential, info: dict) -> None:
    """
    Salva a arquitetura do modelo e suas informações.
    
    Parâmetros:
    -----------
    model : Sequential
        Modelo Keras compilado
    info : dict
        Dicionário com informações do modelo
    """
    print(f"💾 Salvando Arquitetura:")
    print(f"{'─'*70}\n")
    
    # Salvar estrutura do modelo em JSON
    model_json = model.to_json()
    json_path = os.path.join(MODELS_DIR, "model_architecture.json")
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(model_json)
    
    tamanho_kb = os.path.getsize(json_path) / 1024
    print(f"   ✅ Arquitetura salva: {json_path} ({tamanho_kb:.2f} KB)")
    
    # Salvar informações detalhadas
    info_path = os.path.join(DOCS_DIR, "model_info.json")
    
    with open(info_path, 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=4, ensure_ascii=False)
    
    tamanho_kb = os.path.getsize(info_path) / 1024
    print(f"   ✅ Informações salvas: {info_path} ({tamanho_kb:.2f} KB)")
    
    # Salvar resumo em texto
    summary_path = os.path.join(DOCS_DIR, "model_summary.txt")
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        model.summary(print_fn=lambda x: f.write(x + '\n'))
    
    tamanho_kb = os.path.getsize(summary_path) / 1024
    print(f"   ✅ Resumo salvo: {summary_path} ({tamanho_kb:.2f} KB)\n")


# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """
    Função principal que constrói e compila o modelo LSTM.
    """
    try:
        # 1. Construir arquitetura
        model = construir_modelo_lstm()
        
        # 2. Compilar modelo
        model = compilar_modelo(model)
        
        # 3. Exibir resumo
        info = exibir_resumo_modelo(model)
        
        # 4. Salvar arquitetura
        salvar_arquitetura(model, info)
        
        print(f"{'='*70}")
        print(f"✅ CONSTRUÇÃO DO MODELO CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        print(f"📁 Arquivos gerados:")
        print(f"   → models/model_architecture.json")
        print(f"   → docs/model_architecture/model_info.json")
        print(f"   → docs/model_architecture/model_summary.txt")
        print(f"\n🎯 Próximos passos:")
        print(f"   → O modelo está pronto para treinamento")
        print(f"   → Execute o script de treinamento na próxima fase\n")
        
        return model
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERRO NA CONSTRUÇÃO DO MODELO: {str(e)}")
        print(f"{'='*70}\n")
        raise


if __name__ == "__main__":
    main()
