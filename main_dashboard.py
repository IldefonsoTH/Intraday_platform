import streamlit as st
import polars as pl
import plotly.graph_objects as fgo
from pathlib import Path
from src.strategies.base_strategy import VWAPPullback
from src.risk_manager.position_sizer import RiskManager
from src.backtester.engine import BacktestEngine

st.set_page_config(page_title="Intraday Intelligence Platform", layout="wide")
st.title("📊 Research & Backtesting Dashboard")

PROCESSED_PATH = Path("data/processed")

# --- BARRA LATERAL: Configuración ---
st.sidebar.header("1. Datos")
files = [f.name for f in PROCESSED_PATH.glob("*.parquet")]
selected_file = st.sidebar.selectbox("Selecciona un activo:", files)

st.sidebar.header("2. Parámetros de Riesgo")
capital_init = st.sidebar.number_input("Capital Inicial ($)", value=10000)
risk_pct = st.sidebar.slider("% Riesgo por Trade", 0.1, 2.0, 0.5) / 100 # Bajamos a 0.5% por prudencia

# --- CUERPO PRINCIPAL ---
if selected_file:
    df = pl.read_parquet(PROCESSED_PATH / selected_file)
    
    # Ejecución automática de Estrategia y Backtest
    strategy = VWAPPullback()
    df_signals = strategy.generate_signals(df)
    
    rm = RiskManager(total_capital=capital_init, risk_per_trade=risk_pct)
    engine = BacktestEngine(initial_capital=capital_init, commission=0.001)
    results_df = engine.run(df_signals, rm)

    # --- MÉTRICAS ---
    m1, m2, m3, m4 = st.columns(4)
    color_retorno = "normal" if engine.capital >= capital_init else "inverse"
    m1.metric("Capital Final", f"${engine.capital:.2f}")
    m2.metric("Total Trades", len(engine.trades))
    m3.metric("Retorno %", f"{((engine.capital/capital_init)-1)*100:.2f}%", delta_color=color_retorno)
    m4.metric("Varianza (ATR Medid)", f"{df['ATR'].mean():.2f}")

    # --- GRÁFICOS ---
    tab1, tab2 = st.tabs(["Precio y Señales", "Curva de Equidad"])
    
    with tab1:
        fig_price = fgo.Figure()
        fig_price.add_trace(fgo.Candlestick(x=df["Datetime"], open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Precio"))
        fig_price.add_trace(fgo.Scatter(x=df["Datetime"], y=df["VWAP"], line=dict(color='orange', width=2), name="VWAP"))
        fig_price.update_layout(height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        fig_equity = fgo.Figure()
        fig_equity.add_trace(fgo.Scatter(y=engine.equity_curve, mode='lines', fill='tozeroy', name='Equity', line=dict(color='blue')))
        fig_equity.update_layout(title="Evolución del Capital en el tiempo", height=400)
        st.plotly_chart(fig_equity, use_container_width=True)

else:
    st.info("Por favor, selecciona un archivo procesado en la barra lateral.")