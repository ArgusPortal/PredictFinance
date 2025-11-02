# Guia de Execução - Fase 1: Coleta e Limpeza de Dados

## 📋 Objetivo da Fase 1

Coletar dados históricos da ação B3SA3.SA (B3 S.A.) dos últimos 5 anos através da API do Yahoo Finance, realizar tratamento e limpeza dos dados, e preparar análises exploratórias iniciais.

---

## 🔧 Pré-requisitos

### 1. Python Instalado
Verifique se o Python 3.9+ está instalado:
```bash
python --version
```

### 2. Instalar Dependências

#### Opção A: Instalação Completa (Recomendado)
```bash
pip install -r requirements.txt
```

#### Opção B: Instalação Mínima (Apenas Fase 1)
```bash
pip install yfinance pandas numpy scipy matplotlib seaborn
```

---

## 🚀 Executar Fase 1

### Comando de Execução
```bash
python src/data_collection.py
```

---

## 📤 Saídas Esperadas

Após a execução bem-sucedida, os seguintes arquivos serão criados:

### 1. Dados Coletados
- **Localização**: `data/raw/b3sa3_historical.csv`
- **Conteúdo**: Dados históricos (OHLCV) da B3SA3.SA
- **Formato**: CSV com colunas:
  - `Date` (índice): Data do pregão
  - `Open`: Preço de abertura
  - `High`: Preço máximo
  - `Low`: Preço mínimo
  - `Close`: Preço de fechamento
  - `Adj Close`: Preço ajustado
  - `Volume`: Volume negociado

### 2. Log de Execução
- **Localização**: `docs/data_collection/data_collection_log.json`
- **Conteúdo**: Metadados da coleta
  - Timestamp de execução
  - Período de dados coletados
  - Estatísticas de limpeza
  - Métricas dos dados

### 3. Visualizações
- **Localização**: `docs/data_collection/`
- **Arquivos**:
  - `analise_exploratoria.png`: Gráficos de série temporal, distribuição, volume e boxplot
  - `matriz_correlacao.png`: Mapa de calor com correlações entre features

---

## 📊 O Que o Script Faz

### 1. Coleta de Dados
- Conecta ao Yahoo Finance via biblioteca `yfinance`
- Baixa 5 anos de dados históricos da B3SA3.SA
- Valida período e completude dos dados

### 2. Análise de Dados Faltantes
- Identifica valores ausentes em cada coluna
- Calcula percentual de missing data
- Documenta estatísticas

### 3. Limpeza de Dados
- Remove duplicatas
- Trata valores ausentes com forward fill (limite de 3 dias)
- Valida consistência de preços (Low ≤ Open, Close ≤ High)
- Detecta outliers usando Z-score (threshold = 3 desvios padrão)
- Garante valores positivos para preços e volume

### 4. Análise Exploratória
- **Estatísticas Descritivas**: Média, mediana, desvio padrão, mín/máx
- **Série Temporal**: Evolução do preço de fechamento
- **Distribuição**: Histograma dos preços
- **Volume**: Gráfico de barras do volume negociado
- **Boxplot**: Visualização de OHLC
- **Matriz de Correlação**: Relações entre features

### 5. Salvamento
- Exporta dados limpos em CSV
- Gera log JSON com metadados
- Salva visualizações em PNG (300 DPI)

---

## ✅ Verificação de Sucesso

Ao final da execução, você deve ver:

```
======================================================================
✅ FASE 1 CONCLUÍDA COM SUCESSO!
======================================================================

📁 Próximos passos:
   → Execute: python src/data_preparation.py
   → Para preparar os dados para o modelo LSTM
```

### Validar Saídas

1. **Verificar CSV criado**:
```bash
# Windows
dir data\raw\b3sa3_historical.csv

# Linux/Mac
ls -lh data/raw/b3sa3_historical.csv
```

2. **Verificar logs**:
```bash
# Windows
type docs\data_collection\data_collection_log.json

# Linux/Mac
cat docs/data_collection/data_collection_log.json
```

3. **Visualizar gráficos**:
- Abra os arquivos `.png` em `docs/data_collection/`

---

## 🔍 Exemplos de Dados Coletados

### Estrutura do CSV
```csv
Date,Open,High,Low,Close,Adj Close,Volume
2020-11-02,11.50,11.75,11.45,11.68,10.89,15234000
2020-11-03,11.70,11.92,11.63,11.85,11.05,18456000
...
```

### Exemplo de Log JSON
```json
{
  "timestamp": "2025-11-02T10:30:00.000000",
  "ticker": "B3SA3.SA",
  "periodo": {
    "inicio": "2020-11-02",
    "fim": "2025-11-02",
    "dias_totais": 1234
  },
  "estatisticas_limpeza": {
    "duplicatas_removidas": 0,
    "missing_tratados": 5,
    "inconsistencias": 0,
    "outliers_detectados": 3,
    "valores_negativos": 0,
    "registros_finais": 1229
  },
  "estatisticas_dados": {
    "preco_medio": 12.45,
    "preco_minimo": 9.80,
    "preco_maximo": 15.20,
    "preco_atual": 13.50,
    "volume_medio": 12000000
  }
}
```

---

## ⚠️ Possíveis Problemas e Soluções

### Problema 1: "No module named 'yfinance'"
**Solução**: Instalar dependências
```bash
pip install yfinance
```

### Problema 2: "Nenhum dado encontrado para B3SA3.SA"
**Possíveis causas**:
- Sem conexão com internet
- Yahoo Finance temporariamente indisponível
- Ticker incorreto

**Solução**: 
- Verificar conexão
- Tentar novamente em alguns minutos

### Problema 3: Erro ao salvar gráficos
**Causa**: Matplotlib backend incompatível

**Solução**: Adicionar no início do script:
```python
import matplotlib
matplotlib.use('Agg')
```

### Problema 4: Dados insuficientes
**Causa**: B3SA3.SA tem menos de 5 anos de histórico disponível

**Solução**: Ajustar a variável `YEARS_OF_DATA` no script

---

## 📈 Interpretação dos Resultados

### Métricas de Qualidade dos Dados

- **Duplicatas Removidas**: Deve ser 0 (Yahoo Finance não retorna duplicatas)
- **Missing Tratados**: Poucos (< 1% dos dados)
- **Inconsistências**: Deve ser 0
- **Outliers**: 0-5 outliers são aceitáveis
- **Valores Negativos**: Deve ser 0

### Análise da Série Temporal

- **Tendência**: Observar se há tendência de alta, baixa ou lateralização
- **Volatilidade**: Períodos com grandes variações indicam instabilidade
- **Volume**: Picos de volume podem indicar eventos importantes

### Correlações Esperadas

- **Close vs Adj Close**: ~1.0 (altamente correlacionados)
- **Open vs Close**: 0.9-0.95 (correlação forte)
- **Volume vs Preço**: Variável (depende do comportamento do ativo)

---

## 🎯 Critérios de Aceitação

Para prosseguir para a Fase 2, os dados devem atender:

- ✅ Mínimo de 1000 dias de dados
- ✅ Menos de 1% de valores ausentes
- ✅ Zero inconsistências nos preços
- ✅ Arquivo CSV gerado com sucesso
- ✅ Log JSON criado
- ✅ Visualizações salvas

---

## 📝 Próximos Passos

Após concluir com sucesso a Fase 1, prossiga para:

**Fase 2: Preparação dos Dados para LSTM**
```bash
python src/data_preparation.py
```

Esta fase irá:
- Carregar dados de `data/raw/b3sa3_historical.csv`
- Normalizar usando MinMaxScaler
- Criar sequências temporais (janelas de 60 dias)
- Dividir em conjuntos treino/validação/teste
- Salvar em `data/processed/`

---

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs em `docs/data_collection/data_collection_log.json`
2. Consultar especificações técnicas em `docs/especificacoes_tecnicas.md`
3. Revisar código-fonte comentado em `src/data_collection.py`

---

**Versão**: 1.0.0  
**Última Atualização**: 02/11/2025  
**Autor**: ArgusPortal
