# Guia de Execução - Fase 5: Persistência e Verificação do Modelo

## 📋 Objetivo da Fase 5

Verificar a integridade dos artefatos de produção (modelo treinado e scaler), testar o carregamento e funcionamento correto, gerar metadados completos para construção da API, e documentar especificações técnicas para deployment.

---

## 🔧 Pré-requisitos

### 1. Fases Anteriores Concluídas

Certifique-se de que as fases anteriores foram executadas com sucesso:

```bash
# Verificar modelo treinado (Fase 4)
ls models/lstm_model_best.h5

# Verificar scaler (Fase 2)
ls models/scaler.pkl

# Verificar arquitetura (Fase 3)
ls models/model_architecture.json
```

### 2. Dependências Instaladas
As bibliotecas necessárias já devem estar instaladas do requirements.txt:
- tensorflow/keras
- joblib
- numpy
- json

---

## 🚀 Executar Fase 5

### Comando de Execução
```bash
python src/model_persistence.py
```

### Tempo Estimado
- **Execução**: 5-10 segundos
- **Carregamento e Testes**: Rápido

---

## 📤 Saídas Esperadas

Após a execução bem-sucedida, os seguintes arquivos serão criados:

### 1. Metadados de Deployment
**Localização**: `docs/deployment/model_deployment_metadata.json`
- **Conteúdo**:
  - Informações completas dos artefatos
  - Metadados do modelo (input/output shapes)
  - Metadados do scaler (range, features)
  - Resultados de validação e testes
  - Instruções de uso
- **Tamanho**: ~5-6 KB

### 2. Metadados da API
**Localização**: `docs/deployment/api_metadata.json`
- **Conteúdo**:
  - Especificações de input/output
  - Versão da API
  - Estrutura dos dados esperados
  - Ordem das features
  - Timesteps e configurações
- **Tamanho**: ~1-2 KB
- **Uso**: Base para construção da API FastAPI

### 3. README de Deployment
**Localização**: `docs/deployment/README.md`
- **Conteúdo**:
  - Documentação completa dos artefatos
  - Exemplos de código para uso
  - Instruções de carregamento
  - Especificações técnicas
  - Métricas de performance
- **Formato**: Markdown
- **Tamanho**: ~2-3 KB

---

## 🔍 Artefatos Verificados

### 1. Modelo LSTM
- **Arquivo**: `lstm_model_best.h5`
- **Formato**: HDF5 (Keras/TensorFlow)
- **Tamanho**: ~0.39 MB
- **Parâmetros**: 30,369
- **Input Shape**: (None, 60, 5)
- **Output Shape**: (None, 1)
- **Status**: ✅ Verificado e testado

### 2. Scaler de Normalização
- **Arquivo**: `scaler.pkl`
- **Formato**: PKL (joblib)
- **Tipo**: MinMaxScaler
- **Tamanho**: ~0.86 KB
- **Range**: [0, 1]
- **Features**: 5 (Open, High, Low, Close, Volume)
- **Status**: ✅ Verificado e testado

### 3. Arquitetura do Modelo
- **Arquivo**: `model_architecture.json`
- **Formato**: JSON
- **Tamanho**: ~3.41 KB
- **Uso**: Documentação de referência
- **Status**: ✅ Disponível

---

## 🧪 Testes Realizados

### 1. Teste de Carregamento do Modelo
```
✅ Modelo carregado com sucesso
   • Nome: LSTM_B3SA3_Predictor
   • Parâmetros: 30,369
   • 4 camadas carregadas corretamente
   • Compilação preservada
```

### 2. Teste de Carregamento do Scaler
```
✅ Scaler carregado com sucesso
   • Tipo: MinMaxScaler
   • Range: [0, 1]
   • 5 features configuradas
   • Data min/max preservados
```

### 3. Teste de Predição de Exemplo
```
✅ Predição realizada com sucesso
   • Input Shape: (1, 60, 5)
   • Predição Normalizada: ~0.35-0.45
   • Predição Final: R$ ~12-13
   • Validação: ✅ Dentro do range esperado (R$ 10-15)
```

---

## 📊 Especificações para API

### Input Esperado

**Formato**: JSON
```json
{
  "dados_historicos": [
    [Open, High, Low, Close, Volume],  // Dia 1
    [Open, High, Low, Close, Volume],  // Dia 2
    ...
    [Open, High, Low, Close, Volume]   // Dia 60
  ]
}
```

**Requisitos**:
- **Shape**: (60, 5)
- **Timesteps**: 60 dias históricos
- **Features**: 5 valores por dia
- **Ordem**: [Open, High, Low, Close, Volume]
- **Tipo**: float

### Output Esperado

**Formato**: JSON
```json
{
  "preco_previsto": 12.45,
  "unidade": "R$",
  "confianca": "alta",
  "timestamp": "2025-11-02T16:31:21"
}
```

**Descrição**:
- **Tipo**: float
- **Descrição**: Preço de fechamento previsto para o próximo dia
- **Unidade**: R$ (Reais)
- **Range Esperado**: R$ 8.00 - R$ 18.00

---

## 📊 Saída Esperada no Console

```
======================================================================
FASE 5: PERSISTÊNCIA E VERIFICAÇÃO DO MODELO
======================================================================

🔍 Verificando Artefatos Salvos:
──────────────────────────────────────────────────────────────────────

   ✅ Modelo LSTM encontrado:
      • Arquivo: lstm_model_best.h5
      • Tamanho: 0.39 MB
      • Modificado: 2025-11-02 16:26:44
      • Formato: HDF5

   ✅ Scaler encontrado:
      • Arquivo: scaler.pkl
      • Tamanho: 0.86 KB
      • Modificado: 2025-11-02 16:12:45
      • Formato: PKL (joblib)

   ✅ Arquitetura encontrada:
      • Arquivo: model_architecture.json
      • Tamanho: 3.41 KB
      • Formato: JSON

🧪 Testando Carregamento do Modelo:
──────────────────────────────────────────────────────────────────────

   📥 Carregando modelo de: models\lstm_model_best.h5
   ✅ Modelo carregado com sucesso!

   📊 Metadados do Modelo:
      • Nome: LSTM_B3SA3_Predictor
      • Input Shape: [None, 60, 5]
      • Output Shape: [None, 1]
      • Parâmetros: 30,369
      • Camadas: 4

   🔍 Arquitetura:
      1. lstm_layer_1 (LSTM) → (None, 60, 64)
      2. dropout_layer (Dropout) → (None, 60, 64)
      3. lstm_layer_2 (LSTM) → (None, 32)
      4. output_layer (Dense) → (None, 1)

🧪 Testando Carregamento do Scaler:
──────────────────────────────────────────────────────────────────────

   📥 Carregando scaler de: models\scaler.pkl
   ✅ Scaler carregado com sucesso!

   📊 Metadados do Scaler:
      • Tipo: MinMaxScaler
      • Feature Range: [0, 1]
      • Número de Features: 5
      • Data Min: ['8.9940', '9.1309', '8.7887', '8.9451', '0.0000']
      • Data Max: ['17.7529', '18.0457', '17.5953', '17.8627', '276369600.0000']

🧪 Testando Predição de Exemplo:
──────────────────────────────────────────────────────────────────────

   📝 Gerando dados de exemplo...
   🔄 Normalizando dados...
   🔮 Fazendo predição...
   🔄 Desnormalizando resultado...
   ✅ Predição realizada com sucesso!

   📊 Resultados do Teste:
      • Input Shape: (1, 60, 5)
      • Predição Normalizada: 0.420353
      • Predição Final: R$ 12.69
      • Range Esperado: R$ 10.00 - R$ 15.00

   ✅ Predição dentro do range esperado

📋 Gerando Metadados para API:
──────────────────────────────────────────────────────────────────────

   ✅ Metadados gerados:
      • Versão da API: 1.0.0
      • Timesteps: 60
      • Features: 5
      • Features: ['Open', 'High', 'Low', 'Close', 'Volume']
      • Scaler Range: [0, 1]

💾 Salvando Documentação:
──────────────────────────────────────────────────────────────────────

   ✅ Documentação completa: docs/deployment\model_deployment_metadata.json (5.39 KB)
   ✅ Metadados da API: docs/deployment\api_metadata.json (1.34 KB)
   ✅ README de deployment: docs/deployment\README.md (2.37 KB)

======================================================================
✅ FASE 5 CONCLUÍDA COM SUCESSO!
======================================================================

📁 Artefatos Verificados:
   ✅ lstm_model_best.h5 (0.39 MB)
   ✅ scaler.pkl (0.86 KB)
   ✅ model_architecture.json (3.41 KB)

📊 Especificações do Modelo:
   → Input Shape: [None, 60, 5]
   → Output Shape: [None, 1]
   → Timesteps: 60
   → Features: ['Open', 'High', 'Low', 'Close', 'Volume']

📁 Documentação Gerada:
   → docs/deployment/model_deployment_metadata.json
   → docs/deployment/api_metadata.json
   → docs/deployment/README.md

🎯 Próximos Passos:
   → Construir API FastAPI (Fase 6)
   → Implementar endpoints de predição
   → Adicionar validação de entrada
   → Deploy em produção

🧹 Memória liberada (modelo e scaler removidos da RAM)
```

---

## 📝 Exemplo de Uso dos Artefatos

### Carregar Modelo e Scaler

```python
import joblib
from tensorflow import keras
import numpy as np

# 1. Carregar artefatos
model = keras.models.load_model('models/lstm_model_best.h5')
scaler = joblib.load('models/scaler.pkl')

print("✅ Artefatos carregados com sucesso!")
```

### Preparar Dados e Fazer Predição

```python
# 2. Preparar dados de entrada (60 dias × 5 features)
dados_historicos = np.array([
    [12.50, 12.75, 12.30, 12.60, 50000000],  # Dia 1
    [12.60, 12.80, 12.55, 12.70, 52000000],  # Dia 2
    # ... (58 dias mais)
])  # Shape: (60, 5)

# 3. Normalizar
dados_normalizados = scaler.transform(dados_historicos)

# 4. Reshape para o modelo
input_modelo = dados_normalizados.reshape(1, 60, 5)

# 5. Fazer predição
predicao_normalizada = model.predict(input_modelo)

# 6. Desnormalizar resultado
ultima_linha = dados_historicos[-1:].copy()
ultima_linha[0, 3] = predicao_normalizada[0, 0]  # Substituir Close

resultado = scaler.inverse_transform(ultima_linha)
preco_previsto = resultado[0, 3]  # Extrair Close

print(f"Preço previsto: R$ {preco_previsto:.2f}")
```

---

## 🔍 Validação da Execução

### Verificar Documentação Gerada
```bash
# Listar arquivos de deployment
ls -lh docs/deployment/

# Deve mostrar:
# - model_deployment_metadata.json (~5 KB)
# - api_metadata.json (~1 KB)
# - README.md (~2 KB)
```

### Verificar Conteúdo dos Metadados
```bash
# Ver metadados da API
cat docs/deployment/api_metadata.json

# Ver README
cat docs/deployment/README.md
```

### Verificar Artefatos
```bash
# Verificar todos os artefatos
ls -lh models/

# Deve mostrar:
# - lstm_model_best.h5 (~0.4 MB)
# - scaler.pkl (~1 KB)
# - model_architecture.json (~3 KB)
```

---

## 🚨 Solução de Problemas

### Erro: "FileNotFoundError: lstm_model_best.h5"
- **Causa**: Fase 4 (treinamento) não foi executada
- **Solução**: Execute `python src/model_training.py` primeiro

### Erro: "FileNotFoundError: scaler.pkl"
- **Causa**: Fase 2 (preparação) não foi executada
- **Solução**: Execute `python src/data_preparation.py` primeiro

### Erro: "Unable to load model"
- **Causa**: Versão do TensorFlow incompatível
- **Solução**: Reinstale TensorFlow correto
```bash
pip install tensorflow==2.15.1
```

### Aviso: "Compiled metrics are not supported for this model"
- **Natureza**: Informativo (não é erro)
- **Significado**: Algumas métricas de compilação não foram salvas
- **Ação**: Pode ignorar, modelo funciona normalmente

---

## ✅ Checklist de Verificação

- [ ] Fases 1, 2, 3 e 4 concluídas
- [ ] Modelo `lstm_model_best.h5` existe
- [ ] Scaler `scaler.pkl` existe
- [ ] Script executado sem erros
- [ ] Modelo carregado com sucesso (✅)
- [ ] Scaler carregado com sucesso (✅)
- [ ] Teste de predição passou (✅)
- [ ] Arquivo `model_deployment_metadata.json` criado
- [ ] Arquivo `api_metadata.json` criado
- [ ] Arquivo `README.md` de deployment criado
- [ ] Metadados completos para API gerados
- [ ] Input shape verificado: (None, 60, 5)
- [ ] Output shape verificado: (None, 1)

---

## 🎓 Conceitos Técnicos

### Persistência de Modelo
- **HDF5**: Formato hierárquico que armazena arquitetura + pesos + compilação
- **Vantagem**: Arquivo único e portátil
- **Uso**: Produção e deployment

### Serialização do Scaler
- **Joblib**: Biblioteca otimizada para objetos NumPy
- **Pickle**: Formato de serialização Python
- **Importância**: Mesma normalização deve ser aplicada em produção

### Metadados para API
- **Função**: Documentar requisitos de entrada/saída
- **Uso**: Validação automática de requests
- **Benefício**: Contrato claro entre frontend e backend

---

## 🎯 Próximos Passos

Após concluir a Fase 5 com sucesso:

1. **Fase 6**: Construção da API FastAPI
   - Criar endpoints REST
   - Implementar validação de entrada
   - Adicionar documentação automática (Swagger)
   - Testar localmente

```bash
# Próximos comandos
# (Fase 6 - será implementada)
```

---

## 📚 Referências

- [Keras Model Saving](https://keras.io/guides/serialization_and_saving/)
- [Joblib Documentation](https://joblib.readthedocs.io/)
- [HDF5 Format](https://www.hdfgroup.org/solutions/hdf5/)
- [Model Deployment Best Practices](https://ml-ops.org/content/model-serving)

---

**Data de Criação**: 02/11/2025  
**Versão**: 1.0.0  
**Autor**: ArgusPortal
