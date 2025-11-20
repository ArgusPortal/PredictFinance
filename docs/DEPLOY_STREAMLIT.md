# 🚀 Deploy Frontend Streamlit Cloud

## Arquitetura de Deploy

```
┌─────────────────────┐         ┌──────────────────────┐
│  Streamlit Cloud    │◄───────►│   Render.com         │
│  (Frontend)         │  HTTPS  │   (API Backend)      │
│  app_streamlit.py   │         │   FastAPI + LSTM     │
│  Port: 443          │         │   Port: 10000        │
└─────────────────────┘         └──────────────────────┘
         │                                  │
         │                                  │
         ▼                                  ▼
    Usuários                        SQLite Cache DB
```

## ✅ Pré-requisitos

1. ✅ API já deployada no Render: `https://b3sa3-api.onrender.com`
2. ✅ Conta no Streamlit Cloud (https://streamlit.io/cloud)
3. ✅ Repositório GitHub com código atualizado

## 📋 Checklist Pré-Deploy

```bash
# 1. Verificar arquivos necessários
ls -la app_streamlit.py
ls -la .streamlit/config.toml
ls -la requirements.txt

# 2. Verificar se API está online
curl https://b3sa3-api.onrender.com/health

# 3. Testar localmente primeiro
streamlit run app_streamlit.py
```

## 🚀 Passos para Deploy

### 1. Commit das Alterações

```bash
git add app_streamlit.py
git add .streamlit/
git add docs/DEPLOY_STREAMLIT.md
git commit -m "feat: integração Streamlit com SQLite cache via API"
git push origin main
```

### 2. Acessar Streamlit Cloud

1. Acesse: https://share.streamlit.io/
2. Faça login com GitHub
3. Clique em **"New app"**

### 3. Configurar Aplicação

| Campo | Valor |
|-------|-------|
| **Repository** | `ArgusPortal/PredictFinance` |
| **Branch** | `main` |
| **Main file path** | `app_streamlit.py` |
| **App URL** | `predictfinance` (ou customize) |

### 4. Configurar Secrets

No painel do Streamlit Cloud:

1. Vá em **Settings** → **Secrets**
2. Cole o conteúdo (formato TOML):

```toml
# URL da API no Render
API_BASE_URL = "https://b3sa3-api.onrender.com"

# Chave Gemini para relatórios IA
GEMINI_API_KEY = "SUA_CHAVE_AQUI"
```

3. Clique em **Save**

### 5. Deploy Automático

- Streamlit Cloud detecta `requirements.txt` automaticamente
- Build leva ~3-5 minutos
- URL gerada: `https://predictfinance.streamlit.app`

## 🔧 Configurações Avançadas

### Python Version

O Streamlit Cloud usa Python 3.11 por padrão. Para especificar:

Crie `.streamlit/python-version.txt`:
```
3.10
```

### Dependencies

O `requirements.txt` principal será usado. Certifique-se de incluir:

```txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
requests>=2.31.0
yfinance>=0.2.28
python-dotenv>=1.0.0
google-generativeai>=0.3.0
```

### Health Check

O Streamlit Cloud usa o endpoint `/healthz` automaticamente.
Nossa configuração em `.streamlit/config.toml`:

```toml
[server]
headless = true
enableCORS = true
```

## 🌐 Fluxo de Dados

### 1. Busca de Dados Históricos

```
Streamlit → GET /data/historical/{ticker}?start_date&end_date
          ← JSON com dados OHLCV do cache SQLite
```

### 2. Previsão

```
Streamlit → POST /predict/auto {"ticker": "B3SA3.SA"}
          ← JSON com previsão, confiança, métricas
```

### 3. Análise Técnica

```
Streamlit → POST /analise-tecnica {"ticker": "B3SA3.SA"}
          ← JSON com indicadores técnicos
```

## 📊 Vantagens da Arquitetura

### ✅ Cache SQLite

- **Performance**: Queries < 10ms (vs 2-30s do Yahoo)
- **Resiliência**: Funciona mesmo com Yahoo bloqueado
- **Histórico**: 6 anos de dados (2020-2025)

### ✅ Deploy Separado

- **Escalabilidade**: Frontend e backend escalam independentemente
- **Manutenção**: Atualizar um não afeta o outro
- **Custo**: Ambos em tier gratuito

### ✅ Fallback Automático

O Streamlit tenta buscar dados nesta ordem:
1. 🏆 **Cache SQLite** (via API `/data/historical`) - Preferido
2. 🌐 **Yahoo Finance** (direto) - Se API falhar
3. 📦 **Dados Hardcoded** (60 dias) - Último recurso

## 🔄 Atualização Automática

### GitHub Actions (Daily Update)

O workflow `.github/workflows/daily_update_db.yml` roda diariamente:

1. **4h UTC**: Atualiza `market_data.db` com dados novos
2. **Commit automático** no repo
3. **Render redeploy** automático (API)
4. **Streamlit Cloud** usa dados atualizados via API

## 🐛 Troubleshooting

### ❌ "API offline" no Streamlit

**Causa**: API no Render está dormindo (free tier)

**Solução**:
- Aguarde 30-60s (cold start)
- Ou acesse `https://b3sa3-api.onrender.com/health` para acordar

### ❌ "No data found"

**Causa**: Banco SQLite não tem dados do ticker solicitado

**Solução**:
```bash
# Popular banco com novo ticker
python database/populate_db.py --ticker PETR4.SA --years 5

# Commit e push
git add database/market_data.db
git commit -m "feat: adicionar dados PETR4.SA"
git push
```

### ❌ CORS errors

**Causa**: Configuração CORS incorreta

**Solução**: Verificar `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### ❌ "Module not found"

**Causa**: Dependência faltando em `requirements.txt`

**Solução**:
```bash
# Adicionar ao requirements.txt
pip freeze | grep nome-pacote >> requirements.txt
git commit -am "fix: adicionar dependência"
git push
```

## 📝 Monitoramento

### Logs do Streamlit

Acesse: Dashboard → App → Logs

### Métricas da API

```bash
# Verificar health
curl https://b3sa3-api.onrender.com/health

# Ver métricas
curl https://b3sa3-api.onrender.com/info
```

### Analytics

O Streamlit Cloud fornece:
- **Viewers**: Número de usuários
- **Sessions**: Sessões ativas
- **Resources**: Uso de CPU/RAM

## 🔐 Segurança

### Secrets Management

- ✅ **Nunca commitar** `.streamlit/secrets.toml`
- ✅ Usar Streamlit Cloud Secrets para produção
- ✅ `.env` apenas para desenvolvimento local

### API Keys

```python
# No código Streamlit
import streamlit as st

# Buscar da configuração do Streamlit Cloud
GEMINI_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
```

## 🎯 Checklist Final

Antes de fazer deploy:

- [ ] ✅ API no Render funcionando
- [ ] ✅ Banco SQLite populado e commitado
- [ ] ✅ `app_streamlit.py` usando `buscar_dados_historicos()`
- [ ] ✅ `.streamlit/config.toml` configurado (headless=true)
- [ ] ✅ `requirements.txt` completo
- [ ] ✅ Secrets configurados no Streamlit Cloud
- [ ] ✅ Teste local funcionando
- [ ] ✅ Commit e push para GitHub

## 🚀 Deploy!

```bash
# Após configurar tudo
git push origin main
```

Acesse no Streamlit Cloud e clique em **"Reboot app"** se necessário.

## 📞 Suporte

- **Streamlit Docs**: https://docs.streamlit.io/
- **Streamlit Community**: https://discuss.streamlit.io/
- **Issues GitHub**: https://github.com/ArgusPortal/PredictFinance/issues

---

**Última atualização**: 2025-11-20  
**Versão**: 2.0
