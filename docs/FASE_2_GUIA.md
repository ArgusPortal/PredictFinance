# Guia de Execução - Fase 2: Preparação dos Dados para LSTM

## 📋 Objetivo da Fase 2

Transformar os dados limpos da Fase 1 em formato adequado para treinamento da rede neural LSTM, incluindo normalização, criação de sequências temporais e divisão em conjuntos de treino, validação e teste.

---

## 🔧 Pré-requisitos

### 1. Fase 1 Concluída
Certifique-se de que a Fase 1 foi executada com sucesso e o arquivo existe:
```bash
data/raw/b3sa3_historical.csv
```

### 2. Dependências Instaladas
As bibliotecas necessárias já devem estar instaladas do requirements.txt:
- pandas
- numpy
- scikit-learn (MinMaxScaler)
- joblib
- matplotlib
- seaborn

---

## 🚀 Executar Fase 2

### Comando de Execução
```bash
python src/data_preparation.py
```

---

## 📤 Saídas Esperadas

Após a execução bem-sucedida, os seguintes arquivos serão criados:

### 1. Arrays NumPy (Dados Processados)
**Localização**: `data/processed/`

- **X_train.npy**: Sequências de entrada para treino
  - Shape: (n_train, 60, 5)
  - n_train ≈ 70% do total de sequências
  - 60 = timesteps (janela de 60 dias)
  - 5 = features (Open, High, Low, Close, Volume)

- **y_train.npy**: Valores alvo para treino
  - Shape: (n_train, 1)
  - Preços de fechamento normalizados

- **X_val.npy, y_val.npy**: Validação (15%)
- **X_test.npy, y_test.npy**: Teste (15%)

### 2. Scaler Persistido
**Localização**: `models/scaler.pkl`

- MinMaxScaler ajustado aos dados
- Necessário para:
  - Desnormalizar previsões futuras
  - Normalizar novos dados em produção

### 3. Log de Execução
**Localização**: `docs/data_preparation/data_preparation_log.json`

- Parâmetros utilizados
- Shapes dos conjuntos de dados
- Metadados da normalização

### 4. Visualizações
**Localização**: `docs/data_preparation/data_preparation_viz.png`

Gráficos incluindo:
- Comparação Original vs Normalizado
- Distribuição dos dados normalizados
- Divisão temporal (treino/validação/teste)
- Exemplo de sequência LSTM

---

## 📊 O Que o Script Faz

### 1. Carregamento de Dados
- Lê `data/raw/b3sa3_historical.csv`
- Verifica ordem cronológica
- Exibe primeiras linhas

### 2. Normalização (MinMaxScaler)
- Transforma valores para range [0, 1]
- Aplica a todas as features: Open, High, Low, Close, Volume
- **Por que normalizar?**
  - Estabiliza gradientes durante treinamento
  - Melhora convergência da LSTM
  - Evita dominância de features com maior escala

### 3. Criação de Sequências Temporais
- **Método**: Janela deslizante (sliding window)
- **Tamanho da janela**: 60 dias
- **Estrutura**:
  ```
  X[0] = dados[dia 0 a dia 59]   → y[0] = Close do dia 60
  X[1] = dados[dia 1 a dia 60]   → y[1] = Close do dia 61
  ...
  ```
- Cada sequência tem shape (60, 5)

### 4. Divisão Temporal (Não Aleatória!)
- **Treino**: 70% (dados mais antigos)
- **Validação**: 15% (dados intermediários)
- **Teste**: 15% (dados mais recentes)

**Importante**: A divisão é temporal para evitar **data leakage**. Não podemos treinar com dados do futuro!

### 5. Salvamento
- Arrays NumPy: formato eficiente para TensorFlow
- Scaler: para uso em produção
- Logs e visualizações: documentação

---

## ✅ Verificação de Sucesso

Ao final da execução, você deve ver:

```
======================================================================
✅ FASE 2 CONCLUÍDA COM SUCESSO!
======================================================================

📁 Arquivos gerados:
   → data/processed/X_train.npy, y_train.npy
   → data/processed/X_val.npy, y_val.npy
   → data/processed/X_test.npy, y_test.npy
   → models/scaler.pkl
   → docs/data_preparation/

📊 Estatísticas:
   → Sequências de treino: ~830
   → Sequências de validação: ~178
   → Sequências de teste: ~178
   → Timesteps por sequência: 60
   → Features por timestep: 5

🎯 Próximos passos:
   → Execute: python src/model_training.py
   → Para treinar o modelo LSTM
```

### Validar Saídas

**1. Verificar arrays criados**:
```bash
# Windows
dir data\processed

# Linux/Mac
ls -lh data/processed
```

Deve mostrar 6 arquivos `.npy`.

**2. Verificar scaler**:
```bash
# Windows
dir models\scaler.pkl

# Linux/Mac
ls -lh models/scaler.pkl
```

**3. Testar carregamento (Python)**:
```python
import numpy as np
import joblib

# Carregar dados
X_train = np.load('data/processed/X_train.npy')
y_train = np.load('data/processed/y_train.npy')
scaler = joblib.load('models/scaler.pkl')

print(f"X_train shape: {X_train.shape}")
print(f"y_train shape: {y_train.shape}")
print(f"Scaler range: {scaler.feature_range}")
```

---

## 🔍 Entendendo as Sequências

### Exemplo Prático

Com 1.246 dias de dados da Fase 1 e timesteps=60:

```
Dias disponíveis: 1.246
- Primeiros 60 dias: usados para criar a 1ª sequência
- Total de sequências: 1.246 - 60 = 1.186

Divisão:
- Treino (70%): ~830 sequências (dias 0-889)
- Validação (15%): ~178 sequências (dias 890-1067)
- Teste (15%): ~178 sequências (dias 1068-1186)
```

### Formato dos Dados

**X_train** (entrada):
```
Shape: (830, 60, 5)
- 830 sequências
- 60 timesteps (dias)
- 5 features por dia

Exemplo X_train[0]:
[[Open_d0, High_d0, Low_d0, Close_d0, Volume_d0],
 [Open_d1, High_d1, Low_d1, Close_d1, Volume_d1],
 ...
 [Open_d59, High_d59, Low_d59, Close_d59, Volume_d59]]
```

**y_train** (alvo):
```
Shape: (830,)
- 830 valores alvo
- Cada valor = Close normalizado do dia seguinte

Exemplo:
y_train[0] = Close do dia 60 (dia após a sequência)
```

---

## 📈 Por Que 60 Timesteps?

**Razões técnicas**:
1. **Padrão da indústria**: Comum para séries temporais financeiras
2. **~3 meses** de dados (~60 dias úteis)
3. **Balanço**:
   - Muito curto (ex: 10 dias): contexto insuficiente
   - Muito longo (ex: 200 dias): overfitting, treino lento

**Pode ser ajustado**: Altere a constante `TIMESTEPS` no código se desejar experimentar.

---

## ⚠️ Possíveis Problemas e Soluções

### Problema 1: "FileNotFoundError: data/raw/b3sa3_historical.csv"
**Causa**: Fase 1 não foi executada

**Solução**:
```bash
python src/data_collection.py
```

### Problema 2: Shapes inconsistentes
**Causa**: Dados corrompidos ou incompletos

**Solução**: Re-executar Fase 1 para coletar dados novamente

### Problema 3: Memória insuficiente
**Causa**: Arrays grandes demais para RAM disponível

**Solução**: 
- Reduzir `TIMESTEPS`
- Usar menos features
- Aumentar RAM

---

## 🎓 Conceitos Importantes

### 1. MinMaxScaler vs StandardScaler

**MinMaxScaler (usado)**:
- Range: [0, 1]
- Fórmula: `(x - min) / (max - min)`
- Vantagens: Valores limitados, ideal para LSTM

**StandardScaler**:
- Média 0, desvio padrão 1
- Fórmula: `(x - mean) / std`
- Valores podem ser negativos

### 2. Divisão Temporal vs Aleatória

**Temporal (usado)** ✅:
- Respeita ordem cronológica
- Evita data leakage
- Simula cenário real

**Aleatória** ❌:
- Pode treinar com dados do futuro
- Métricas otimistas enganosas
- Não usar para séries temporais!

### 3. Janela Deslizante

```
Dados: [d0, d1, d2, d3, d4, d5, ..., d100]
Timesteps: 3

Sequências:
X[0] = [d0, d1, d2] → y[0] = d3
X[1] = [d1, d2, d3] → y[1] = d4
X[2] = [d2, d3, d4] → y[2] = d5
...
```

---

## 📝 Próximos Passos

Após concluir com sucesso a Fase 2, prossiga para:

**Fase 3: Treinamento do Modelo LSTM**
```bash
python src/model_training.py
```

Esta fase irá:
- Carregar dados de `data/processed/`
- Construir arquitetura LSTM
- Treinar com early stopping
- Salvar modelo em `models/`

---

**Versão**: 1.0.0  
**Última Atualização**: 02/11/2025  
**Autor**: ArgusPortal
