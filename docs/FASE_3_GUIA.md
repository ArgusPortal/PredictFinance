# Guia de Execução - Fase 3: Construção da Arquitetura LSTM

## 📋 Objetivo da Fase 3

Construir a arquitetura do modelo LSTM (Long Short-Term Memory) conforme especificações técnicas, compilar o modelo com otimizador Adam e função de perda MSE, e gerar documentação da estrutura da rede neural.

---

## 🔧 Pré-requisitos

### 1. Dependências Instaladas
As bibliotecas necessárias já devem estar instaladas do requirements.txt:
- tensorflow
- keras
- numpy
- json

### 2. Verificar Instalação do TensorFlow
```bash
python -c "import tensorflow as tf; print(tf.__version__)"
```

Versão esperada: 2.15.0 ou superior

---

## 🚀 Executar Fase 3

### Comando de Execução
```bash
python src/model_builder.py
```

---

## 📤 Saídas Esperadas

Após a execução bem-sucedida, os seguintes arquivos serão criados:

### 1. Arquitetura do Modelo (JSON)
**Localização**: `models/model_architecture.json`
- **Conteúdo**: Estrutura completa do modelo em formato JSON
- **Tamanho**: ~3-4 KB
- **Uso**: Permite reconstruir o modelo sem os pesos

### 2. Informações Detalhadas
**Localização**: `docs/model_architecture/model_info.json`
- **Conteúdo**: Metadados completos do modelo
  - Nome do modelo
  - Input/Output shapes
  - Número de parâmetros
  - Detalhes de cada camada
  - Configuração de compilação
- **Tamanho**: ~1-2 KB

### 3. Resumo da Arquitetura
**Localização**: `docs/model_architecture/model_summary.txt`
- **Conteúdo**: Resumo textual do modelo (Keras summary)
- **Formato**: Texto plano
- **Tamanho**: ~1 KB

---

## 🏗️ Arquitetura do Modelo

### Camadas Implementadas

```
┌─────────────────────────────────────────────┐
│  Input: (60 timesteps, 5 features)          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  LSTM Layer 1                               │
│  • Units: 64                                │
│  • return_sequences: True                   │
│  • Parâmetros: 17,920                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Dropout Layer                              │
│  • Rate: 0.2 (20%)                          │
│  • Reduz overfitting                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  LSTM Layer 2                               │
│  • Units: 32                                │
│  • return_sequences: False                  │
│  • Parâmetros: 12,416                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  Dense Output Layer                         │
│  • Units: 1                                 │
│  • Activation: Linear                       │
│  • Parâmetros: 33                           │
└─────────────────────────────────────────────┘
                    ↓
         (Preço de fechamento previsto)
```

### Estatísticas do Modelo

- **Total de Parâmetros**: 30,369
- **Parâmetros Treináveis**: 30,369
- **Parâmetros Não-Treináveis**: 0
- **Tamanho do Modelo**: ~118.63 KB
- **Número de Camadas**: 4

---

## ⚙️ Configuração de Compilação

### Otimizador
- **Nome**: Adam
- **Descrição**: Otimizador adaptativo eficiente
- **Taxa de Aprendizado**: 0.001 (padrão)

### Função de Perda
- **Nome**: MSE (Mean Squared Error)
- **Descrição**: Apropriada para problemas de regressão
- **Fórmula**: `MSE = (1/n) * Σ(y_true - y_pred)²`

### Métricas de Monitoramento
- **Nome**: MAE (Mean Absolute Error)
- **Descrição**: Erro médio absoluto para interpretação fácil
- **Fórmula**: `MAE = (1/n) * Σ|y_true - y_pred|`

---

## 🔍 Validação da Execução

### Verificar Arquivos Gerados
```bash
# Listar arquivos do modelo
ls -lh models/model_architecture.json

# Listar documentação
ls -lh docs/model_architecture/
```

### Verificar Conteúdo do JSON
```bash
# Exibir informações do modelo
cat docs/model_architecture/model_info.json | head -20
```

### Verificar Resumo
```bash
# Exibir resumo da arquitetura
cat docs/model_architecture/model_summary.txt
```

---

## 📊 Saída Esperada no Console

```
======================================================================
CONSTRUÇÃO DO MODELO LSTM
======================================================================

🔨 Construindo Arquitetura:
──────────────────────────────────────────────────────────────────────

   1️⃣  Inicializando modelo Sequential...
      ✅ Modelo inicializado

   2️⃣  Adicionando Camada LSTM 1:
      • Unidades: 64
      • Return sequences: True
      • Input shape: (60, 5)
      ✅ LSTM Layer 1 adicionada

   3️⃣  Adicionando Camada Dropout:
      • Taxa: 0.2 (20%)
      • Função: Reduzir overfitting
      ✅ Dropout Layer adicionada

   4️⃣  Adicionando Camada LSTM 2:
      • Unidades: 32
      • Return sequences: False (camada final recorrente)
      ✅ LSTM Layer 2 adicionada

   5️⃣  Adicionando Camada Dense de Saída:
      • Unidades: 1 (previsão do preço)
      • Ativação: Linear (regressão)
      ✅ Dense Output Layer adicionada

──────────────────────────────────────────────────────────────────────
✅ Arquitetura construída com sucesso!

⚙️  Compilando Modelo:
──────────────────────────────────────────────────────────────────────

   🔧 Configurações de Compilação:
      • Otimizador: ADAM
        └─ Adam: Otimizador adaptativo eficiente
      • Função de Perda: MSE
        └─ MSE: Apropriada para regressão
      • Métricas: ['MAE']
        └─ MAE: Erro médio absoluto (interpretação fácil)

   ✅ Modelo compilado com sucesso!

📊 Resumo da Arquitetura:
──────────────────────────────────────────────────────────────────────

Model: "LSTM_B3SA3_Predictor"
_________________________________________________________________
 Layer (type)                Output Shape              Param #
=================================================================
 lstm_layer_1 (LSTM)         (None, 60, 64)            17920

 dropout_layer (Dropout)     (None, 60, 64)            0

 lstm_layer_2 (LSTM)         (None, 32)                12416

 output_layer (Dense)        (None, 1)                 33

=================================================================
Total params: 30369 (118.63 KB)
Trainable params: 30369 (118.63 KB)
Non-trainable params: 0 (0.00 Byte)
_________________________________________________________________

📈 Estatísticas do Modelo:
   • Total de parâmetros:      30,369
   • Parâmetros treináveis:    30,369
   • Parâmetros não-treináveis: 0
   • Número de camadas:        4
   • Input shape:              (None, 60, 5)
   • Output shape:             (None, 1)

======================================================================
✅ CONSTRUÇÃO DO MODELO CONCLUÍDA COM SUCESSO!
======================================================================
```

---

## 🎓 Conceitos Técnicos

### LSTM (Long Short-Term Memory)
- **Tipo**: Rede Neural Recorrente especializada
- **Vantagem**: Capaz de aprender dependências de longo prazo
- **Uso**: Séries temporais, sequências, previsão
- **Componentes**: Cell state, gates (forget, input, output)

### Return Sequences
- **True**: Retorna sequência completa (necessário para empilhar LSTMs)
- **False**: Retorna apenas última saída (camada final antes da Dense)

### Dropout
- **Função**: Regularização para prevenir overfitting
- **Mecânica**: Desativa aleatoriamente 20% dos neurônios durante treino
- **Benefício**: Força a rede a aprender features mais robustas

---

## 🚨 Solução de Problemas

### Erro: "Module 'tensorflow' not found"
```bash
# Reinstalar TensorFlow
pip install tensorflow==2.15.1
```

### Erro: "cuDNN not found"
- **Causa**: GPU não configurada corretamente
- **Solução**: O modelo funciona em CPU. Para GPU, instale CUDA Toolkit e cuDNN

### Aviso: "oneDNN custom operations"
- **Natureza**: Informativo (não é erro)
- **Significado**: TensorFlow otimizando operações para CPU
- **Ação**: Pode ignorar

---

## ✅ Checklist de Verificação

- [ ] TensorFlow instalado e funcionando
- [ ] Script executado sem erros
- [ ] Arquivo `model_architecture.json` criado
- [ ] Arquivo `model_info.json` criado com metadados
- [ ] Arquivo `model_summary.txt` criado
- [ ] Resumo do modelo exibido no console
- [ ] Total de parâmetros: 30,369
- [ ] Input shape: (None, 60, 5)
- [ ] Output shape: (None, 1)

---

## 🎯 Próximos Passos

Após concluir a Fase 3 com sucesso:

1. **Fase 4**: Treinamento do Modelo e Avaliação
   - Treinar o modelo com dados de treino
   - Validar com dados de validação
   - Avaliar métricas de desempenho
   - Gerar curvas de aprendizado

```bash
# Próximo comando
python src/model_training.py
```

---

## 📚 Referências

- [Keras LSTM Documentation](https://keras.io/api/layers/recurrent_layers/lstm/)
- [Understanding LSTM Networks](http://colah.github.io/posts/2015-08-Understanding-LSTMs/)
- [Dropout: A Simple Way to Prevent Neural Networks from Overfitting](http://jmlr.org/papers/v15/srivastava14a.html)
- [Adam Optimizer](https://arxiv.org/abs/1412.6980)

---

**Data de Criação**: 02/11/2025  
**Versão**: 1.0.0  
**Autor**: ArgusPortal
