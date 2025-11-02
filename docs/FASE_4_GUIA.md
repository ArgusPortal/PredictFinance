# Guia de Execução - Fase 4: Treinamento e Avaliação do Modelo

## 📋 Objetivo da Fase 4

Treinar o modelo LSTM com os dados preparados, utilizando técnicas de Early Stopping e Model Checkpoint, avaliar o desempenho em dados de teste, calcular métricas de performance (RMSE, MAE, MAPE, R²) e gerar visualizações dos resultados.

---

## 🔧 Pré-requisitos

### 1. Fases Anteriores Concluídas

Certifique-se de que as fases anteriores foram executadas com sucesso:

```bash
# Verificar dados preparados (Fase 2)
ls data/processed/X_train.npy
ls data/processed/y_train.npy
ls data/processed/X_val.npy
ls data/processed/y_val.npy
ls data/processed/X_test.npy
ls data/processed/y_test.npy

# Verificar scaler (Fase 2)
ls models/scaler.pkl
```

### 2. Dependências Instaladas
As bibliotecas necessárias já devem estar instaladas do requirements.txt:
- tensorflow/keras
- numpy
- scikit-learn
- matplotlib
- seaborn
- joblib

---

## 🚀 Executar Fase 4

### Comando de Execução
```bash
python src/model_training.py
```

### Tempo Estimado
- **CPU**: 1-3 minutos
- **GPU**: 30-60 segundos

---

## 📤 Saídas Esperadas

Após a execução bem-sucedida, os seguintes arquivos serão criados:

### 1. Modelo Treinado
**Localização**: `models/lstm_model_best.h5`
- **Formato**: HDF5 (Keras)
- **Conteúdo**: Arquitetura + Pesos + Configuração de compilação
- **Tamanho**: ~0.4 MB
- **Descrição**: Melhor modelo salvo durante o treinamento (menor val_loss)

### 2. Resultados do Treinamento
**Localização**: `docs/training/training_results.json`
- **Conteúdo**:
  - Configurações de treinamento (épocas, batch_size)
  - Histórico de loss e métricas por época
  - Métricas finais no conjunto de teste
  - Interpretação dos resultados
- **Tamanho**: ~8 KB

### 3. Curvas de Aprendizado
**Localização**: `docs/training/curvas_aprendizado.png`
- **Conteúdo**: Gráfico com 2 painéis
  - Painel 1: Loss (MSE) por época (treino vs validação)
  - Painel 2: MAE por época (treino vs validação)
- **Formato**: PNG (alta resolução: 300 DPI)
- **Tamanho**: ~100-200 KB

### 4. Gráfico de Predições
**Localização**: `docs/training/resultado_teste.png`
- **Conteúdo**: Gráfico com 2 painéis
  - Painel 1: Série temporal (Preço Real vs Previsto)
  - Painel 2: Scatter plot (correlação entre real e previsto)
- **Formato**: PNG (alta resolução: 300 DPI)
- **Tamanho**: ~150-250 KB

---

## 📊 Configurações de Treinamento

### Hiperparâmetros

| Parâmetro | Valor | Descrição |
|-----------|-------|-----------|
| **Épocas** | 50 | Número máximo de épocas |
| **Batch Size** | 32 | Amostras processadas por iteração |
| **Otimizador** | Adam | Taxa de aprendizado adaptativa |
| **Learning Rate** | 0.001 | Taxa de aprendizado inicial |
| **Loss Function** | MSE | Mean Squared Error |
| **Métrica** | MAE | Mean Absolute Error |

### Callbacks Configurados

#### 1. Early Stopping
- **Monitor**: val_loss
- **Paciência**: 10 épocas
- **Modo**: min (minimizar val_loss)
- **Restaurar Melhores Pesos**: True
- **Função**: Interrompe treinamento se val_loss não melhorar

#### 2. Model Checkpoint
- **Monitor**: val_loss
- **Modo**: min
- **Salvar Apenas o Melhor**: True
- **Arquivo**: models/lstm_model_best.h5
- **Função**: Salva modelo quando val_loss melhora

#### 3. Reduce Learning Rate on Plateau
- **Monitor**: val_loss
- **Fator**: 0.5 (reduz LR pela metade)
- **Paciência**: 5 épocas
- **Modo**: min
- **LR Mínimo**: 1e-7
- **Função**: Reduz taxa de aprendizado quando val_loss estagna

---

## 📈 Métricas de Avaliação

### Métricas Calculadas no Conjunto de Teste

#### MSE (Mean Squared Error)
- **Fórmula**: `MSE = (1/n) * Σ(y_true - y_pred)²`
- **Unidade**: R$²
- **Interpretação**: Penaliza erros grandes quadraticamente

#### RMSE (Root Mean Squared Error)
- **Fórmula**: `RMSE = √MSE`
- **Unidade**: R$
- **Interpretação**: Erro médio na mesma escala dos preços
- **Valor Esperado**: < R$ 0.50

#### MAE (Mean Absolute Error)
- **Fórmula**: `MAE = (1/n) * Σ|y_true - y_pred|`
- **Unidade**: R$
- **Interpretação**: Erro médio absoluto
- **Valor Esperado**: < R$ 0.30

#### MAPE (Mean Absolute Percentage Error)
- **Fórmula**: `MAPE = (100/n) * Σ|(y_true - y_pred) / y_true|`
- **Unidade**: %
- **Interpretação**: Erro percentual médio
- **Valor Esperado**: < 5%

#### R² Score (Coeficiente de Determinação)
- **Fórmula**: `R² = 1 - (SS_res / SS_tot)`
- **Range**: -∞ a 1
- **Interpretação**: Proporção da variância explicada pelo modelo
- **Valor Esperado**: > 0.85

---

## 🎯 Resultados Alcançados

### Performance do Modelo

| Métrica | Valor Obtido | Avaliação |
|---------|--------------|-----------|
| **RMSE** | R$ 0.26 | ✅ Excelente |
| **MAE** | R$ 0.20 | ✅ Excelente |
| **MAPE** | 1.53% | ✅ Excelente (< 2%) |
| **R² Score** | 0.9351 | ✅ Excelente (93.5%) |
| **Erro % vs Preço Médio** | 2.00% | ✅ Excelente (< 5%) |

### Informações do Treinamento

- **Épocas Executadas**: 49 de 50
- **Early Stopping**: Ativado na época 39
- **Melhor Época**: 39
- **Best val_loss**: 0.000811
- **Duração**: ~28 segundos
- **Overfitting**: Não detectado

### Estatísticas dos Dados de Teste

- **Preço Médio**: R$ 12.83
- **Preço Mínimo**: R$ 10.23
- **Preço Máximo**: R$ 14.78
- **Amostras de Teste**: 179 dias

---

## 📊 Saída Esperada no Console

```
======================================================================
FASE 4: TREINAMENTO E AVALIAÇÃO DO MODELO LSTM
======================================================================

📂 Carregando Dados Preparados:
──────────────────────────────────────────────────────────────────────

   ✅ X_train    carregado - Shape: (830, 60, 5)
   ✅ y_train    carregado - Shape: (830,)
   ✅ X_val      carregado - Shape: (177, 60, 5)
   ✅ y_val      carregado - Shape: (177,)
   ✅ X_test     carregado - Shape: (179, 60, 5)
   ✅ y_test     carregado - Shape: (179,)

🔄 Carregando Scaler:
──────────────────────────────────────────────────────────────────────

   ✅ Scaler carregado: models\scaler.pkl
   📊 Range de normalização: (0, 1)

⚙️  Configurando Callbacks:
──────────────────────────────────────────────────────────────────────

   ✅ Early Stopping configurado:
      • Monitor: val_loss
      • Paciência: 10 épocas
      • Restaurar melhores pesos: True

   ✅ Model Checkpoint configurado:
      • Salvando em: models\lstm_model_best.h5
      • Monitor: val_loss
      • Salvar apenas o melhor: True

   ✅ Reduce LR on Plateau configurado:
      • Monitor: val_loss
      • Fator de redução: 0.5
      • Paciência: 5 épocas

🚀 Iniciando Treinamento:
──────────────────────────────────────────────────────────────────────

   📊 Configurações:
      • Épocas: 50
      • Batch Size: 32
      • Amostras de Treino: 830
      • Amostras de Validação: 177

Epoch 1/50
26/26 [==============================] - 3s - loss: 0.0242 - mae: 0.1128 - val_loss: 0.0056 - val_mae: 0.0640
Epoch 2/50
26/26 [==============================] - 1s - loss: 0.0059 - mae: 0.0610 - val_loss: 0.0031 - val_mae: 0.0421
...
Epoch 39/50
26/26 [==============================] - 1s - loss: 0.0017 - mae: 0.0323 - val_loss: 8.1145e-04 - val_mae: 0.0209
...
Epoch 49: early stopping

──────────────────────────────────────────────────────────────────────
✅ Treinamento Concluído!
   ⏱️  Duração: 27.67 segundos (0.46 minutos)
   📈 Épocas executadas: 49

📏 Calculando Métricas de Desempenho:
──────────────────────────────────────────────────────────────────────

   📊 Métricas em Escala Original (R$):
      • MSE (Mean Squared Error):           0.0656
      • RMSE (Root Mean Squared Error):     0.2561
      • MAE (Mean Absolute Error):          0.1987
      • MAPE (Mean Abs Percentage Error):     1.53%
      • R² Score:                           0.9351

   📈 Estatísticas dos Dados de Teste:
      • Preço Médio:   R$      12.83
      • Preço Mínimo:  R$      10.23
      • Preço Máximo:  R$      14.78

   🎯 Análise de Erro:
      • RMSE vs Preço Médio: 2.00%
      • Avaliação: ✅ Excelente (< 5%)

======================================================================
✅ FASE 4 CONCLUÍDA COM SUCESSO!
======================================================================

📁 Arquivos gerados:
   → models/lstm_model_best.h5
   → docs/training/training_results.json
   → docs/training/curvas_aprendizado.png
   → docs/training/resultado_teste.png

📊 Resumo de Desempenho:
   → RMSE: R$ 0.26
   → MAE:  R$ 0.20
   → MAPE: 1.53%
   → R² Score: 0.9351

🎯 Próximos passos:
   → Análise detalhada dos resultados
   → Ajuste de hiperparâmetros se necessário
   → Preparação para deploy (Fase 5)
```

---

## 🔍 Interpretação dos Resultados

### Qualidade do Modelo: EXCELENTE ✅

#### 1. Precisão Notável
- **MAPE de 1.53%**: Em média, o modelo erra apenas 1.53% do valor real
- **MAE de R$ 0.20**: Erro médio de apenas 20 centavos por ação
- **Conclusão**: Capacidade excepcional de prever preços de fechamento

#### 2. Capacidade Explicativa
- **R² de 0.9351**: O modelo explica 93.5% da variância dos dados
- **Interpretação**: Excelente captura dos padrões temporais
- **Conclusão**: Alta confiabilidade nas previsões

#### 3. Generalização
- **Gap treino-validação < 10%**: Sem overfitting significativo
- **Curvas convergentes**: Modelo generalizou bem
- **Conclusão**: Desempenho será mantido em dados futuros

#### 4. Erro Relativo Baixo
- **2% de erro vs preço médio**: Altamente aceitável
- **Range de preços**: R$ 10.23 - R$ 14.78
- **Conclusão**: Modelo confiável para previsões de curto prazo

---

## 🔍 Validação da Execução

### Verificar Modelo Salvo
```bash
# Verificar tamanho do modelo
ls -lh models/lstm_model_best.h5

# Deve mostrar ~0.4 MB
```

### Verificar Resultados
```bash
# Ver métricas finais
cat docs/training/training_results.json | grep -A 10 "metricas_teste"
```

### Verificar Gráficos
```bash
# Listar visualizações
ls -lh docs/training/*.png

# Deve mostrar:
# - curvas_aprendizado.png
# - resultado_teste.png
```

---

## 🚨 Solução de Problemas

### Erro: "No module named 'tensorflow'"
```bash
pip install tensorflow==2.15.1
```

### Erro: "FileNotFoundError: X_train.npy"
- **Causa**: Fase 2 não foi executada
- **Solução**: Execute `python src/data_preparation.py` primeiro

### Aviso: "Learning rate reduced"
- **Natureza**: Normal (ReduceLROnPlateau funcionando)
- **Significado**: Taxa de aprendizado ajustada automaticamente
- **Ação**: Pode ignorar

### Performance Ruim (MAPE > 10%)
- **Causa**: Possíveis problemas nos dados ou hiperparâmetros
- **Soluções**:
  1. Verificar qualidade dos dados da Fase 1
  2. Aumentar número de épocas
  3. Ajustar arquitetura (mais neurônios/camadas)
  4. Aumentar timesteps (de 60 para 90 dias)

---

## ✅ Checklist de Verificação

- [ ] Fases 1, 2 e 3 concluídas
- [ ] Dados preparados disponíveis (X_train, y_train, etc.)
- [ ] Script executado sem erros
- [ ] Modelo salvo em `models/lstm_model_best.h5`
- [ ] Resultados salvos em `training_results.json`
- [ ] Gráficos gerados (curvas de aprendizado e predições)
- [ ] MAPE < 5% ✅
- [ ] R² Score > 0.85 ✅
- [ ] Early Stopping ativado
- [ ] Melhor modelo carregado

---

## 🎯 Próximos Passos

Após concluir a Fase 4 com sucesso:

1. **Fase 5**: Persistência e Verificação do Modelo
   - Verificar artefatos salvos
   - Testar carregamento do modelo
   - Gerar metadados para API
   - Documentar especificações

```bash
# Próximo comando
python src/model_persistence.py
```

---

## 📚 Referências

- [Keras Model Checkpoint](https://keras.io/api/callbacks/model_checkpoint/)
- [Early Stopping in Neural Networks](https://www.tensorflow.org/api_docs/python/tf/keras/callbacks/EarlyStopping)
- [Understanding Learning Curves](https://machinelearningmastery.com/learning-curves-for-diagnosing-machine-learning-model-performance/)
- [Regression Metrics](https://scikit-learn.org/stable/modules/model_evaluation.html#regression-metrics)

---

**Data de Criação**: 02/11/2025  
**Versão**: 1.0.0  
**Autor**: ArgusPortal
