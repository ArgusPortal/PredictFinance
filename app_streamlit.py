"""
Aplicação Streamlit - PredictFinance
Interface avançada para previsão de preços B3SA3.SA com análises e visualizações
"""

import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf
from pathlib import Path
import sys
import json
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="PredictFinance - Previsão B3SA3.SA",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar path para imports
ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

# Configurações da API - usa variável de ambiente ou localhost
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .prediction-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .prediction-price {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<h1 class="main-header">🔮 PredictFinance</h1>', unsafe_allow_html=True)
    st.markdown("### Previsão de Preços com LSTM")
    st.markdown("---")
    
    # Seleção de página
    page = st.radio(
        "Navegação",
        ["🏠 Início", "📊 Análise Descritiva", "🎯 Métricas do Modelo", "🔮 Previsão", "📈 Análise Técnica"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Informações do modelo
    st.markdown("### ℹ️ Informações")
    try:
        response = requests.get(f"{API_BASE_URL}/info", timeout=5)
        if response.status_code == 200:
            info = response.json()
            st.success("✅ API Online")
            st.metric("Window Size", f"{info.get('window_size', 60)} dias")
            st.metric("Features", len(info.get('features', [])))
        else:
            st.error("❌ API Offline")
    except:
        st.warning("⚠️ Conectando à API...")
    
    st.markdown("---")
    st.markdown("**Versão:** 2.0")
    st.markdown("**Última atualização:** 20/11/2025")


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def buscar_dados_historicos(ticker: str, period: str = "1y", use_cache: bool = True):
    """
    Busca dados históricos do banco SQLite via API ou fallback para yfinance
    
    Args:
        ticker: Símbolo da ação (ex: B3SA3.SA)
        period: Período (1mo, 3mo, 6mo, 1y, 2y, 5y)
        use_cache: Se True, tenta buscar do banco via API primeiro
    
    Returns:
        DataFrame com dados OHLCV ou None
    """
    # Mapear período para dias
    period_days = {
        "1mo": 30,
        "3mo": 90,
        "6mo": 180,
        "1y": 365,
        "2y": 730,
        "5y": 1825
    }
    
    days = period_days.get(period, 365)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Tentar buscar do banco via API primeiro
    if use_cache:
        try:
            response = requests.get(
                f"{API_BASE_URL}/data/historical/{ticker}",
                params={
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": end_date.strftime("%Y-%m-%d")
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('count', 0) > 0:
                    # Converter para DataFrame
                    df = pd.DataFrame(data['data'])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    
                    # Renomear colunas para match yfinance
                    df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                    
                    st.info(f"📊 Dados obtidos do cache SQLite ({data['count']} registros)")
                    return df
                    
        except Exception as e:
            st.warning(f"⚠️ Cache SQLite indisponível, usando Yahoo Finance: {str(e)}")
    
    # Fallback para yfinance
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        
        if not df.empty:
            st.info(f"📡 Dados obtidos do Yahoo Finance ({len(df)} registros)")
            return df
        else:
            return None
            
    except Exception as e:
        st.error(f"❌ Erro ao buscar dados: {str(e)}")
        return None


# ============================================================
# PÁGINA: INÍCIO
# ============================================================
if page == "🏠 Início":
    st.markdown('<h1 class="main-header">PredictFinance - Dashboard Principal</h1>', unsafe_allow_html=True)
    st.markdown("### Sistema de Previsão de Preços com Redes LSTM")
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("MAPE", "1.53%", delta="-0.5%", delta_color="inverse")
        st.caption("Erro Percentual Médio")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("R²", "0.9351", delta="+2.1%")
        st.caption("Coeficiente de Determinação")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("MAE", "R$ 0.20", delta="-0.05")
        st.caption("Erro Absoluto Médio")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Parâmetros", "30,369", delta="Otimizado")
        st.caption("Total de Parâmetros")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Informações do projeto
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Sobre o Projeto")
        st.markdown("""
        Sistema completo de previsão de preços de ações usando **Redes Neurais LSTM** (Long Short-Term Memory).
        
        **Features:**
        - 🔄 Busca automática de dados via Yahoo Finance
        - 📊 Análise descritiva completa dos dados
        - 🎯 Métricas detalhadas do modelo
        - 🔮 Previsão em tempo real
        - 📈 Análise técnica avançada
        
        **Modelo:**
        - Arquitetura: LSTM 2 camadas (64 → 32 unidades)
        - Window Size: 60 dias
        - Features: Open, High, Low, Close, Volume
        """)
    
    with col2:
        st.markdown("### 📈 Desempenho do Modelo")
        
        # Gráfico de métricas
        metrics_data = {
            'Métrica': ['MAPE', 'R²', 'MAE', 'RMSE'],
            'Valor': [1.53, 93.51, 0.20, 0.26],
            'Benchmark': [2.0, 90.0, 0.25, 0.30]
        }
        df_metrics = pd.DataFrame(metrics_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Modelo Atual',
            x=df_metrics['Métrica'],
            y=df_metrics['Valor'],
            marker_color='#667eea'
        ))
        fig.add_trace(go.Bar(
            name='Benchmark',
            x=df_metrics['Métrica'],
            y=df_metrics['Benchmark'],
            marker_color='#764ba2'
        ))
        
        fig.update_layout(
            title='Comparação com Benchmark',
            barmode='group',
            height=300,
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Quick Start
    st.markdown("### 🚀 Quick Start")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 1️⃣ Análise Descritiva")
        st.info("Explore estatísticas e visualizações dos dados históricos")
        if st.button("📊 Ver Análises", key="btn_analysis"):
            st.session_state.page = "📊 Análise Descritiva"
            st.rerun()
    
    with col2:
        st.markdown("#### 2️⃣ Métricas do Modelo")
        st.info("Veja métricas detalhadas de performance do LSTM")
        if st.button("🎯 Ver Métricas", key="btn_metrics"):
            st.session_state.page = "🎯 Métricas do Modelo"
            st.rerun()
    
    with col3:
        st.markdown("#### 3️⃣ Fazer Previsão")
        st.info("Gere previsões em tempo real para qualquer ticker")
        if st.button("🔮 Fazer Previsão", key="btn_predict"):
            st.session_state.page = "🔮 Previsão"
            st.rerun()


# ============================================================
# PÁGINA: ANÁLISE DESCRITIVA
# ============================================================
elif page == "📊 Análise Descritiva":
    st.markdown('<h1 class="main-header">📊 Análise Descritiva dos Dados</h1>', unsafe_allow_html=True)
    
    # Seleção de ticker
    ticker = st.text_input("Digite o ticker:", value="B3SA3.SA", key="ticker_analysis")
    period = st.selectbox("Período de análise:", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
    
    if st.button("🔍 Buscar Dados", key="fetch_data"):
        with st.spinner("Buscando dados..."):
            try:
                # Buscar dados do cache SQLite ou Yahoo Finance
                df = buscar_dados_historicos(ticker, period, use_cache=True)
                
                if df is None or df.empty:
                    st.error(f"❌ Nenhum dado encontrado para {ticker}")
                else:
                    st.success(f"✅ Dados carregados: {len(df)} registros")
                    
                    # Armazenar em session_state
                    st.session_state.df_analysis = df
                    st.session_state.ticker_name = ticker
                    
            except Exception as e:
                st.error(f"❌ Erro ao buscar dados: {e}")
    
    # Mostrar análises se dados estiverem disponíveis
    if 'df_analysis' in st.session_state:
        df = st.session_state.df_analysis
        ticker_name = st.session_state.ticker_name
        
        st.markdown("---")
        
        # Estatísticas descritivas
        st.markdown("### 📋 Estatísticas Descritivas")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Preço Atual", f"R$ {df['Close'].iloc[-1]:.2f}")
        with col2:
            st.metric("Máximo", f"R$ {df['Close'].max():.2f}")
        with col3:
            st.metric("Mínimo", f"R$ {df['Close'].min():.2f}")
        with col4:
            st.metric("Média", f"R$ {df['Close'].mean():.2f}")
        with col5:
            variation = ((df['Close'].iloc[-1] - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
            st.metric("Variação", f"{variation:.2f}%", delta=f"{variation:.2f}%")
        
        st.markdown("---")
        
        # Tabela de estatísticas
        st.markdown("### 📊 Tabela de Estatísticas")
        stats_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].describe()
        st.dataframe(stats_df.style.format("{:.2f}"), use_container_width=True)
        
        st.markdown("---")
        
        # Gráficos
        tab1, tab2, tab3, tab4 = st.tabs(["📈 Preços", "📊 Volume", "🔔 Volatilidade", "📉 Correlação"])
        
        with tab1:
            st.markdown("#### Evolução dos Preços (OHLC)")
            
            fig = go.Figure()
            
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'
            ))
            
            # Média móvel
            df['MA20'] = df['Close'].rolling(window=20).mean()
            df['MA50'] = df['Close'].rolling(window=50).mean()
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA20'],
                name='MA20',
                line=dict(color='orange', width=1)
            ))
            
            fig.add_trace(go.Scatter(
                x=df.index, y=df['MA50'],
                name='MA50',
                line=dict(color='blue', width=1)
            ))
            
            fig.update_layout(
                title=f'{ticker_name} - Preços e Médias Móveis',
                yaxis_title='Preço (R$)',
                xaxis_title='Data',
                height=500,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.markdown("#### Volume de Negociação")
            
            fig = go.Figure()
            
            colors = ['red' if df['Close'].iloc[i] < df['Open'].iloc[i] else 'green' 
                     for i in range(len(df))]
            
            fig.add_trace(go.Bar(
                x=df.index,
                y=df['Volume'],
                marker_color=colors,
                name='Volume'
            ))
            
            fig.update_layout(
                title=f'{ticker_name} - Volume de Negociação',
                yaxis_title='Volume',
                xaxis_title='Data',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Estatísticas de volume
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Volume Médio", f"{df['Volume'].mean():,.0f}")
            with col2:
                st.metric("Volume Máximo", f"{df['Volume'].max():,.0f}")
            with col3:
                st.metric("Volume Mínimo", f"{df['Volume'].min():,.0f}")
        
        with tab3:
            st.markdown("#### Análise de Volatilidade")
            
            # Calcular retornos
            df['Returns'] = df['Close'].pct_change()
            df['Volatility'] = df['Returns'].rolling(window=20).std() * np.sqrt(252)
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df['Volatility'] * 100,
                fill='tozeroy',
                name='Volatilidade (20d)',
                line=dict(color='purple')
            ))
            
            fig.update_layout(
                title=f'{ticker_name} - Volatilidade Histórica (Anualizada)',
                yaxis_title='Volatilidade (%)',
                xaxis_title='Data',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Distribuição de retornos
            fig2 = go.Figure()
            fig2.add_trace(go.Histogram(
                x=df['Returns'].dropna() * 100,
                nbinsx=50,
                name='Retornos',
                marker_color='#667eea'
            ))
            
            fig2.update_layout(
                title='Distribuição de Retornos Diários',
                xaxis_title='Retorno (%)',
                yaxis_title='Frequência',
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with tab4:
            st.markdown("#### Matriz de Correlação")
            
            corr_matrix = df[['Open', 'High', 'Low', 'Close', 'Volume']].corr()
            
            fig = go.Figure(data=go.Heatmap(
                z=corr_matrix.values,
                x=corr_matrix.columns,
                y=corr_matrix.columns,
                colorscale='RdBu',
                zmid=0,
                text=corr_matrix.values,
                texttemplate='%{text:.2f}',
                textfont={"size": 12},
                colorbar=dict(title="Correlação")
            ))
            
            fig.update_layout(
                title='Matriz de Correlação entre Features',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Download dos dados
        st.markdown("### 💾 Download dos Dados")
        csv = df.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Baixar dados CSV",
            data=csv,
            file_name=f'{ticker_name}_dados.csv',
            mime='text/csv',
        )


# ============================================================
# PÁGINA: MÉTRICAS DO MODELO
# ============================================================
elif page == "🎯 Métricas do Modelo":
    st.markdown('<h1 class="main-header">🎯 Métricas de Performance do Modelo</h1>', unsafe_allow_html=True)
    
    # Carregar dados de treinamento do JSON
    training_json_path = ROOT_DIR / "docs" / "training" / "training_results.json"
    training_data = None
    
    if training_json_path.exists():
        try:
            with open(training_json_path, 'r') as f:
                training_data = json.load(f)
        except:
            pass
    
    # Tabs para organizar o conteúdo
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Métricas de Teste", 
        "📈 Curvas de Aprendizado", 
        "⚙️ Hiperparâmetros",
        "🏗️ Arquitetura"
    ])
    
    with tab1:
        st.markdown("### 📊 Resultados no Conjunto de Teste")
        
        try:
            response = requests.get(f"{API_BASE_URL}/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics = response.json()
                
                # Métricas principais em cards
                col1, col2, col3, col4 = st.columns(4)
                
                metricas_teste = metrics.get('metricas_teste', {})
                
                with col1:
                    mape = metricas_teste.get('MAPE', {})
                    st.metric(
                        "MAPE",
                        mape.get('valor', 'N/A'),
                        help=mape.get('descricao', '')
                    )
                    if 'interpretacao' in mape:
                        st.caption(f"✅ {mape['interpretacao']}")
                
                with col2:
                    r2 = metricas_teste.get('R2', {})
                    st.metric(
                        "R² Score",
                        r2.get('valor', 'N/A'),
                        help=r2.get('descricao', '')
                    )
                    if 'interpretacao' in r2:
                        st.caption(f"📈 {r2['interpretacao']}")
                
                with col3:
                    mae = metricas_teste.get('MAE', {})
                    st.metric(
                        "MAE",
                        mae.get('valor', 'N/A'),
                        help=mae.get('descricao', '')
                    )
                
                with col4:
                    rmse = metricas_teste.get('RMSE', {})
                    st.metric(
                        "RMSE",
                        rmse.get('valor', 'N/A'),
                        help=rmse.get('descricao', '')
                    )
                
                st.markdown("---")
                
                # Gráfico de Resultado do Teste
                st.markdown("#### 📈 Comparação: Real vs Previsto")
                
                resultado_img_path = ROOT_DIR / "docs" / "training" / "resultado_teste.png"
                
                if resultado_img_path.exists():
                    from PIL import Image
                    img = Image.open(resultado_img_path)
                    st.image(img, use_column_width=True)
                    
                    st.info("""
                    **Interpretação do Gráfico:**
                    - **Gráfico Superior:** Série temporal mostrando preços reais (azul) vs previstos (vermelho) 
                      ao longo do conjunto de teste. A proximidade das linhas indica boa capacidade de predição.
                    - **Gráfico Inferior:** Dispersão (scatter) mostrando a correlação entre valores reais e previstos. 
                      Pontos próximos da linha vermelha tracejada indicam predições precisas.
                    - **Caixa amarela:** Métricas de performance consolidadas para fácil referência.
                    """)
                else:
                    st.info("""
                    📊 **Gráficos de Treinamento Disponíveis no README**
                    
                    As imagens de resultado do teste não estão incluídas no deploy para manter o repositório leve.
                    
                    Você pode:
                    - Ver gráficos completos no [README do GitHub](https://github.com/ArgusPortal/PredictFinance)
                    - Executar localmente: `python src/model_training.py` para gerar as imagens
                    - Confiar nas métricas da API que são calculadas em tempo real
                    """)
                
                st.markdown("---")
                
                # Comparação de métricas
                st.markdown("#### 📊 Comparação com Benchmarks")
                
                metrics_comparison = {
                    'Métrica': ['MAPE (%)', 'R²', 'MAE (R$)', 'RMSE (R$)'],
                    'Valor': [1.53, 0.9351, 0.20, 0.26],
                    'Excelente': [2.0, 0.95, 0.15, 0.20],
                    'Bom': [5.0, 0.85, 0.30, 0.35],
                    'Aceitável': [10.0, 0.70, 0.50, 0.55]
                }
                
                df_comp = pd.DataFrame(metrics_comparison)
                
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=df_comp['Métrica'],
                    y=df_comp['Excelente'],
                    name='Excelente',
                    line=dict(color='green', dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_comp['Métrica'],
                    y=df_comp['Bom'],
                    name='Bom',
                    line=dict(color='orange', dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_comp['Métrica'],
                    y=df_comp['Aceitável'],
                    name='Aceitável',
                    line=dict(color='red', dash='dash')
                ))
                
                fig.add_trace(go.Scatter(
                    x=df_comp['Métrica'],
                    y=df_comp['Valor'],
                    name='Modelo Atual',
                    mode='markers+lines',
                    marker=dict(size=15, color='#667eea'),
                    line=dict(color='#667eea', width=3)
                ))
                
                fig.update_layout(
                    title='Performance do Modelo vs Benchmarks',
                    yaxis_title='Valor',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Interpretação
                st.markdown("#### 💡 Interpretação das Métricas")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    **MAPE (Mean Absolute Percentage Error)**
                    - < 2%: Excelente ✅
                    - 2-5%: Bom 👍
                    - 5-10%: Aceitável ⚠️
                    - > 10%: Ruim ❌
                    
                    **R² (Coeficiente de Determinação)**
                    - > 0.9: Excelente ✅
                    - 0.8-0.9: Bom 👍
                    - 0.7-0.8: Aceitável ⚠️
                    - < 0.7: Ruim ❌
                    """)
                
                with col2:
                    st.markdown("""
                    **MAE (Mean Absolute Error)**
                    - Erro médio absoluto em R$
                    - Quanto menor, melhor
                    - Interpretação direta: erro médio de R$ 0.20
                    
                    **RMSE (Root Mean Squared Error)**
                    - Penaliza erros grandes
                    - Quanto menor, melhor
                    - RMSE > MAE indica presença de outliers
                    """)
            
            else:
                st.error(f"❌ Erro ao buscar métricas: Status {response.status_code}")
        
        except Exception as e:
            st.error(f"❌ Erro ao conectar com a API: {e}")
    
    with tab2:
        st.markdown("### 📈 Curvas de Aprendizado Durante o Treinamento")
        
        curvas_img_path = ROOT_DIR / "docs" / "training" / "curvas_aprendizado.png"
        
        if curvas_img_path.exists():
            from PIL import Image
            img = Image.open(curvas_img_path)
            st.image(img, use_column_width=True)
            
            st.markdown("---")
            
            st.markdown("""
            #### 📖 Como Interpretar as Curvas de Aprendizado
            
            **Gráfico da Esquerda - Loss (MSE):**
            - **Linha Azul (Treino):** Erro médio quadrático no conjunto de treinamento
            - **Linha Laranja (Validação):** Erro médio quadrático no conjunto de validação
            - **Objetivo:** Ambas as curvas devem diminuir e convergir
            - **Sinais Positivos:**
              - ✅ Curvas decrescentes indicam aprendizado
              - ✅ Convergência entre treino e validação indica generalização
              - ✅ Validação menor que treino = modelo não está overfitting
            
            **Gráfico da Direita - MAE:**
            - **Linha Azul (Treino):** Erro absoluto médio no conjunto de treinamento
            - **Linha Laranja (Validação):** Erro absoluto médio no conjunto de validação
            - **Interpretação:** Erro médio em reais (R$) que o modelo comete
            - **Sinais Positivos:**
              - ✅ Redução consistente ao longo das épocas
              - ✅ Estabilização em valores baixos
              - ✅ Pouca diferença entre treino e validação
            """)
            
        else:
            st.info("""
            📈 **Curvas de Aprendizado Disponíveis no README**
            
            As imagens de curvas de treinamento não estão incluídas no deploy para manter o repositório leve.
            
            Você pode:
            - Ver curvas completas no [README do GitHub](https://github.com/ArgusPortal/PredictFinance)
            - Executar localmente: `python src/model_training.py` para gerar as imagens
            - As estatísticas de treinamento estão disponíveis abaixo
            """)
        
        if training_data:
            st.markdown("---")
            st.markdown("#### 📊 Estatísticas de Treinamento")
            
            treino = training_data.get('treinamento', {})
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Épocas Executadas",
                    f"{treino.get('epocas_executadas', 0)}/{treino.get('epocas_configuradas', 0)}"
                )
                st.caption(f"Melhor época: {treino.get('best_epoch', 0)}")
            
            with col2:
                final_train_loss = treino.get('final_train_loss', 0)
                final_val_loss = treino.get('final_val_loss', 0)
                st.metric(
                    "Loss Final (Treino)",
                    f"{final_train_loss:.6f}"
                )
                st.caption(f"Validação: {final_val_loss:.6f}")
            
            with col3:
                final_train_mae = treino.get('final_train_mae', 0)
                final_val_mae = treino.get('final_val_mae', 0)
                st.metric(
                    "MAE Final (Treino)",
                    f"R$ {final_train_mae:.4f}"
                )
                st.caption(f"Validação: R$ {final_val_mae:.4f}")
            
            # Gráfico de evolução do histórico
            if 'historico' in training_data:
                st.markdown("---")
                st.markdown("#### 📉 Evolução Detalhada do Treinamento")
                
                hist = training_data['historico']
                
                # Criar dataframe
                epocas = list(range(1, len(hist['loss']) + 1))
                
                fig = go.Figure()
                
                # Loss
                fig.add_trace(go.Scatter(
                    x=epocas,
                    y=hist['loss'],
                    name='Loss Treino',
                    line=dict(color='blue', width=2),
                    mode='lines'
                ))
                
                fig.add_trace(go.Scatter(
                    x=epocas,
                    y=hist['val_loss'],
                    name='Loss Validação',
                    line=dict(color='orange', width=2),
                    mode='lines'
                ))
                
                # Marcar melhor época
                best_epoch = treino.get('best_epoch', 0)
                if best_epoch > 0:
                    fig.add_vline(
                        x=best_epoch,
                        line_dash="dash",
                        line_color="green",
                        annotation_text=f"Melhor Época: {best_epoch}",
                        annotation_position="top"
                    )
                
                fig.update_layout(
                    title='Histórico Completo de Loss',
                    xaxis_title='Época',
                    yaxis_title='Loss (MSE)',
                    height=400,
                    hovermode='x unified'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("⚠️ Gráfico de curvas de aprendizado não encontrado. Execute `python src/model_training.py` para gerar.")
    
    with tab3:
        st.markdown("### ⚙️ Hiperparâmetros e Configuração do Treinamento")
        
        st.markdown("""
        Os hiperparâmetros são configurações que controlam o processo de aprendizado da rede neural. 
        A escolha correta desses valores é crucial para o desempenho do modelo.
        """)
        
        st.markdown("---")
        
        # Hiperparâmetros de Treinamento
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎓 Parâmetros de Treinamento")
            
            if training_data:
                treino = training_data.get('treinamento', {})
                
                st.markdown(f"""
                **Épocas Configuradas:** `{treino.get('epocas_configuradas', 50)}`
                - ➤ **O que é:** Número máximo de vezes que o modelo passa por todo o dataset
                - ➤ **Por que 50:** Valor balanceado que permite aprendizado suficiente sem overtraining
                - ➤ **Executadas:** {treino.get('epocas_executadas', 0)} (early stopping ativado)
                
                **Batch Size:** `{treino.get('batch_size', 32)}`
                - ➤ **O que é:** Número de amostras processadas antes de atualizar os pesos
                - ➤ **Por que 32:** Tamanho padrão que oferece bom balanço entre:
                  - Velocidade de treinamento (maior = mais rápido)
                  - Estabilidade de gradiente (menor = mais estável)
                  - Uso de memória (menor = menos RAM)
                
                **Early Stopping Patience:** `{treino.get('early_stopping_patience', 10)}`
                - ➤ **O que é:** Número de épocas sem melhora antes de parar o treinamento
                - ➤ **Por que 10:** Evita overfitting e economiza tempo computacional
                - ➤ **Melhor época:** {treino.get('best_epoch', 0)}
                """)
            else:
                st.markdown("""
                **Épocas:** `50`
                - Número de passagens completas pelo dataset
                
                **Batch Size:** `32`
                - Amostras processadas por atualização de pesos
                
                **Early Stopping Patience:** `10`
                - Épocas de espera sem melhora antes de parar
                """)
        
        with col2:
            st.markdown("#### 🧠 Arquitetura da Rede")
            
            st.markdown("""
            **LSTM Layer 1:** `64 unidades`
            - ➤ **O que é:** Primeira camada de memória de longo prazo
            - ➤ **Por que 64:** Capacidade suficiente para capturar padrões temporais complexos
            - ➤ **return_sequences=True:** Passa sequências completas para próxima camada
            
            **Dropout:** `0.2 (20%)`
            - ➤ **O que é:** Desliga aleatoriamente 20% dos neurônios durante treinamento
            - ➤ **Por que 0.2:** Previne overfitting sem prejudicar o aprendizado
            - ➤ **Efeito:** Força o modelo a não depender de neurônios específicos
            
            **LSTM Layer 2:** `32 unidades`
            - ➤ **O que é:** Segunda camada LSTM com menos unidades
            - ➤ **Por que 32:** Redução gradual que extrai features de alto nível
            - ➤ **return_sequences=False:** Retorna apenas último estado
            
            **Dense Layer:** `1 unidade`
            - ➤ **O que é:** Camada de saída totalmente conectada
            - ➤ **Por que 1:** Previsão de um único valor (preço de fechamento)
            - ➤ **Ativação:** Linear (para regressão)
            """)
        
        st.markdown("---")
        
        # Otimizador e Função de Perda
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### ⚡ Otimizador: Adam")
            
            st.markdown("""
            **Learning Rate:** `0.001` (padrão)
            - ➤ **O que é:** Taxa de ajuste dos pesos a cada iteração
            - ➤ **Por que Adam:** Algoritmo adaptativo que ajusta automaticamente a learning rate
            - ➤ **Vantagens:**
              - ✅ Converge mais rápido que SGD
              - ✅ Requer menos tuning manual
              - ✅ Funciona bem com redes profundas
              - ✅ Eficiente com gradientes esparsos
            
            **Parâmetros Adam:**
            - β₁ = 0.9 (momentum)
            - β₂ = 0.999 (momentum de segunda ordem)
            - ε = 1e-7 (estabilidade numérica)
            """)
        
        with col2:
            st.markdown("#### 📏 Função de Perda: MSE")
            
            st.markdown("""
            **Mean Squared Error (MSE)**
            - ➤ **O que é:** Média do quadrado dos erros
            - ➤ **Fórmula:** MSE = (1/n) × Σ(y_real - y_pred)²
            - ➤ **Por que MSE:** 
              - ✅ Penaliza erros grandes (devido ao quadrado)
              - ✅ Padrão para problemas de regressão
              - ✅ Diferenciável (necessário para backpropagation)
              - ✅ Sensível a outliers (alerta para predições ruins)
            
            **Métrica Auxiliar: MAE**
            - Mean Absolute Error
            - Mais interpretável (erro médio em R$)
            - Menos sensível a outliers
            """)
        
        st.markdown("---")
        
        # Callbacks
        st.markdown("#### 🔔 Callbacks Utilizados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Early Stopping**
            - Monitor: `val_loss`
            - Patience: `10 épocas`
            - Restore best weights: `True`
            
            ➤ Para o treinamento se a validação não melhorar por 10 épocas consecutivas
            """)
        
        with col2:
            st.markdown("""
            **Model Checkpoint**
            - Salva melhor modelo
            - Baseado em `val_loss`
            - Arquivo: `lstm_model.keras`
            
            ➤ Garante que sempre temos o melhor modelo salvo
            """)
        
        with col3:
            st.markdown("""
            **Reduce LR on Plateau**
            - Monitor: `val_loss`
            - Factor: `0.5` (reduz pela metade)
            - Patience: `5 épocas`
            
            ➤ Reduz learning rate se parar de melhorar
            """)
        
        st.markdown("---")
        
        # Justificativa dos Hiperparâmetros
        st.markdown("#### 🎯 Justificativa das Escolhas")
        
        st.info("""
        **Por que esses hiperparâmetros funcionam bem para previsão de ações?**
        
        1. **LSTM com 64 → 32 unidades:**
           - Séries temporais financeiras têm padrões complexos que exigem capacidade de memória
           - Redução gradual (64 → 32) cria hierarquia de features (simples → complexas)
           - Evita excesso de parâmetros que causaria overfitting
        
        2. **Window Size de 60 dias:**
           - Aproximadamente 3 meses de negociação
           - Captura tendências de curto/médio prazo
           - Suficiente para padrões sazonais sem ruído excessivo
        
        3. **Dropout de 0.2:**
           - Dados financeiros têm muito ruído
           - 20% é suficiente para regularização sem prejudicar aprendizado
           - Melhora generalização em dados não vistos
        
        4. **Batch Size de 32:**
           - Dataset pequeno/médio (~1000 sequências)
           - 32 oferece bom balanço entre estabilidade e velocidade
           - Permite ~26-30 atualizações de gradiente por época
        
        5. **Early Stopping com patience 10:**
           - Modelos financeiros podem ter variação natural no validation loss
           - 10 épocas dá tempo suficiente para superar platôs temporários
           - Evita parar muito cedo por flutuações aleatórias
        
        **Resultado:** MAPE de 1.53% e R² de 0.935 comprovam a eficácia dessas escolhas! ✅
        """)
    
    with tab4:
        st.markdown("### 🏗️ Arquitetura e Configuração do Modelo")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Estrutura das Camadas")
            
            # Gráfico de arquitetura
            layers_data = {
                'Camada': ['Input', 'LSTM 1', 'Dropout', 'LSTM 2', 'Dropout', 'Dense'],
                'Unidades': [5, 64, 64, 32, 32, 1],
                'Parâmetros': [0, 17664, 0, 12416, 0, 33],
                'Tipo': ['Input', 'LSTM', 'Regularização', 'LSTM', 'Regularização', 'Output']
            }
            df_layers = pd.DataFrame(layers_data)
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=df_layers['Camada'],
                y=df_layers['Unidades'],
                text=df_layers['Unidades'],
                textposition='auto',
                marker_color='#667eea',
                name='Unidades'
            ))
            
            fig.update_layout(
                title='Número de Unidades por Camada',
                yaxis_title='Unidades',
                height=350
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráfico de parâmetros
            fig2 = go.Figure()
            
            layers_with_params = df_layers[df_layers['Parâmetros'] > 0]
            
            fig2.add_trace(go.Bar(
                x=layers_with_params['Camada'],
                y=layers_with_params['Parâmetros'],
                text=layers_with_params['Parâmetros'],
                textposition='auto',
                marker_color='#764ba2',
                name='Parâmetros Treináveis'
            ))
            
            fig2.update_layout(
                title='Parâmetros Treináveis por Camada',
                yaxis_title='Número de Parâmetros',
                height=350
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            st.markdown("#### 📋 Resumo da Arquitetura")
            
            st.markdown("""
            ```
            Model: "lstm_b3sa3"
            _________________________________________________________________
            Layer (type)                Output Shape         Param #
            =================================================================
            lstm_1 (LSTM)              (None, 60, 64)       17,664
            dropout_1 (Dropout)        (None, 60, 64)       0
            lstm_2 (LSTM)              (None, 32)           12,416
            dropout_2 (Dropout)        (None, 32)           0
            dense (Dense)              (None, 1)            33
            =================================================================
            Total params: 30,113 (117.63 KB)
            Trainable params: 30,113 (117.63 KB)
            Non-trainable params: 0 (0.00 Byte)
            _________________________________________________________________
            ```
            
            **Input Shape:** `(batch_size, 60, 5)`
            - 60 timesteps (dias)
            - 5 features (OHLCV)
            
            **Output Shape:** `(batch_size, 1)`
            - Previsão do preço de fechamento
            
            **Total de Parâmetros:** `30,113`
            - LSTM 1: 17,664 (58.7%)
            - LSTM 2: 12,416 (41.2%)
            - Dense: 33 (0.1%)
            
            **Tamanho do Modelo:** `~118 KB`
            - Muito leve e eficiente
            - Rápido para inferência
            - Ideal para deploy em produção
            """)
            
            st.markdown("---")
            
            st.markdown("#### 🔢 Cálculo de Parâmetros LSTM")
            
            st.markdown("""
            **Fórmula:** params = 4 × (input_dim + hidden_dim + 1) × hidden_dim
            
            **LSTM Layer 1:**
            - Input: 5 features
            - Hidden: 64 units
            - Params = 4 × (5 + 64 + 1) × 64 = **17,664**
            
            **LSTM Layer 2:**
            - Input: 64 (da camada anterior)
            - Hidden: 32 units
            - Params = 4 × (64 + 32 + 1) × 32 = **12,416**
            
            **Dense Layer:**
            - Input: 32
            - Output: 1
            - Params = (32 × 1) + 1 = **33**
            """)
        
        st.markdown("---")
        
        # Dados de Treinamento
        st.markdown("#### 📚 Informações dos Dados")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Dataset Original**
            - Período: 2019-2024
            - Total: ~1,186 dias
            - Features: OHLCV (5)
            """)
        
        with col2:
            st.markdown("""
            **Sequências Geradas**
            - Treino: 830 (70%)
            - Validação: 177 (15%)
            - Teste: 179 (15%)
            """)
        
        with col3:
            st.markdown("""
            **Window Size**
            - Tamanho: 60 dias
            - Overlap: Deslizante
            - Target: Dia seguinte
            """)
        
        # Gráfico de divisão dos dados
        split_data = {
            'Conjunto': ['Treino', 'Validação', 'Teste'],
            'Percentual': [70, 15, 15],
            'Sequências': [830, 177, 179]
        }
        df_split = pd.DataFrame(split_data)
        
        fig = go.Figure()
        fig.add_trace(go.Pie(
            labels=df_split['Conjunto'],
            values=df_split['Percentual'],
            hole=0.4,
            marker_colors=['#667eea', '#764ba2', '#11998e'],
            text=df_split['Sequências'],
            texttemplate='%{label}<br>%{text} seq<br>%{percent}',
            textposition='inside'
        ))
        
        fig.update_layout(
            title='Divisão dos Dados de Treinamento',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PÁGINA: PREVISÃO
# ============================================================
elif page == "🔮 Previsão":
    st.markdown('<h1 class="main-header">🔮 Gerador de Previsões</h1>', unsafe_allow_html=True)
    
    # Tabs para diferentes métodos
    tab1, tab2 = st.tabs(["🚀 Busca Automática", "📊 Dados de Exemplo"])
    
    with tab1:
        st.markdown("### Previsão para B3SA3.SA (B3 S.A.)")
        
        st.warning("""
        ⚠️ **IMPORTANTE:** Este modelo foi treinado especificamente para a ação **B3SA3.SA** (B3 S.A. - Brasil, Bolsa, Balcão).
        
        **Não é recomendado** usar este modelo para prever outras ações, pois:
        - Cada ação tem padrões de comportamento únicos
        - O modelo aprendeu características específicas da B3SA3.SA
        - Previsões para outros tickers podem ser totalmente imprecisas
        
        Para prever outras ações, seria necessário **treinar um novo modelo** com dados históricos específicos daquela ação.
        """)
        
        st.markdown("---")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            ticker_input = st.text_input(
                "Ticker (apenas B3SA3.SA é suportado)",
                value="B3SA3.SA",
                placeholder="B3SA3.SA",
                key="ticker_predict",
                disabled=False
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            predict_button = st.button("🔮 Gerar Previsão", type="primary", use_container_width=True)
        
        # Validação do ticker
        if predict_button:
            # Normalizar ticker para comparação
            ticker_normalizado = ticker_input.strip().upper()
            if ticker_normalizado != "B3SA3.SA":
                st.error(f"""
                ❌ **Ticker não suportado: {ticker_input}**
                
                Este modelo foi treinado exclusivamente para **B3SA3.SA**.
                
                **Por que não funciona para outras ações?**
                - Cada ação tem padrões únicos de volume, volatilidade e comportamento
                - O modelo LSTM aprendeu características específicas da B3SA3.SA
                - Usar o modelo em outra ação resultará em previsões sem sentido
                
                **Como prever outras ações?**
                1. Coletar dados históricos da ação desejada (5 anos+)
                2. Treinar um novo modelo LSTM com esses dados
                3. Avaliar performance antes de usar em produção
                
                **Sugestão:** Use o ticker **B3SA3.SA** para ver o modelo em ação.
                """)
            else:
                # Ticker válido (B3SA3.SA) - fazer previsão
                with st.spinner("🔍 Buscando dados e gerando previsão..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/predict/auto",
                            json={"ticker": ticker_input},
                            timeout=45
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            st.markdown("---")
                            
                            # Box de resultado
                            st.markdown(f"""
                            <div class="prediction-box">
                                <h3>✅ Previsão Gerada com Sucesso!</h3>
                                <div class="prediction-price">R$ {result['preco_previsto']:.2f}</div>
                                <p><strong>Confiança:</strong> {result['confianca'].upper()}</p>
                                <p style="font-size: 0.9rem; margin-top: 1rem;">{result['mensagem']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("---")
                            
                            # Informações adicionais
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("### 📊 Dados Utilizados")
                                
                                # Buscar dados históricos para mostrar
                                df_hist = None
                                try:
                                    # Usar função helper para buscar dados (cache SQLite ou Yahoo)
                                    df_hist = buscar_dados_historicos(ticker_input, "3mo", use_cache=True)
                                    
                                    if df_hist is not None and not df_hist.empty:
                                        st.metric("Período", f"Últimos {len(df_hist)} dias")
                                        st.metric("Último Preço Real", f"R$ {df_hist['Close'].iloc[-1]:.2f}")
                                        st.metric("Variação (período)", f"{((df_hist['Close'].iloc[-1] - df_hist['Close'].iloc[0]) / df_hist['Close'].iloc[0] * 100):.2f}%")
                                        
                                        # Mini gráfico
                                        fig = go.Figure()
                                        fig.add_trace(go.Scatter(
                                            x=df_hist.index,
                                            y=df_hist['Close'],
                                            mode='lines',
                                            name='Preço',
                                            line=dict(color='#667eea', width=2)
                                        ))
                                        
                                        fig.update_layout(
                                            title='Histórico dos Últimos 60 Dias',
                                            height=300,
                                            showlegend=False,
                                            margin=dict(l=0, r=0, t=30, b=0)
                                        )
                                        
                                        st.plotly_chart(fig, use_container_width=True)
                                except:
                                    st.info("Gráfico histórico não disponível")
                            
                            with col2:
                                st.markdown("### 🎯 Análise da Previsão")
                                
                                # Calcular diferença
                                if df_hist is not None and not df_hist.empty:
                                    ultimo_preco = df_hist['Close'].iloc[-1]
                                    preco_previsto = result['preco_previsto']
                                    diferenca = preco_previsto - ultimo_preco
                                    diferenca_pct = (diferenca / ultimo_preco) * 100
                                    
                                    st.metric(
                                        "Variação Prevista",
                                        f"R$ {abs(diferenca):.2f}",
                                        delta=f"{diferenca_pct:.2f}%"
                                    )
                                    
                                    if diferenca > 0:
                                        st.success(f"📈 Tendência de ALTA: +{diferenca_pct:.2f}%")
                                    elif diferenca < 0:
                                        st.error(f"📉 Tendência de BAIXA: {diferenca_pct:.2f}%")
                                    else:
                                        st.info("➡️ Tendência NEUTRA")
                                    
                                    st.markdown("---")
                                    
                                    st.markdown("**💡 Interpretação:**")
                                    st.markdown(f"""
                                    - Último preço: R$ {ultimo_preco:.2f}
                                    - Previsão: R$ {preco_previsto:.2f}
                                    - Diferença: R$ {diferenca:.2f} ({diferenca_pct:+.2f}%)
                                    
                                    ⚠️ **Aviso:** Esta é uma previsão estatística baseada em dados históricos.
                                    Não deve ser usada como única base para decisões de investimento.
                                    """)
                                else:
                                    st.info("Análise detalhada não disponível")
                        
                        else:
                            error_detail = response.json().get('detail', 'Erro desconhecido')
                            st.error(f"❌ Erro na previsão: {error_detail}")
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout: A requisição demorou muito. Tente novamente.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
    
    with tab2:
        st.markdown("### Use dados de exemplo pré-carregados para teste rápido")
        st.info("📊 Esta opção usa dados reais do conjunto de teste do modelo.")
        
        if st.button("🎯 Gerar Previsão com Exemplo", type="primary", use_container_width=True):
            with st.spinner("Gerando previsão..."):
                try:
                    response = requests.get(f"{API_BASE_URL}/predict/example", timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown("---")
                        
                        st.markdown(f"""
                        <div class="prediction-box">
                            <h3>✅ Previsão de Exemplo Gerada!</h3>
                            <div class="prediction-price">R$ {result['preco_previsto']:.2f}</div>
                            <p><strong>Confiança:</strong> {result['confianca'].upper()}</p>
                            <p style="font-size: 0.9rem; margin-top: 1rem;">{result['mensagem']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.success("✅ Esta previsão foi gerada usando dados reais do conjunto de teste.")
                    
                    elif response.status_code == 404:
                        st.warning("""
                        ⚠️ Dados de exemplo não encontrados.
                        
                        Execute o comando para gerar os dados:
                        ```bash
                        python generate_example_data.py
                        ```
                        """)
                    else:
                        st.error(f"❌ Erro: Status {response.status_code}")
                
                except Exception as e:
                    st.error(f"❌ Erro: {e}")


# ============================================================
# PÁGINA: ANÁLISE TÉCNICA
# ============================================================
elif page == "📈 Análise Técnica":
    st.markdown('<h1 class="main-header">📈 Análise Técnica Avançada</h1>', unsafe_allow_html=True)
    
    # Inicializar session_state para dados da análise
    if 'technical_data' not in st.session_state:
        st.session_state.technical_data = None
    if 'technical_ticker' not in st.session_state:
        st.session_state.technical_ticker = "B3SA3.SA"
    if 'technical_period' not in st.session_state:
        st.session_state.technical_period = "6mo"
    
    ticker = st.text_input("Digite o ticker:", value=st.session_state.technical_ticker, key="ticker_technical")
    period = st.selectbox("Período:", ["1mo", "3mo", "6mo", "1y", "2y"], 
                          index=["1mo", "3mo", "6mo", "1y", "2y"].index(st.session_state.technical_period), 
                          key="period_technical")
    
    if st.button("🔍 Analisar", key="analyze_technical"):
        st.session_state.technical_ticker = ticker
        st.session_state.technical_period = period
        
        with st.spinner("Analisando..."):
            try:
                # Usar função helper para buscar dados (cache SQLite ou Yahoo)
                df = buscar_dados_historicos(ticker, period, use_cache=True)
                
                if df is None or df.empty:
                    st.error(f"❌ Nenhum dado encontrado para {ticker}")
                    st.session_state.technical_data = None
                else:
                    # Calcular indicadores técnicos
                    df['SMA_20'] = df['Close'].rolling(window=20).mean()
                    df['SMA_50'] = df['Close'].rolling(window=50).mean()
                    df['EMA_12'] = df['Close'].ewm(span=12).mean()
                    df['EMA_26'] = df['Close'].ewm(span=26).mean()
                    df['MACD'] = df['EMA_12'] - df['EMA_26']
                    df['Signal'] = df['MACD'].ewm(span=9).mean()
                    
                    # RSI
                    delta = df['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['RSI'] = 100 - (100 / (1 + rs))
                    
                    # Bollinger Bands
                    df['BB_middle'] = df['Close'].rolling(window=20).mean()
                    bb_std = df['Close'].rolling(window=20).std()
                    df['BB_upper'] = df['BB_middle'] + (bb_std * 2)
                    df['BB_lower'] = df['BB_middle'] - (bb_std * 2)
                    
                    # Adicionar volatilidade
                    df['Volatility'] = df['Close'].pct_change().rolling(window=20).std()
                    
                    # Salvar no session_state
                    st.session_state.technical_data = {
                        'df': df,
                        'ticker': ticker,
                        'period': period
                    }
                    
                    st.success(f"✅ Análise técnica completa para {ticker}")
            except Exception as e:
                st.error(f"❌ Erro ao carregar dados: {e}")
                st.session_state.technical_data = None
    
    # Exibir análise se dados existirem no session_state
    if st.session_state.technical_data:
        df = st.session_state.technical_data['df']
        ticker = st.session_state.technical_data['ticker']
        period = st.session_state.technical_data['period']
        
        try:
            # Gráfico principal com indicadores
            st.markdown("### 📊 Gráfico de Preços com Indicadores")
            
            fig = go.Figure()
            
            # Candlestick
            fig.add_trace(go.Candlestick(
                x=df.index,
                open=df['Open'],
                high=df['High'],
                low=df['Low'],
                close=df['Close'],
                name='OHLC'
            ))
            
            # Bollinger Bands
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_upper'],
                line=dict(color='gray', width=1, dash='dash'),
                name='BB Superior'
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_middle'],
                line=dict(color='blue', width=1),
                name='BB Média (SMA 20)'
            ))
            fig.add_trace(go.Scatter(
                x=df.index, y=df['BB_lower'],
                line=dict(color='gray', width=1, dash='dash'),
                name='BB Inferior',
                fill='tonexty'
            ))
            
            # SMAs
            fig.add_trace(go.Scatter(
                x=df.index, y=df['SMA_50'],
                line=dict(color='orange', width=2),
                name='SMA 50'
            ))
            
            fig.update_layout(
                title=f'{ticker} - Preços e Bollinger Bands',
                yaxis_title='Preço (R$)',
                height=500,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Indicadores secundários
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### MACD")
                
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(
                    x=df.index, y=df['MACD'],
                    name='MACD',
                    line=dict(color='blue', width=2)
                ))
                fig_macd.add_trace(go.Scatter(
                    x=df.index, y=df['Signal'],
                    name='Signal',
                    line=dict(color='red', width=2)
                ))
                fig_macd.add_trace(go.Bar(
                    x=df.index, y=df['MACD'] - df['Signal'],
                    name='Histograma',
                    marker_color='gray'
                ))
                
                fig_macd.update_layout(height=300)
                st.plotly_chart(fig_macd, use_container_width=True)
            
            with col2:
                st.markdown("#### RSI (Relative Strength Index)")
                
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(
                    x=df.index, y=df['RSI'],
                    name='RSI',
                    line=dict(color='purple', width=2)
                ))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
                
                fig_rsi.update_layout(height=300, yaxis_range=[0, 100])
                st.plotly_chart(fig_rsi, use_container_width=True)
            
            # Sinais de trading
            st.markdown("### 🎯 Análise de Sinais")
            
            col1, col2, col3 = st.columns(3)
            
            current_rsi = df['RSI'].iloc[-1]
            current_macd = df['MACD'].iloc[-1]
            current_signal = df['Signal'].iloc[-1]
            current_price = df['Close'].iloc[-1]
            sma_50 = df['SMA_50'].iloc[-1]
            
            with col1:
                if current_rsi > 70:
                    st.error("⚠️ RSI: Sobrecomprado")
                elif current_rsi < 30:
                    st.success("✅ RSI: Sobrevendido")
                else:
                    st.info(f"➡️ RSI: Neutro ({current_rsi:.1f})")
            
            with col2:
                if current_macd > current_signal:
                    st.success("✅ MACD: Tendência de Alta")
                else:
                    st.error("⚠️ MACD: Tendência de Baixa")
            
            with col3:
                if current_price > sma_50:
                    st.success("✅ Preço > SMA 50")
                else:
                    st.error("⚠️ Preço < SMA 50")
            
            st.markdown("---")
            
            # Relatório Analítico com Gemini AI
            st.markdown("### 🤖 Relatório Analítico com IA (Gemini)")
            
            # Inicializar session_state para o relatório
            if 'ai_report' not in st.session_state:
                st.session_state.ai_report = None
            if 'ai_report_timestamp' not in st.session_state:
                st.session_state.ai_report_timestamp = None
            
            if st.button("📊 Gerar Relatório com IA", key="generate_report"):
                with st.spinner("🤖 Gemini AI analisando dados técnicos..."):
                    try:
                        # Configurar Gemini com chave do ambiente
                        api_key = os.getenv('GEMINI_API_KEY')
                        if not api_key:
                            st.error("❌ Chave da API Gemini não encontrada. Configure GEMINI_API_KEY no arquivo .env")
                        else:
                            genai.configure(api_key=api_key)  # type: ignore
                            model = genai.GenerativeModel('gemini-2.0-flash')  # type: ignore
                            
                            # Preparar dados para análise
                            ultimo_preco = df['Close'].iloc[-1]
                            preco_min = df['Close'].min()
                            preco_max = df['Close'].max()
                            variacao_periodo = ((ultimo_preco - df['Close'].iloc[0]) / df['Close'].iloc[0]) * 100
                            volume_medio = df['Volume'].mean()
                            volatilidade_atual = df['Volatility'].iloc[-1] * 100 if 'Volatility' in df.columns else 0
                            
                            # Determinar sinais
                            sinal_rsi = "Sobrecomprado" if current_rsi > 70 else "Sobrevendido" if current_rsi < 30 else "Neutro"
                            sinal_macd = "Alta" if current_macd > current_signal else "Baixa"
                            sinal_sma = "Acima" if current_price > sma_50 else "Abaixo"
                            
                            # Bollinger Bands
                            bb_upper = df['BB_upper'].iloc[-1]
                            bb_lower = df['BB_lower'].iloc[-1]
                            bb_middle = df['BB_middle'].iloc[-1]
                            posicao_bb = "superior" if current_price > bb_middle else "inferior"
                            distancia_bb_upper = ((bb_upper - current_price) / current_price) * 100
                            distancia_bb_lower = ((current_price - bb_lower) / current_price) * 100
                            
                            # Criar prompt para Gemini com instruções de formatação Markdown
                            prompt = f"""
Você é um analista financeiro especializado em análise técnica. Analise os seguintes dados da ação {ticker} e forneça um relatório analítico bem estruturado em Markdown.

**DADOS TÉCNICOS:**
- Ticker: {ticker}
- Período analisado: {period}
- Preço atual: R$ {ultimo_preco:.2f}
- Variação no período: {variacao_periodo:.2f}%
- Preço mínimo: R$ {preco_min:.2f}
- Preço máximo: R$ {preco_max:.2f}
- Volume médio: {volume_medio:,.0f}
- Volatilidade anualizada: {volatilidade_atual:.2f}%

**INDICADORES TÉCNICOS:**
- RSI (14): {current_rsi:.2f} ({sinal_rsi})
- MACD: {current_macd:.4f} (Tendência de {sinal_macd})
- Signal Line: {current_signal:.4f}
- SMA 50: R$ {sma_50:.2f} (Preço está {sinal_sma})
- Bollinger Bands:
  - Superior: R$ {bb_upper:.2f} (+{distancia_bb_upper:.2f}%)
  - Média: R$ {bb_middle:.2f}
  - Inferior: R$ {bb_lower:.2f} (-{distancia_bb_lower:.2f}%)
  - Posição atual: Banda {posicao_bb}

**FORMATO OBRIGATÓRIO (use exatamente esta estrutura Markdown):**

## 📊 Resumo Executivo
[2-3 linhas com visão geral da situação atual]

## 📈 Análise Técnica
[Interpretação detalhada dos indicadores em 4-5 linhas]

**RSI:** [análise]
**MACD:** [análise]
**Bollinger Bands:** [análise]
**SMA 50:** [análise]

## 🎯 Tendência
[Tendência de curto/médio prazo em 2-3 linhas]

## 🔍 Níveis Críticos
- **Resistência:** [valores e explicação]
- **Suporte:** [valores e explicação]

## 💡 Recomendação
**Posicionamento:** [COMPRA / VENDA / MANUTENÇÃO]

[Justificativa em 3-4 linhas com base nos dados analisados]

---
⚠️ **Importante:** Análise baseada em dados históricos. Não constitui recomendação de investimento.

**INSTRUÇÕES:**
- Use Markdown corretamente (## para títulos, ** para negrito)
- Seja objetivo e profissional
- Use linguagem técnica mas acessível
- Baseie-se exclusivamente nos dados fornecidos
- NÃO use emojis dentro do texto, apenas nos títulos
- Mantenha entre 250-350 palavras
"""
                            
                            # Gerar relatório
                            response = model.generate_content(prompt)
                            st.session_state.ai_report = response.text
                            st.session_state.ai_report_timestamp = datetime.now()
                            
                            # Extrair dados para métricas visuais
                            st.session_state.ai_report_data = {
                                'ticker': ticker,
                                'preco': ultimo_preco,
                                'variacao': variacao_periodo,
                                'rsi': current_rsi,
                                'sinal_rsi': sinal_rsi,
                                'sinal_macd': sinal_macd,
                                'volatilidade': volatilidade_atual
                            }
                            
                            st.success("✅ Relatório gerado com sucesso!")
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao gerar relatório com IA: {e}")
                        st.info("""
                        **Possíveis causas:**
                        - Limite de requisições da API excedido
                        - Problema de conectividade
                        - API key inválida
                        
                        Tente novamente em alguns instantes.
                        """)
            
            # Exibir relatório se existir
            if st.session_state.ai_report:
                st.markdown("---")
                
                # Cabeçalho do relatório
                st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 1.5rem;
                            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                    <h2 style="margin: 0; color: white; font-size: 1.8rem;">🤖 Relatório de Análise Técnica com IA</h2>
                    <p style="margin: 0.5rem 0 0 0; font-size: 1rem; opacity: 0.95;">
                        Powered by Google Gemini 2.0 Flash
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Métricas visuais rápidas (se disponível)
                if 'ai_report_data' in st.session_state:
                    data = st.session_state.ai_report_data
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric(
                            label="💰 Preço Atual",
                            value=f"R$ {data['preco']:.2f}",
                            delta=f"{data['variacao']:.2f}%"
                        )
                    
                    with col2:
                        rsi_color = "🔴" if data['rsi'] > 70 else "🟢" if data['rsi'] < 30 else "🟡"
                        st.metric(
                            label=f"{rsi_color} RSI (14)",
                            value=f"{data['rsi']:.1f}",
                            delta=data['sinal_rsi']
                        )
                    
                    with col3:
                        macd_emoji = "📈" if data['sinal_macd'] == "Alta" else "📉"
                        st.metric(
                            label=f"{macd_emoji} MACD",
                            value=data['sinal_macd'],
                            delta=None
                        )
                    
                    with col4:
                        st.metric(
                            label="📊 Volatilidade",
                            value=f"{data['volatilidade']:.1f}%",
                            delta=None
                        )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                
                # Relatório em container estilizado
                st.markdown("""
                <div style="background: #f8f9fa; padding: 2rem; border-radius: 10px; 
                            border-left: 5px solid #667eea; margin-bottom: 1.5rem;">
                """, unsafe_allow_html=True)
                
                st.markdown(st.session_state.ai_report)
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Disclaimer em destaque
                st.markdown("""
                <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            padding: 1rem; border-radius: 10px; color: white; margin: 1.5rem 0;">
                    <h4 style="margin: 0 0 0.5rem 0; color: white;">⚠️ Disclaimer Importante</h4>
                    <p style="margin: 0; font-size: 0.9rem; line-height: 1.6;">
                        Este relatório foi gerado por inteligência artificial (Google Gemini) com base em dados 
                        técnicos históricos. As análises e recomendações são <strong>apenas educacionais</strong> e 
                        <strong>não constituem aconselhamento financeiro</strong>. Sempre consulte um profissional 
                        certificado antes de tomar decisões de investimento. O mercado financeiro envolve riscos significativos.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Informações adicionais
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    if st.session_state.ai_report_timestamp:
                        st.caption(f"📅 Relatório gerado em: {st.session_state.ai_report_timestamp.strftime('%d/%m/%Y às %H:%M:%S')}")
                
                with col2:
                    if st.button("🗑️ Limpar Relatório", key="clear_report", use_container_width=True):
                        st.session_state.ai_report = None
                        st.session_state.ai_report_timestamp = None
                        if 'ai_report_data' in st.session_state:
                            del st.session_state.ai_report_data
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro: {e}")


# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p><strong>PredictFinance v2.0</strong></p>
    <p>Desenvolvido por ArgusPortal | Powered by LSTM Neural Networks</p>
    <p>⚠️ Disclaimer: Este sistema é apenas para fins educacionais e de pesquisa.
    Não deve ser usado como única base para decisões de investimento.</p>
</div>
""", unsafe_allow_html=True)
