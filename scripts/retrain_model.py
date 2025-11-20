"""
Script de Re-treino Automático do Modelo LSTM

Baixa dados atualizados do Yahoo Finance, treina novo modelo
e compara com modelo existente antes de substituir.

Uso:
    python scripts/retrain_model.py [--dry-run] [--force]
"""

import sys
import os
from pathlib import Path
import argparse
import json
from datetime import datetime
import shutil

# Adicionar src ao path
ROOT_DIR = Path(__file__).parent.parent
sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Imports do projeto
from src.data_collection import coletar_dados_historicos
from src.data_preparation import (
    normalizar_dados,
    criar_sequencias,
    dividir_dados,
    salvar_dados_preparados
)
from src.model_training import construir_modelo_lstm, treinar_modelo


def calcular_metricas(y_true, y_pred):
    """Calcula métricas de avaliação"""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
    r2 = r2_score(y_true, y_pred)
    
    return {
        'MAE': round(float(mae), 4),
        'RMSE': round(float(rmse), 4),
        'MAPE': round(float(mape), 2),
        'R2': round(float(r2), 4)
    }


def backup_modelo_atual(models_dir):
    """Faz backup do modelo atual"""
    modelo_path = models_dir / "lstm_model_best.h5"
    scaler_path = models_dir / "scaler.pkl"
    
    if modelo_path.exists():
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = models_dir / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        shutil.copy2(modelo_path, backup_dir / f"lstm_model_{timestamp}.h5")
        shutil.copy2(scaler_path, backup_dir / f"scaler_{timestamp}.pkl")
        
        print(f"✅ Backup criado: {timestamp}")
        return timestamp
    
    return None


def carregar_metricas_antigas(models_dir):
    """Carrega métricas do modelo atual"""
    metrics_file = models_dir / "model_metrics.json"
    
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            return json.load(f)
    
    return None


def salvar_metricas(metricas, models_dir):
    """Salva métricas do modelo"""
    metrics_file = models_dir / "model_metrics.json"
    
    metricas['timestamp'] = datetime.now().isoformat()
    
    with open(metrics_file, 'w') as f:
        json.dump(metricas, f, indent=2)
    
    print(f"✅ Métricas salvas em {metrics_file}")


def comparar_modelos(metricas_antigas, metricas_novas):
    """
    Compara métricas e decide se novo modelo é melhor
    
    Critérios:
    - MAPE deve ser <= antigo (ou no máximo 10% pior)
    - R2 deve ser >= antigo (ou no máximo 5% pior)
    """
    if not metricas_antigas:
        print("⚠️  Sem métricas antigas - novo modelo será aceito")
        return True
    
    mape_old = metricas_antigas.get('MAPE', 100)
    mape_new = metricas_novas['MAPE']
    r2_old = metricas_antigas.get('R2', 0)
    r2_new = metricas_novas['R2']
    
    # Tolerância de 10% piora no MAPE
    mape_ok = mape_new <= mape_old * 1.1
    
    # Tolerância de 5% piora no R2
    r2_ok = r2_new >= r2_old * 0.95
    
    print("\n📊 Comparação de Métricas:")
    print(f"   MAPE: {mape_old:.2f}% → {mape_new:.2f}% {'✅' if mape_ok else '❌'}")
    print(f"   R²:   {r2_old:.4f} → {r2_new:.4f} {'✅' if r2_ok else '❌'}")
    
    return mape_ok and r2_ok


def main():
    parser = argparse.ArgumentParser(description='Re-treinar modelo LSTM')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Apenas treina mas não substitui modelo')
    parser.add_argument('--force', action='store_true',
                       help='Força substituição mesmo se métricas piores')
    parser.add_argument('--ticker', default='B3SA3.SA',
                       help='Ticker para treinar (padrão: B3SA3.SA)')
    parser.add_argument('--years', type=int, default=5,
                       help='Anos de histórico (padrão: 5)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔄 SCRIPT DE RE-TREINO AUTOMÁTICO")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📈 Ticker: {args.ticker}")
    print(f"📊 Período: {args.years} anos")
    print(f"🧪 Dry Run: {'Sim' if args.dry_run else 'Não'}")
    print("=" * 60)
    
    # Diretórios
    data_dir = ROOT_DIR / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    models_dir = ROOT_DIR / "models"
    
    raw_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    
    try:
        # 1. Coletar dados atualizados
        print("\n📥 ETAPA 1: Coletando dados atualizados...")
        df = coletar_dados_historicos(
            ticker=args.ticker,
            anos=args.years
        )
        
        # Salvar dados coletados
        raw_file = raw_dir / f"{args.ticker}_atualizado.csv"
        df.to_csv(raw_file)
        print(f"✅ {len(df)} dias de dados coletados e salvos em {raw_file}")
        
        # 2. Preparar dados para LSTM
        print("\n🔧 ETAPA 2: Preparando dados para LSTM...")
        
        # Features a serem usadas
        features = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        # Normalizar dados
        print("   📊 Normalizando dados...")
        dados_normalizados, scaler = normalizar_dados(df, features)
        
        # Criar sequências
        print("   🔨 Criando sequências temporais...")
        close_idx = features.index('Close')
        X, y = criar_sequencias(
            dados=dados_normalizados,
            timesteps=60,  # window_size
            target_idx=close_idx
        )
        
        # Dividir dados
        print("   ✂️  Dividindo dados (70% treino, 15% val, 15% teste)...")
        dados_divididos = dividir_dados(
            X=X,
            y=y,
            train_pct=0.70,
            val_pct=0.15,
            test_pct=0.15
        )
        
        # Salvar dados preparados
        print("   💾 Salvando dados preparados...")
        salvar_dados_preparados(dados_divididos, scaler)
        
        print("✅ Dados preparados com sucesso!")
        
        # 3. Carregar dados preparados
        print("\n📂 ETAPA 3: Carregando dados de treinamento...")
        X_train = dados_divididos['X_train']
        y_train = dados_divididos['y_train']
        X_val = dados_divididos['X_val']
        y_val = dados_divididos['y_val']
        X_test = dados_divididos['X_test']
        y_test = dados_divididos['y_test']
        
        print(f"   Treino: {X_train.shape[0]} sequências")
        print(f"   Validação: {X_val.shape[0]} sequências")
        print(f"   Teste: {X_test.shape[0]} sequências")
        
        # 4. Construir e treinar modelo
        print("\n🧠 ETAPA 4: Treinando novo modelo LSTM...")
        input_shape = (X_train.shape[1], X_train.shape[2])
        modelo = construir_modelo_lstm(input_shape)
        
        historico, modelo_treinado = treinar_modelo(
            modelo,
            X_train, y_train,
            X_val, y_val,
            epochs=50,
            batch_size=32,
            save_dir=str(models_dir / "temp")
        )
        print("✅ Modelo treinado")
        
        # 5. Avaliar no conjunto de teste
        print("\n📊 ETAPA 5: Avaliando modelo no conjunto de teste...")
        y_pred = modelo_treinado.predict(X_test, verbose=0)
        
        # Desnormalizar previsões
        import joblib
        scaler = joblib.load(processed_dir / "scaler.pkl")
        
        # Criar array dummy para desnormalizar apenas Close
        dummy_train = np.zeros((len(y_test), 5))
        dummy_train[:, 3] = y_test.flatten()
        y_test_real = scaler.inverse_transform(dummy_train)[:, 3]
        
        dummy_pred = np.zeros((len(y_pred), 5))
        dummy_pred[:, 3] = y_pred.flatten()
        y_pred_real = scaler.inverse_transform(dummy_pred)[:, 3]
        
        # Calcular métricas
        metricas_novas = calcular_metricas(y_test_real, y_pred_real)
        
        print("\n📈 Métricas do Novo Modelo:")
        print(f"   MAE:  R$ {metricas_novas['MAE']:.4f}")
        print(f"   RMSE: R$ {metricas_novas['RMSE']:.4f}")
        print(f"   MAPE: {metricas_novas['MAPE']:.2f}%")
        print(f"   R²:   {metricas_novas['R2']:.4f}")
        
        # 6. Comparar com modelo antigo
        print("\n🔍 ETAPA 6: Comparando com modelo existente...")
        metricas_antigas = carregar_metricas_antigas(models_dir)
        
        if metricas_antigas:
            print("\n📊 Métricas do Modelo Atual:")
            print(f"   MAE:  R$ {metricas_antigas.get('MAE', 'N/A')}")
            print(f"   RMSE: R$ {metricas_antigas.get('RMSE', 'N/A')}")
            print(f"   MAPE: {metricas_antigas.get('MAPE', 'N/A')}%")
            print(f"   R²:   {metricas_antigas.get('R2', 'N/A')}")
        
        substituir = comparar_modelos(metricas_antigas, metricas_novas)
        
        # 7. Decidir substituição
        if args.dry_run:
            print("\n🧪 DRY RUN: Modelo não será substituído")
            print("   Para substituir, execute sem --dry-run")
            return 0
        
        if not substituir and not args.force:
            print("\n⚠️  MODELO NÃO APROVADO:")
            print("   Métricas do novo modelo são piores que o atual")
            print("   Modelo antigo será mantido")
            print("   Use --force para forçar substituição")
            return 1
        
        if args.force and not substituir:
            print("\n⚠️  FORÇANDO SUBSTITUIÇÃO (--force ativado)")
        
        # 8. Fazer backup e substituir
        print("\n💾 ETAPA 7: Substituindo modelo...")
        backup_timestamp = backup_modelo_atual(models_dir)
        
        # Copiar novo modelo
        temp_model = models_dir / "temp" / "lstm_model_best.h5"
        final_model = models_dir / "lstm_model_best.h5"
        
        shutil.copy2(temp_model, final_model)
        shutil.copy2(processed_dir / "scaler.pkl", models_dir / "scaler.pkl")
        
        # Salvar métricas
        salvar_metricas(metricas_novas, models_dir)
        
        # Limpar temporários
        shutil.rmtree(models_dir / "temp")
        
        print("\n✅ MODELO ATUALIZADO COM SUCESSO!")
        print(f"   Backup anterior: backups/lstm_model_{backup_timestamp}.h5")
        print(f"   Novo modelo: {final_model}")
        
        # 9. Resumo
        print("\n" + "=" * 60)
        print("📊 RESUMO DO RE-TREINO")
        print("=" * 60)
        print(f"✅ Dados: {len(df)} dias coletados")
        print(f"✅ Modelo: Treinado com sucesso")
        print(f"✅ MAPE: {metricas_novas['MAPE']:.2f}%")
        print(f"✅ R²: {metricas_novas['R2']:.4f}")
        print(f"✅ Backup: Criado")
        print(f"✅ Status: Modelo em produção atualizado")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO durante re-treino:")
        print(f"   {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
