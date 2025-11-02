"""
===================================================================
PredictFinance - Módulo de Coleta de Dados
Coleta de dados históricos da ação B3SA3.SA via Yahoo Finance
===================================================================

Este módulo é responsável pela Fase 1 do projeto:
- Obtenção de dados históricos da B3 S.A. (B3SA3.SA)
- Limpeza e tratamento de dados
- Análise exploratória inicial
- Salvamento dos dados processados

Autor: ArgusPortal
Data: 02/11/2025
Versão: 1.0.0
"""

import os
import json
from datetime import datetime, timedelta
from typing import Tuple, Dict
import warnings

import yfinance as yf
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# ===================================================================
# CONFIGURAÇÕES
# ===================================================================

TICKER = "B3SA3.SA"
YEARS_OF_DATA = 5
DATA_DIR = "data/raw"
DOCS_DIR = "docs/data_collection"
OUTPUT_FILE = os.path.join(DATA_DIR, "b3sa3_historical.csv")
LOG_FILE = os.path.join(DOCS_DIR, "data_collection_log.json")

# Criar diretórios se não existirem
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Configuração de visualizações
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ===================================================================
# FUNÇÕES AUXILIARES
# ===================================================================

def coletar_dados_historicos(ticker: str, anos: int) -> pd.DataFrame:
    """
    Coleta dados históricos do Yahoo Finance.
    
    Parâmetros:
    -----------
    ticker : str
        Código da ação (ex: B3SA3.SA)
    anos : int
        Número de anos de histórico a coletar
        
    Retorna:
    --------
    pd.DataFrame
        DataFrame com dados históricos (OHLCV)
    """
    print(f"\n{'='*70}")
    print(f"FASE 1: COLETA DE DADOS - {ticker}")
    print(f"{'='*70}\n")
    
    # Calcular datas
    data_fim = datetime.now()
    data_inicio = data_fim - timedelta(days=anos*365)
    
    print(f"📅 Período de coleta:")
    print(f"   Início: {data_inicio.strftime('%Y-%m-%d')}")
    print(f"   Fim:    {data_fim.strftime('%Y-%m-%d')}\n")
    
    print(f"📡 Conectando ao Yahoo Finance...")
    
    try:
        # Download dos dados
        dados = yf.download(
            ticker,
            start=data_inicio,
            end=data_fim,
            progress=False
        )
        
        # Remover MultiIndex se houver (quando temos apenas um ticker)
        if isinstance(dados.columns, pd.MultiIndex):
            dados.columns = dados.columns.droplevel(1)
        
        if dados.empty:
            raise ValueError(f"Nenhum dado encontrado para {ticker}")
        
        print(f"✅ Dados coletados com sucesso!")
        print(f"   Total de registros: {len(dados)}")
        print(f"   Período efetivo: {dados.index[0].strftime('%Y-%m-%d')} a {dados.index[-1].strftime('%Y-%m-%d')}\n")
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao coletar dados: {str(e)}")
        raise


def analisar_dados_faltantes(df: pd.DataFrame) -> Dict:
    """
    Analisa e trata valores ausentes no DataFrame.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame a ser analisado
        
    Retorna:
    --------
    dict
        Estatísticas sobre dados faltantes
    """
    print(f"🔍 Análise de Dados Faltantes:")
    print(f"{'─'*70}\n")
    
    # Contagem de valores ausentes
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    
    missing_info = {}
    
    for col in df.columns:
        if missing[col] > 0:
            print(f"   ⚠️  {col}: {missing[col]} valores ({missing_pct[col]:.2f}%)")
            missing_info[col] = {
                'count': int(missing[col]),
                'percentage': float(missing_pct[col])
            }
        else:
            print(f"   ✅ {col}: Sem valores faltantes")
            missing_info[col] = {
                'count': 0,
                'percentage': 0.0
            }
    
    print()
    return missing_info


def detectar_outliers(df: pd.DataFrame, coluna: str, threshold: float = 3.0) -> Tuple[pd.Series, int]:
    """
    Detecta outliers usando o método Z-score.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame com os dados
    coluna : str
        Nome da coluna a analisar
    threshold : float
        Limite de desvios padrão para considerar outlier
        
    Retorna:
    --------
    tuple
        (Série booleana com outliers, número de outliers)
    """
    z_scores = np.abs(stats.zscore(df[coluna].dropna()))
    outliers = z_scores > threshold
    
    return outliers, outliers.sum()


def limpar_dados(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """
    Realiza limpeza completa dos dados.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame bruto
        
    Retorna:
    --------
    tuple
        (DataFrame limpo, estatísticas de limpeza)
    """
    print(f"🧹 Limpeza de Dados:")
    print(f"{'─'*70}\n")
    
    df_limpo = df.copy()
    stats_limpeza = {}
    
    # 1. Remover duplicatas
    duplicatas_antes = len(df_limpo)
    df_limpo = df_limpo[~df_limpo.index.duplicated(keep='first')]
    duplicatas_removidas = duplicatas_antes - len(df_limpo)
    print(f"   🗑️  Duplicatas removidas: {duplicatas_removidas}")
    stats_limpeza['duplicatas_removidas'] = duplicatas_removidas
    
    # 2. Tratar valores ausentes
    missing_antes = df_limpo.isnull().sum().sum()
    
    # Forward fill para gaps curtos (máximo 3 dias)
    df_limpo = df_limpo.fillna(method='ffill', limit=3)
    
    # Remover linhas com valores ainda ausentes
    df_limpo = df_limpo.dropna()
    
    missing_tratados = missing_antes - df_limpo.isnull().sum().sum()
    print(f"   📝 Valores ausentes tratados: {missing_tratados}")
    stats_limpeza['missing_tratados'] = missing_tratados
    
    # 3. Validar consistência de preços
    inconsistencias = 0
    
    # Low deve ser <= High
    mask_low_high = df_limpo['Low'] > df_limpo['High']
    inconsistencias += mask_low_high.sum()
    
    # Open e Close devem estar entre Low e High
    mask_open = (df_limpo['Open'] < df_limpo['Low']) | (df_limpo['Open'] > df_limpo['High'])
    inconsistencias += mask_open.sum()
    
    mask_close = (df_limpo['Close'] < df_limpo['Low']) | (df_limpo['Close'] > df_limpo['High'])
    inconsistencias += mask_close.sum()
    
    print(f"   ⚖️  Inconsistências detectadas: {inconsistencias}")
    stats_limpeza['inconsistencias'] = inconsistencias
    
    # 4. Detectar outliers no preço de fechamento
    outliers, num_outliers = detectar_outliers(df_limpo, 'Close', threshold=3.0)
    print(f"   📊 Outliers detectados (Close): {num_outliers}")
    stats_limpeza['outliers_detectados'] = num_outliers
    
    # 5. Garantir valores positivos
    valores_negativos = (df_limpo[['Open', 'High', 'Low', 'Close', 'Volume']] <= 0).sum().sum()
    print(f"   ➕ Valores não-positivos: {valores_negativos}")
    stats_limpeza['valores_negativos'] = valores_negativos
    
    print(f"\n   ✅ Dados limpos: {len(df_limpo)} registros válidos\n")
    stats_limpeza['registros_finais'] = len(df_limpo)
    
    return df_limpo, stats_limpeza


def realizar_analise_exploratoria(df: pd.DataFrame) -> None:
    """
    Realiza análise exploratória dos dados e gera visualizações.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame com dados limpos
    """
    print(f"📊 Análise Exploratória:")
    print(f"{'─'*70}\n")
    
    # Estatísticas descritivas
    print("   📈 Estatísticas Descritivas do Preço de Fechamento:")
    stats_close = df['Close'].describe()
    for stat, valor in stats_close.items():
        print(f"      {stat:8s}: R$ {float(valor):,.2f}")
    print()
    
    # Criar figura com múltiplos gráficos
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'Análise Exploratória - {TICKER}', fontsize=16, fontweight='bold')
    
    # 1. Série temporal do preço de fechamento
    ax1 = axes[0, 0]
    ax1.plot(df.index, df['Close'], linewidth=1.5, color='#2E86AB')
    ax1.set_title('Série Temporal - Preço de Fechamento', fontweight='bold')
    ax1.set_xlabel('Data')
    ax1.set_ylabel('Preço (R$)')
    ax1.grid(True, alpha=0.3)
    
    # 2. Distribuição do preço de fechamento
    ax2 = axes[0, 1]
    ax2.hist(df['Close'], bins=50, color='#A23B72', alpha=0.7, edgecolor='black')
    ax2.set_title('Distribuição - Preço de Fechamento', fontweight='bold')
    ax2.set_xlabel('Preço (R$)')
    ax2.set_ylabel('Frequência')
    ax2.grid(True, alpha=0.3)
    
    # 3. Volume de negociação
    ax3 = axes[1, 0]
    ax3.bar(df.index, df['Volume'], width=1, color='#F18F01', alpha=0.6)
    ax3.set_title('Volume de Negociação', fontweight='bold')
    ax3.set_xlabel('Data')
    ax3.set_ylabel('Volume')
    ax3.grid(True, alpha=0.3)
    
    # 4. Boxplot de preços
    ax4 = axes[1, 1]
    box_data = [df['Open'], df['High'], df['Low'], df['Close']]
    ax4.boxplot(box_data, labels=['Open', 'High', 'Low', 'Close'])
    ax4.set_title('Boxplot - Preços OHLC', fontweight='bold')
    ax4.set_ylabel('Preço (R$)')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Salvar gráfico
    plot_path = os.path.join(DOCS_DIR, 'analise_exploratoria.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"   💾 Gráficos salvos em: {plot_path}\n")
    
    plt.close()
    
    # Matriz de correlação
    print("   🔗 Matriz de Correlação:")
    corr_matrix = df[['Open', 'High', 'Low', 'Close', 'Volume']].corr()
    print(corr_matrix.round(3))
    print()
    
    # Salvar matriz de correlação
    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.3f', cmap='coolwarm', 
                center=0, square=True, linewidths=1, ax=ax_corr)
    ax_corr.set_title('Matriz de Correlação - Features', fontweight='bold', fontsize=14)
    
    corr_path = os.path.join(DOCS_DIR, 'matriz_correlacao.png')
    plt.savefig(corr_path, dpi=300, bbox_inches='tight')
    print(f"   💾 Matriz de correlação salva em: {corr_path}\n")
    
    plt.close()


def salvar_dados_e_log(df: pd.DataFrame, stats: Dict) -> None:
    """
    Salva dados limpos e log de execução.
    
    Parâmetros:
    -----------
    df : pd.DataFrame
        DataFrame limpo a salvar
    stats : dict
        Estatísticas da coleta e limpeza
    """
    print(f"💾 Salvando Resultados:")
    print(f"{'─'*70}\n")
    
    # Salvar CSV
    df.to_csv(OUTPUT_FILE)
    print(f"   ✅ Dados salvos em: {OUTPUT_FILE}")
    print(f"      Tamanho: {os.path.getsize(OUTPUT_FILE) / 1024:.2f} KB")
    print(f"      Registros: {len(df)}")
    print(f"      Colunas: {list(df.columns)}\n")
    
    # Converter stats para tipos Python nativos
    def converter_para_json(obj):
        """Converte tipos numpy para tipos Python nativos"""
        if isinstance(obj, dict):
            return {k: converter_para_json(v) for k, v in obj.items()}
        elif isinstance(obj, (np.integer, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    # Criar log de execução
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'ticker': TICKER,
        'periodo': {
            'inicio': df.index[0].strftime('%Y-%m-%d'),
            'fim': df.index[-1].strftime('%Y-%m-%d'),
            'dias_totais': int(len(df))
        },
        'estatisticas_limpeza': converter_para_json(stats),
        'estatisticas_dados': {
            'preco_medio': float(df['Close'].mean()),
            'preco_minimo': float(df['Close'].min()),
            'preco_maximo': float(df['Close'].max()),
            'preco_atual': float(df['Close'].iloc[-1]),
            'volume_medio': float(df['Volume'].mean())
        },
        'colunas': list(df.columns),
        'output_file': OUTPUT_FILE
    }
    
    # Salvar log em JSON
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=4, ensure_ascii=False)
    
    print(f"   ✅ Log salvo em: {LOG_FILE}\n")


# ===================================================================
# FUNÇÃO PRINCIPAL
# ===================================================================

def main():
    """
    Função principal que executa todo o pipeline de coleta e limpeza.
    """
    try:
        # 1. Coletar dados
        dados_brutos = coletar_dados_historicos(TICKER, YEARS_OF_DATA)
        
        # 2. Analisar dados faltantes
        analisar_dados_faltantes(dados_brutos)
        
        # 3. Limpar dados
        dados_limpos, stats_limpeza = limpar_dados(dados_brutos)
        
        # 4. Análise exploratória
        realizar_analise_exploratoria(dados_limpos)
        
        # 5. Salvar resultados
        salvar_dados_e_log(dados_limpos, stats_limpeza)
        
        print(f"{'='*70}")
        print(f"✅ FASE 1 CONCLUÍDA COM SUCESSO!")
        print(f"{'='*70}\n")
        print(f"📁 Próximos passos:")
        print(f"   → Execute: python src/data_preparation.py")
        print(f"   → Para preparar os dados para o modelo LSTM\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"❌ ERRO NA FASE 1: {str(e)}")
        print(f"{'='*70}\n")
        raise


if __name__ == "__main__":
    main()
