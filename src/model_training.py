"""
===================================================================
PredictFinance - Módulo de Treinamento e Avaliação do Modelo LSTM
Treinamento, predição e cálculo de métricas de desempenho
===================================================================

Este módulo é responsável pela Fase 4 do projeto:
- Carregamento dos dados preparados e do modelo
- Treinamento do modelo LSTM com validation_data
- Avaliação em dados de teste
- Cálculo de métricas (MSE, RMSE, MAE)
- Visualização de resultados (real vs previsto)
- Análise e interpretação dos resultados

Autor: ArgusPortal
Data: 02/11/2025
Versão: 1.0.0
"""

import os
import json
import warnings
from datetime import datetime
from typing import Tuple, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

# Importar função de construção do modelo
import sys
sys.path.append(os.path.dirname(__file__))
from model_builder import construir_modelo_lstm, compilar_modelo

warnings.filterwarnings('ignore')

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

# Diretórios
PROCESSED_DIR = "data/processed"
MODELS_DIR = "models"
DOCS_DIR = "docs/training"

# Parâmetros de treinamento
EPOCHS = 50           # Número de épocas
BATCH_SIZE = 32       # Tamanho do batch
VERBOSE = 1           # Nível de verbosidade (0=silencioso, 1=barra de progresso, 2=uma linha por época)

# Early Stopping
EARLY_STOPPING_PATIENCE = 10  # Paciência para early stopping
RESTORE_BEST_WEIGHTS = True   # Restaurar melhores pesos

# Criar diretórios
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Configuração de visualizações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ===================================================================
# FUNÇÕES DE CARREGAMENTO
# ===================================================================

def carregar_dados_preparados() -> Dict[str, np.ndarray]:
    """
    Carrega os dados preparados da Fase 2.
    
    Retorna:
    --------
    dict
        Dicionário com arrays X_train, y_train, X_val, y_val, X_test, y_test
    """
    print(f"\n{'='*70}")
    print(f"FASE 4: TREINAMENTO E AVALIAÇÃO DO MODELO LSTM")
    print(f"{'='*70}\n")
    
    print(f"📂 Carregando Dados Preparados:")
    print(f"{'─'*70}\n")
    
    dados = {}
    arquivos = ['X_train', 'y_train', 'X_val', 'y_val', 'X_test', 'y_test']
    
    for arquivo in arquivos:
        filepath = os.path.join(PROCESSED_DIR, f"{arquivo}.npy")
        dados[arquivo] = np.load(filepath)
        print(f"   ✅ {arquivo:10s} carregado - Shape: {dados[arquivo].shape}")
    
    print()
    return dados


def carregar_scaler():
    """
    Carrega o scaler salvo na Fase 2.
    
    Retorna:
    --------
    MinMaxScaler
        Scaler ajustado
    """
    print(f"🔄 Carregando Scaler:")
    print(f"{'─'*70}\n")
    
    scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")
    scaler = joblib.load(scaler_path)
    
    print(f"   ✅ Scaler carregado: {scaler_path}")
    print(f"   📊 Range de normalização: {scaler.feature_range}\n")
    
    return scaler


# ===================================================================
# FUNÇÕES DE TREINAMENTO
# ===================================================================

def configurar_callbacks(model_path: str) -> list:
    """
    Configura callbacks para o treinamento.
    
    Parâmetros:
    -----------
    model_path : str
        Caminho para salvar o melhor modelo
        
    Retorna:
    --------
    list
        Lista de callbacks configurados
    """
    print(f"⚙️  Configurando Callbacks:")
    print(f"{'─'*70}\n")
    
    callbacks = []
    
    # Early Stopping
    early_stop = EarlyStopping(
        monitor='val_loss',
        patience=EARLY_STOPPING_PATIENCE,
        restore_best_weights=RESTORE_BEST_WEIGHTS,
        verbose=1,
        mode='min'
    )
    callbacks.append(early_stop)
    print(f"   ✅ Early Stopping configurado:")
    print(f"      • Monitor: val_loss")
    print(f"      • Paciência: {EARLY_STOPPING_PATIENCE} épocas")
    print(f"      • Restaurar melhores pesos: {RESTORE_BEST_WEIGHTS}\n")
    
    # Model Checkpoint
    checkpoint = ModelCheckpoint(
        filepath=model_path,
        monitor='val_loss',
        save_best_only=True,
        verbose=1,
        mode='min'
    )
    callbacks.append(checkpoint)
    print(f"   ✅ Model Checkpoint configurado:")
    print(f"      • Salvando em: {model_path}")
    print(f"      • Monitor: val_loss")
    print(f"      • Salvar apenas o melhor: True\n")
    
    # Reduce Learning Rate on Plateau
    reduce_lr = ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1,
        mode='min'
    )
    callbacks.append(reduce_lr)
    print(f"   ✅ Reduce LR on Plateau configurado:")
    print(f"      • Monitor: val_loss")
    print(f"      • Fator de redução: 0.5")
    print(f"      • Paciência: 5 épocas\n")
    
    return callbacks


def treinar_modelo(model: Sequential, dados: dict, callbacks: list) -> keras.callbacks.History:
    """
    Treina o modelo LSTM.
    
    Parâmetros:
    -----------
    model : Sequential
        Modelo compilado
    dados : dict
        Dicionário com dados de treino e validação
    callbacks : list
        Lista de callbacks
        
    Retorna:
    --------
    History
        Histórico do treinamento
    """
    print(f"🚀 Iniciando Treinamento:")
    print(f"{'─'*70}\n")
    
    print(f"   📊 Configurações:")
    print(f"      • Épocas: {EPOCHS}")
    print(f"      • Batch Size: {BATCH_SIZE}")
    print(f"      • Amostras de Treino: {len(dados['X_train'])}")
    print(f"      • Amostras de Validação: {len(dados['X_val'])}\n")
    
    print(f"{'─'*70}")
    print(f"Treinamento em andamento...\n")
    
    inicio = datetime.now()
    
    history = model.fit(
        dados['X_train'], 
        dados['y_train'],
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        validation_data=(dados['X_val'], dados['y_val']),
        callbacks=callbacks,
        verbose=VERBOSE
    )
    
    fim = datetime.now()
    duracao = (fim - inicio).total_seconds()
    
    print(f"\n{'─'*70}")
    print(f"✅ Treinamento Concluído!")
    print(f"   ⏱️  Duração: {duracao:.2f} segundos ({duracao/60:.2f} minutos)")
    print(f"   📈 Épocas executadas: {len(history.history['loss'])}\n")
    
    return history


# ===================================================================
# FUNÇÕES DE AVALIAÇÃO
# ===================================================================

def fazer_predicoes(model: Sequential, X_test: np.ndarray, 
                    scaler, feature_idx: int = 3) -> Tuple[np.ndarray, np.ndarray]:
    """
    Faz predições no conjunto de teste e inverte a escala.
    
    Parâmetros:
    -----------
    model : Sequential
        Modelo treinado
    X_test : np.ndarray
        Dados de teste
    scaler : MinMaxScaler
        Scaler para inverter normalização
    feature_idx : int
        Índice da feature Close (padrão: 3)
        
    Retorna:
    --------
    tuple
        (predições_escala_original, reais_escala_original)
    """
    print(f"🔮 Fazendo Predições:")
    print(f"{'─'*70}\n")
    
    # Predições normalizadas
    print(f"   📊 Predizendo em {len(X_test)} amostras...")
    predicoes_norm = model.predict(X_test, verbose=0)
    print(f"   ✅ Predições concluídas - Shape: {predicoes_norm.shape}\n")
    
    # Inverter escala das predições
    print(f"   🔄 Invertendo normalização...")
    
    # Criar array com todas as features (usar últimos valores de X_test)
    # e substituir apenas a coluna Close pelas predições
    ultima_sequencia = X_test[:, -1, :]  # Pegar último timestep de cada sequência
    
    # Criar cópia para predições
    predicoes_full = np.copy(ultima_sequencia)
    predicoes_full[:, feature_idx] = predicoes_norm.flatten()
    
    # Inverter escala
    predicoes_original = scaler.inverse_transform(predicoes_full)[:, feature_idx]
    
    print(f"   ✅ Escala invertida - Predições em valores originais\n")
    
    return predicoes_original, predicoes_norm


def calcular_metricas(y_true: np.ndarray, y_pred: np.ndarray, 
                      y_true_norm: np.ndarray, y_pred_norm: np.ndarray) -> dict:
    """
    Calcula métricas de desempenho.
    
    Parâmetros:
    -----------
    y_true : np.ndarray
        Valores reais (escala original)
    y_pred : np.ndarray
        Valores preditos (escala original)
    y_true_norm : np.ndarray
        Valores reais (normalizados)
    y_pred_norm : np.ndarray
        Valores preditos (normalizados)
        
    Retorna:
    --------
    dict
        Dicionário com métricas calculadas
    """
    print(f"📏 Calculando Métricas de Desempenho:")
    print(f"{'─'*70}\n")
    
    # Métricas em escala original
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    
    # Estatísticas dos dados
    preco_medio = np.mean(y_true)
    preco_min = np.min(y_true)
    preco_max = np.max(y_true)
    
    # Erro percentual em relação ao preço médio
    erro_pct_medio = (rmse / preco_medio) * 100
    
    print(f"   📊 Métricas em Escala Original (R$):")
    print(f"      • MSE (Mean Squared Error):     {mse:>12.4f}")
    print(f"      • RMSE (Root Mean Squared Error): {rmse:>10.4f}")
    print(f"      • MAE (Mean Absolute Error):    {mae:>12.4f}")
    print(f"      • MAPE (Mean Abs Percentage Error): {mape:>8.2f}%")
    print(f"      • R² Score:                     {r2:>12.4f}\n")
    
    print(f"   📈 Estatísticas dos Dados de Teste:")
    print(f"      • Preço Médio:   R$ {preco_medio:>10.2f}")
    print(f"      • Preço Mínimo:  R$ {preco_min:>10.2f}")
    print(f"      • Preço Máximo:  R$ {preco_max:>10.2f}\n")
    
    print(f"   🎯 Análise de Erro:")
    print(f"      • RMSE vs Preço Médio: {erro_pct_medio:.2f}%")
    
    if erro_pct_medio < 5:
        print(f"      • Avaliação: ✅ Excelente (< 5%)")
    elif erro_pct_medio < 10:
        print(f"      • Avaliação: ✅ Bom (5-10%)")
    elif erro_pct_medio < 15:
        print(f"      • Avaliação: ⚠️ Aceitável (10-15%)")
    else:
        print(f"      • Avaliação: ❌ Necessita melhorias (> 15%)")
    
    print()
    
    metricas = {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'mape': float(mape),
        'r2_score': float(r2),
        'preco_medio': float(preco_medio),
        'preco_min': float(preco_min),
        'preco_max': float(preco_max),
        'erro_pct_medio': float(erro_pct_medio)
    }
    
    return metricas


# ===================================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ===================================================================

def visualizar_curvas_aprendizado(history: keras.callbacks.History) -> None:
    """
    Visualiza curvas de aprendizado (loss e MAE).
    
    Parâmetros:
    -----------
    history : History
        Histórico do treinamento
    """
    print(f"📊 Gerando Curvas de Aprendizado:")
    print(f"{'─'*70}\n")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle('Curvas de Aprendizado - Treinamento LSTM', 
                 fontsize=16, fontweight='bold')
    
    # Loss
    ax1 = axes[0]
    ax1.plot(history.history['loss'], label='Treino', linewidth=2)
    ax1.plot(history.history['val_loss'], label='Validação', linewidth=2)
    ax1.set_title('Função de Perda (MSE)', fontweight='bold', fontsize=12)
    ax1.set_xlabel('Época')
    ax1.set_ylabel('Loss (MSE)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # MAE
    ax2 = axes[1]
    ax2.plot(history.history['mae'], label='Treino', linewidth=2)
    ax2.plot(history.history['val_mae'], label='Validação', linewidth=2)
    ax2.set_title('Erro Absoluto Médio (MAE)', fontweight='bold', fontsize=12)
    ax2.set_xlabel('Época')
    ax2.set_ylabel('MAE')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar
    plot_path = os.path.join(DOCS_DIR, 'curvas_aprendizado.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"   💾 Curvas salvas: {plot_path}\n")
    
    plt.close()


def visualizar_predicoes(y_true: np.ndarray, y_pred: np.ndarray, 
                        metricas: dict) -> None:
    """
    Visualiza predições vs valores reais.
    
    Parâmetros:
    -----------
    y_true : np.ndarray
        Valores reais
    y_pred : np.ndarray
        Valores preditos
    metricas : dict
        Métricas calculadas
    """
    print(f"📈 Gerando Gráfico de Predições:")
    print(f"{'─'*70}\n")
    
    fig, axes = plt.subplots(2, 1, figsize=(15, 10))
    fig.suptitle('Avaliação do Modelo LSTM - B3SA3.SA', 
                 fontsize=16, fontweight='bold')
    
    # Gráfico 1: Série temporal
    ax1 = axes[0]
    indices = np.arange(len(y_true))
    
    ax1.plot(indices, y_true, label='Preço Real', 
             linewidth=2, alpha=0.7, color='blue')
    ax1.plot(indices, y_pred, label='Preço Previsto', 
             linewidth=2, alpha=0.7, color='red')
    
    ax1.set_title('Comparação: Preço Real vs Previsto (Conjunto de Teste)', 
                  fontweight='bold', fontsize=12)
    ax1.set_xlabel('Amostras (Dias)')
    ax1.set_ylabel('Preço de Fechamento (R$)')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Adicionar métricas no gráfico
    textstr = f'RMSE: R$ {metricas["rmse"]:.2f}\nMAE: R$ {metricas["mae"]:.2f}\nMAPE: {metricas["mape"]:.2f}%\nR²: {metricas["r2_score"]:.4f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax1.text(0.02, 0.98, textstr, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    # Gráfico 2: Scatter plot
    ax2 = axes[1]
    ax2.scatter(y_true, y_pred, alpha=0.5, s=30)
    
    # Linha de identidade (predição perfeita)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax2.plot([min_val, max_val], [min_val, max_val], 
             'r--', linewidth=2, label='Predição Perfeita')
    
    ax2.set_title('Dispersão: Valores Reais vs Previstos', 
                  fontweight='bold', fontsize=12)
    ax2.set_xlabel('Preço Real (R$)')
    ax2.set_ylabel('Preço Previsto (R$)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar
    plot_path = os.path.join(DOCS_DIR, 'resultado_teste.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"   💾 Gráfico salvo: {plot_path}\n")
    
    plt.close()


# ===================================================================
# FUNÇÕES DE PERSISTÊNCIA
# ===================================================================

def salvar_resultados(history: keras.callbacks.History, metricas: dict) -> None:
    """
    Salva resultados do treinamento e avaliação.
    
    Parâmetros:
    -----------
    history : History
        Histórico do treinamento
    metricas : dict
        Métricas calculadas
    """
    print(f"💾 Salvando Resultados:")
    print(f"{'─'*70}\n")
    
    # Preparar dados do histórico
    historico = {
        'loss': [float(x) for x in history.history['loss']],
        'val_loss': [float(x) for x in history.history['val_loss']],
        'mae': [float(x) for x in history.history['mae']],
        'val_mae': [float(x) for x in history.history['val_mae']],
        'epocas': len(history.history['loss'])
    }
    
    # Criar log completo
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'treinamento': {
            'epocas_configuradas': EPOCHS,
            'epocas_executadas': historico['epocas'],
            'batch_size': BATCH_SIZE,
            'early_stopping_patience': EARLY_STOPPING_PATIENCE,
            'final_train_loss': historico['loss'][-1],
            'final_val_loss': historico['val_loss'][-1],
            'final_train_mae': historico['mae'][-1],
            'final_val_mae': historico['val_mae'][-1],
            'best_val_loss': float(min(historico['val_loss'])),
            'best_epoch': int(np.argmin(historico['val_loss']) + 1)
        },
        'metricas_teste': metricas,
        'historico': historico,
        'interpretacao': interpretar_resultados(metricas, historico)
    }
    
    # Salvar JSON
    log_path = os.path.join(DOCS_DIR, 'training_results.json')
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)
    
    tamanho_kb = os.path.getsize(log_path) / 1024
    print(f"   ✅ Resultados salvos: {log_path} ({tamanho_kb:.2f} KB)\n")


def interpretar_resultados(metricas: dict, historico: dict) -> dict:
    """
    Interpreta resultados e gera análise qualitativa.
    
    Parâmetros:
    -----------
    metricas : dict
        Métricas calculadas
    historico : dict
        Histórico do treinamento
        
    Retorna:
    --------
    dict
        Interpretação dos resultados
    """
    interpretacao = {}
    
    # Avaliar qualidade do modelo
    erro_pct = metricas['erro_pct_medio']
    
    if erro_pct < 5:
        interpretacao['qualidade'] = 'Excelente'
        interpretacao['comentario'] = 'O modelo apresenta erro muito baixo em relação ao preço médio.'
    elif erro_pct < 10:
        interpretacao['qualidade'] = 'Boa'
        interpretacao['comentario'] = 'O modelo apresenta erro aceitável e bom desempenho preditivo.'
    elif erro_pct < 15:
        interpretacao['qualidade'] = 'Aceitável'
        interpretacao['comentario'] = 'O modelo funciona mas pode ser melhorado com ajustes.'
    else:
        interpretacao['qualidade'] = 'Requer melhorias'
        interpretacao['comentario'] = 'O modelo precisa de ajustes significativos na arquitetura ou dados.'
    
    # Avaliar overfitting
    val_loss = historico['val_loss']
    train_loss = historico['loss']
    
    gap_final = val_loss[-1] - train_loss[-1]
    gap_pct = (gap_final / train_loss[-1]) * 100
    
    if gap_pct < 10:
        interpretacao['overfitting'] = 'Não detectado'
    elif gap_pct < 30:
        interpretacao['overfitting'] = 'Leve'
    else:
        interpretacao['overfitting'] = 'Moderado a Alto'
    
    # Avaliar R²
    r2 = metricas['r2_score']
    
    if r2 > 0.9:
        interpretacao['capacidade_explicativa'] = 'Excelente (R² > 0.9)'
    elif r2 > 0.7:
        interpretacao['capacidade_explicativa'] = 'Boa (R² > 0.7)'
    elif r2 > 0.5:
        interpretacao['capacidade_explicativa'] = 'Moderada (R² > 0.5)'
    else:
        interpretacao['capacidade_explicativa'] = 'Baixa (R² < 0.5)'
    
    return interpretacao


# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """
    Função principal que executa todo o pipeline de treinamento e avaliação.
    """
    try:
        # 1. Carregar dados e scaler
        dados = carregar_dados_preparados()
        scaler = carregar_scaler()
        
        # 2. Construir e compilar modelo
        model = construir_modelo_lstm()
        model = compilar_modelo(model)
        
        # 3. Configurar callbacks
        model_path = os.path.join(MODELS_DIR, 'lstm_model_best.h5')
        callbacks = configurar_callbacks(model_path)
        
        # 4. Treinar modelo
        history = treinar_modelo(model, dados, callbacks)
        
        # 5. Carregar melhor modelo
        print(f"📥 Carregando Melhor Modelo:")
        print(f"{'─'*70}\n")
        print(f"   Carregando: {model_path}")
        model = keras.models.load_model(model_path)
        print(f"   ✅ Melhor modelo carregado\n")
        
        # 6. Fazer predições
        y_pred_original, y_pred_norm = fazer_predicoes(model, dados['X_test'], scaler)
        
        # Inverter escala dos valores reais de teste
        # Pegar último timestep de cada sequência
        ultima_sequencia_test = dados['X_test'][:, -1, :]
        y_test_full = scaler.inverse_transform(ultima_sequencia_test)
        y_test_original = y_test_full[:, 3]  # Índice 3 = Close
        
        # 7. Calcular métricas
        metricas = calcular_metricas(y_test_original, y_pred_original,
                                     dados['y_test'], y_pred_norm)
        
        # 8. Visualizar resultados
        visualizar_curvas_aprendizado(history)
        visualizar_predicoes(y_test_original, y_pred_original, metricas)
        
        # 9. Salvar resultados
        salvar_resultados(history, metricas)
        
        # 10. Exibir resumo final
        print(f"{'='*70}")
        print(f"✅ FASE 4 CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        print(f"📁 Arquivos gerados:")
        print(f"   → models/lstm_model_best.h5")
        print(f"   → docs/training/training_results.json")
        print(f"   → docs/training/curvas_aprendizado.png")
        print(f"   → docs/training/resultado_teste.png")
        print(f"\n📊 Resumo de Desempenho:")
        print(f"   → RMSE: R$ {metricas['rmse']:.2f}")
        print(f"   → MAE:  R$ {metricas['mae']:.2f}")
        print(f"   → MAPE: {metricas['mape']:.2f}%")
        print(f"   → R² Score: {metricas['r2_score']:.4f}")
        print(f"\n🎯 Próximos passos:")
        print(f"   → Análise detalhada dos resultados")
        print(f"   → Ajuste de hiperparâmetros se necessário")
        print(f"   → Preparação para deploy (Fase 5)\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERRO NA FASE 4: {str(e)}")
        print(f"{'='*70}\n")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
