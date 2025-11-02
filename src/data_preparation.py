"""
===================================================================
PredictFinance - Módulo de Preparação de Dados para LSTM
Normalização e criação de sequências temporais
===================================================================

Este módulo é responsável pela Fase 2 do projeto:
- Carregamento dos dados limpos da Fase 1
- Normalização usando MinMaxScaler
- Criação de sequências temporais (janelas deslizantes)
- Divisão em conjuntos de treino, validação e teste
- Salvamento dos dados preparados e do scaler

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
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

# Arquivos de entrada
DATA_DIR = "data/raw"
INPUT_FILE = os.path.join(DATA_DIR, "b3sa3_historical.csv")

# Arquivos de saída
PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
DOCS_DIR = "docs/data_preparation"

# Parâmetros do modelo
TIMESTEPS = 60  # Janela de 60 dias para prever o próximo dia
TRAIN_SPLIT = 0.70  # 70% para treino
VAL_SPLIT = 0.15    # 15% para validação
TEST_SPLIT = 0.15   # 15% para teste

# Features a serem usadas (todas exceto Adj Close)
FEATURES = ['Open', 'High', 'Low', 'Close', 'Volume']
TARGET = 'Close'  # Variável alvo: preço de fechamento

# Criar diretórios
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Configuração de visualizações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def carregar_dados_limpos() -> pd.DataFrame:
    """
    Carrega os dados limpos gerados na Fase 1.
    
    Retorna:
    --------
    pd.DataFrame
        DataFrame com dados históricos limpos
    """
    print(f"\n{'='*70}")
    print(f"FASE 2: PREPARAÇÃO DOS DADOS PARA LSTM")
    print(f"{'='*70}\n")
    
    print(f"📂 Carregando dados da Fase 1...")
    print(f"   Arquivo: {INPUT_FILE}\n")
    
    try:
        # Carregar CSV com index como data
        df = pd.read_csv(INPUT_FILE, index_col=0, parse_dates=True)
        
        print(f"✅ Dados carregados com sucesso!")
        print(f"   Registros: {len(df)}")
        print(f"   Período: {df.index[0].strftime('%Y-%m-%d')} a {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"   Features: {list(df.columns)}\n")
        
        # Verificar ordem cronológica
        if not df.index.is_monotonic_increasing:
            print(f"⚠️  Ordenando dados cronologicamente...")
            df = df.sort_index()
            print(f"✅ Dados ordenados\n")
        
        # Exibir primeiras linhas
        print(f"📋 Primeiras linhas dos dados:")
        print(df.head())
        print()
        
        return df
        
    except FileNotFoundError:
        print(f"❌ Erro: Arquivo não encontrado!")
        print(f"   Execute primeiro: python src/data_collection.py")
        raise
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {str(e)}")
        raise


def normalizar_dados(df: pd.DataFrame, features: list) -> Tuple[np.ndarray, MinMaxScaler]:
    """
    Normaliza os dados usando MinMaxScaler [0, 1].
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame com dados brutos
    features : list
        Lista de features a normalizar
        
    Retorna:
    --------
    tuple
        (dados normalizados, scaler ajustado)
    """
    print(f"🔄 Normalização dos Dados:")
    print(f"{'─'*70}\n")
    
    # Selecionar apenas as features desejadas
    dados = df[features].values
    
    print(f"   📊 Features selecionadas: {features}")
    print(f"   📏 Shape dos dados: {dados.shape}\n")
    
    # Estatísticas antes da normalização
    print(f"   📈 Estatísticas ANTES da normalização (Close):")
    print(f"      Mínimo: {df[TARGET].min():.2f}")
    print(f"      Máximo: {df[TARGET].max():.2f}")
    print(f"      Média:  {df[TARGET].mean():.2f}\n")
    
    # Inicializar e ajustar o scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    dados_normalizados = scaler.fit_transform(dados)
    
    print(f"   ✅ Normalização concluída!")
    print(f"   📊 Range: [0, 1]")
    print(f"   📏 Shape normalizado: {dados_normalizados.shape}\n")
    
    # Estatísticas após normalização
    close_idx = features.index(TARGET)
    print(f"   📈 Estatísticas APÓS normalização (Close):")
    print(f"      Mínimo: {dados_normalizados[:, close_idx].min():.6f}")
    print(f"      Máximo: {dados_normalizados[:, close_idx].max():.6f}")
    print(f"      Média:  {dados_normalizados[:, close_idx].mean():.6f}\n")
    
    return dados_normalizados, scaler


def criar_sequencias(dados: np.ndarray, timesteps: int, target_idx: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    Cria sequências temporais (janelas deslizantes) para LSTM.
    
    Parâmetros:
    -----------
    dados : np.ndarray
        Dados normalizados
    timesteps : int
        Tamanho da janela temporal
    target_idx : int
        Índice da feature alvo (Close)
        
    Retorna:
    --------
    tuple
        (X: sequências de entrada, y: valores alvo)
    """
    print(f"🔨 Criação de Sequências Temporais:")
    print(f"{'─'*70}\n")
    
    print(f"   ⏱️  Timesteps (janela): {timesteps} dias")
    print(f"   🎯 Feature alvo: {FEATURES[target_idx]}\n")
    
    X, y = [], []
    
    # Criar janelas deslizantes
    for i in range(timesteps, len(dados)):
        # X[i] = sequência dos últimos 'timesteps' dias
        X.append(dados[i-timesteps:i])
        
        # y[i] = preço de fechamento do dia seguinte
        y.append(dados[i, target_idx])
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"   ✅ Sequências criadas com sucesso!")
    print(f"   📊 Shape de X (entrada): {X.shape}")
    print(f"      - Amostras: {X.shape[0]}")
    print(f"      - Timesteps: {X.shape[1]}")
    print(f"      - Features: {X.shape[2]}")
    print(f"   📊 Shape de y (alvo): {y.shape}\n")
    
    # Exemplo de uma sequência
    print(f"   📋 Exemplo de sequência:")
    print(f"      X[0] shape: {X[0].shape} (últimos {timesteps} dias)")
    print(f"      y[0] valor: {y[0]:.6f} (Close do dia {timesteps+1})\n")
    
    return X, y


def dividir_dados(X: np.ndarray, y: np.ndarray, 
                  train_pct: float, val_pct: float, test_pct: float) -> dict:
    """
    Divide dados em conjuntos de treino, validação e teste (divisão temporal).
    
    Parâmetros:
    -----------
    X : np.ndarray
        Sequências de entrada
    y : np.ndarray
        Valores alvo
    train_pct : float
        Percentual para treino
    val_pct : float
        Percentual para validação
    test_pct : float
        Percentual para teste
        
    Retorna:
    --------
    dict
        Dicionário com conjuntos divididos
    """
    print(f"✂️  Divisão dos Dados:")
    print(f"{'─'*70}\n")
    
    total_samples = len(X)
    
    # Calcular índices de divisão (divisão temporal, não aleatória!)
    train_size = int(total_samples * train_pct)
    val_size = int(total_samples * val_pct)
    
    # Divisão temporal: treino -> validação -> teste
    X_train = X[:train_size]
    y_train = y[:train_size]
    
    X_val = X[train_size:train_size+val_size]
    y_val = y[train_size:train_size+val_size]
    
    X_test = X[train_size+val_size:]
    y_test = y[train_size+val_size:]
    
    print(f"   📊 Divisão (temporal, não aleatória):")
    print(f"      Total de amostras: {total_samples}")
    print(f"      ├─ Treino:     {len(X_train):5d} ({train_pct*100:.0f}%)")
    print(f"      ├─ Validação:  {len(X_val):5d} ({val_pct*100:.0f}%)")
    print(f"      └─ Teste:      {len(X_test):5d} ({test_pct*100:.0f}%)\n")
    
    # Visualizar distribuição temporal
    print(f"   📅 Distribuição Temporal:")
    print(f"      Treino:     amostras 0 a {train_size-1}")
    print(f"      Validação:  amostras {train_size} a {train_size+val_size-1}")
    print(f"      Teste:      amostras {train_size+val_size} a {total_samples-1}\n")
    
    return {
        'X_train': X_train, 'y_train': y_train,
        'X_val': X_val, 'y_val': y_val,
        'X_test': X_test, 'y_test': y_test,
        'train_size': train_size,
        'val_size': val_size,
        'test_size': len(X_test)
    }


def salvar_dados_preparados(dados_divididos: dict, scaler: MinMaxScaler) -> None:
    """
    Salva dados preparados e scaler para uso futuro.
    
    Parâmetros:
    -----------
    dados_divididos : dict
        Dicionário com conjuntos divididos
    scaler : MinMaxScaler
        Scaler ajustado
    """
    print(f"💾 Salvando Dados Preparados:")
    print(f"{'─'*70}\n")
    
    # Salvar arrays NumPy
    arquivos_salvos = []
    
    for nome, array in dados_divididos.items():
        if isinstance(array, np.ndarray):
            filepath = os.path.join(PROCESSED_DIR, f"{nome}.npy")
            np.save(filepath, array)
            tamanho_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"   ✅ {nome}.npy salvo ({tamanho_mb:.2f} MB)")
            arquivos_salvos.append(filepath)
    
    print()
    
    # Salvar scaler
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    joblib.dump(scaler, scaler_path)
    tamanho_kb = os.path.getsize(scaler_path) / 1024
    print(f"   ✅ Scaler salvo: {scaler_path} ({tamanho_kb:.2f} KB)\n")
    arquivos_salvos.append(scaler_path)
    
    # Criar log
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'parametros': {
            'timesteps': TIMESTEPS,
            'features': FEATURES,
            'target': TARGET,
            'train_split': TRAIN_SPLIT,
            'val_split': VAL_SPLIT,
            'test_split': TEST_SPLIT
        },
        'dados': {
            'total_sequencias': int(dados_divididos['train_size'] + 
                                   dados_divididos['val_size'] + 
                                   dados_divididos['test_size']),
            'treino': {
                'X_shape': list(dados_divididos['X_train'].shape),
                'y_shape': list(dados_divididos['y_train'].shape),
                'samples': int(dados_divididos['train_size'])
            },
            'validacao': {
                'X_shape': list(dados_divididos['X_val'].shape),
                'y_shape': list(dados_divididos['y_val'].shape),
                'samples': int(dados_divididos['val_size'])
            },
            'teste': {
                'X_shape': list(dados_divididos['X_test'].shape),
                'y_shape': list(dados_divididos['y_test'].shape),
                'samples': int(dados_divididos['test_size'])
            }
        },
        'normalizacao': {
            'metodo': 'MinMaxScaler',
            'range': [0, 1],
            'scaler_path': scaler_path
        },
        'arquivos_gerados': arquivos_salvos
    }
    
    log_file = os.path.join(DOCS_DIR, "data_preparation_log.json")
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)
    
    print(f"   ✅ Log salvo: {log_file}\n")


def visualizar_preparacao(df: pd.DataFrame, dados_normalizados: np.ndarray, 
                          dados_divididos: dict) -> None:
    """
    Cria visualizações dos dados preparados.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame original
    dados_normalizados : np.ndarray
        Dados após normalização
    dados_divididos : dict
        Conjuntos divididos
    """
    print(f"📊 Gerando Visualizações:")
    print(f"{'─'*70}\n")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Preparação de Dados para LSTM - B3SA3.SA', 
                 fontsize=16, fontweight='bold')
    
    # 1. Dados originais vs normalizados (Close)
    ax1 = axes[0, 0]
    close_idx = FEATURES.index(TARGET)
    
    ax1.plot(df.index, df[TARGET], label='Original', alpha=0.7, linewidth=1.5)
    ax1_twin = ax1.twinx()
    ax1_twin.plot(df.index, dados_normalizados[:, close_idx], 
                  label='Normalizado', color='orange', alpha=0.7, linewidth=1.5)
    
    ax1.set_title('Preço de Fechamento: Original vs Normalizado', fontweight='bold')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('Preço Original (R$)', color='blue')
    ax1_twin.set_ylabel('Preço Normalizado [0,1]', color='orange')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1_twin.tick_params(axis='y', labelcolor='orange')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribuição dos dados normalizados
    ax2 = axes[0, 1]
    ax2.hist(dados_normalizados[:, close_idx], bins=50, 
             color='green', alpha=0.7, edgecolor='black')
    ax2.set_title('Distribuição do Close Normalizado', fontweight='bold')
    ax2.set_xlabel('Valor Normalizado')
    ax2.set_ylabel('Frequência')
    ax2.grid(True, alpha=0.3)
    
    # 3. Divisão temporal dos dados
    ax3 = axes[1, 0]
    train_end = dados_divididos['train_size']
    val_end = train_end + dados_divididos['val_size']
    
    indices = np.arange(len(dados_normalizados[:, close_idx]))
    ax3.plot(indices[:train_end], dados_normalizados[:train_end, close_idx], 
             label=f'Treino ({TRAIN_SPLIT*100:.0f}%)', color='blue', alpha=0.7)
    ax3.plot(indices[train_end:val_end], dados_normalizados[train_end:val_end, close_idx], 
             label=f'Validação ({VAL_SPLIT*100:.0f}%)', color='orange', alpha=0.7)
    ax3.plot(indices[val_end:], dados_normalizados[val_end:, close_idx], 
             label=f'Teste ({TEST_SPLIT*100:.0f}%)', color='green', alpha=0.7)
    
    ax3.axvline(x=train_end, color='red', linestyle='--', alpha=0.5)
    ax3.axvline(x=val_end, color='red', linestyle='--', alpha=0.5)
    ax3.set_title('Divisão Temporal: Treino/Validação/Teste', fontweight='bold')
    ax3.set_xlabel('Índice Temporal')
    ax3.set_ylabel('Close Normalizado')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Exemplo de sequência
    ax4 = axes[1, 1]
    exemplo_seq = dados_divididos['X_train'][0, :, close_idx]
    exemplo_target = dados_divididos['y_train'][0]
    
    ax4.plot(range(TIMESTEPS), exemplo_seq, marker='o', 
             linewidth=2, markersize=4, label=f'Últimos {TIMESTEPS} dias')
    ax4.axhline(y=exemplo_target, color='red', linestyle='--', 
                label=f'Alvo (dia {TIMESTEPS+1})')
    ax4.set_title(f'Exemplo de Sequência LSTM ({TIMESTEPS} timesteps)', fontweight='bold')
    ax4.set_xlabel('Timestep')
    ax4.set_ylabel('Close Normalizado')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar gráfico
    plot_path = os.path.join(DOCS_DIR, 'data_preparation_viz.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"   💾 Visualizações salvas: {plot_path}\n")
    
    plt.close()


# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """
    Função principal que executa todo o pipeline de preparação.
    """
    try:
        # 1. Carregar dados limpos
        df = carregar_dados_limpos()
        
        # 2. Normalizar dados
        dados_normalizados, scaler = normalizar_dados(df, FEATURES)
        
        # 3. Criar sequências temporais
        target_idx = FEATURES.index(TARGET)
        X, y = criar_sequencias(dados_normalizados, TIMESTEPS, target_idx)
        
        # 4. Dividir em treino/validação/teste
        dados_divididos = dividir_dados(X, y, TRAIN_SPLIT, VAL_SPLIT, TEST_SPLIT)
        
        # 5. Salvar dados preparados
        salvar_dados_preparados(dados_divididos, scaler)
        
        # 6. Visualizar preparação
        visualizar_preparacao(df, dados_normalizados, dados_divididos)
        
        print(f"{'='*70}")
        print(f"✅ FASE 2 CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        print(f"📁 Arquivos gerados:")
        print(f"   → data/processed/X_train.npy, y_train.npy")
        print(f"   → data/processed/X_val.npy, y_val.npy")
        print(f"   → data/processed/X_test.npy, y_test.npy")
        print(f"   → models/scaler.pkl")
        print(f"   → docs/data_preparation/")
        print(f"\n📊 Estatísticas:")
        print(f"   → Sequências de treino: {dados_divididos['train_size']}")
        print(f"   → Sequências de validação: {dados_divididos['val_size']}")
        print(f"   → Sequências de teste: {dados_divididos['test_size']}")
        print(f"   → Timesteps por sequência: {TIMESTEPS}")
        print(f"   → Features por timestep: {len(FEATURES)}")
        print(f"\n🎯 Próximos passos:")
        print(f"   → Execute: python src/model_training.py")
        print(f"   → Para treinar o modelo LSTM\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERRO NA FASE 2: {str(e)}")
        print(f"{'='*70}\n")
        raise


if __name__ == "__main__":
    main()
