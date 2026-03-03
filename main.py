import polars as pl
import datetime
import os
from src.data_loader.downloader import DataDownloader
from src.processors.feature_engineering import FeatureProcessor
from src.strategies.rsi_strategy import RSISymbolicStrategy
from src.risk_manager.position_sizer import RiskManager
from src.alerts.telegram_provider import TelegramNotifier
from src.alerts.chart_generator import ChartGenerator
from src.alerts.trade_logger import TradeLogger

def run_live_pipeline(ticker: str):
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # 1. Ingesta (Capa 1)
    downloader = DataDownloader()
    raw_data = downloader.fetch_history(ticker, interval="5m", period="1d")
    
    # 2. Procesamiento (Capa 2) - Ahora incluye ATR
    processor = FeatureProcessor()
    df_processed = processor.calculate_indicators(raw_data) 
    
    # --- EXTRACCIÓN DE DATOS CLAVE ---
    last_row = df_processed.tail(1)
    current_price = last_row["Close"][0]
    current_rsi = last_row["RSI"][0]
    current_atr = last_row["ATR"][0] # <--- EXTRAEMOS EL ATR
    
    # 3. Estrategia (Capa 3)
    strategy = RSISymbolicStrategy(rsi_overbought=70, rsi_oversold=30)
    # Nota: Tu estrategia actual genera SL/TP internos, pero ahora usaremos el RM
    signal, entry_price, _, _ = strategy.generate_signal(df_processed)
    
    # 4. Gestión de Riesgo Adaptativa (Capa 4)
    rm = RiskManager(account_balance=10000.0, max_risk_per_trade=0.005)    

    if signal:
        # A. CALCULAMOS NIVELES DINÁMICOS CON EL ATR
        sl, tp = rm.get_trade_levels(current_price, current_atr, signal)
        
        # B. CALCULAMOS TAMAÑO DE POSICIÓN
        pos_size = rm.calculate_position_size(current_price, sl)
        
        if pos_size > 0:
            # C. GENERAR GRÁFICO
            chart_gen = ChartGenerator()
            chart_file = chart_gen.generate_signal_chart(df_processed, ticker, signal)
            
            # D. NOTIFICACIÓN TELEGRAM
            notifier = TelegramNotifier(token=TOKEN, chat_id=CHAT_ID)
            notifier.send_signal(
                symbol=ticker,
                signal_type=signal,
                price=current_price,
                sl=sl,
                tp=tp,
                risk_pct=0.5,
                chart_path=chart_file
            )
            
            # E. REGISTRO EN LOG (Ahora con ATR)
            logger = TradeLogger()
            logger.log_signal(
                symbol=ticker,
                signal=signal,
                price=current_price,
                sl=sl,
                tp=tp,
                rsi=current_rsi,
                atr=current_atr
            )
            print(f"🚀 {datetime.datetime.now()} - SEÑAL ATR ENVIADA: {ticker} ({signal})")
    else:
        print(f"😴 {datetime.datetime.now()} - {ticker}: Sin ventaja (RSI: {current_rsi:.2f} | ATR: {current_atr:.4f})")

if __name__ == "__main__":
    watchlist = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "AVAX-USD"]
    print(f"🕒 Ejecución programada con ATR: {datetime.datetime.now()}")
    for ticker in watchlist:
        try:
            run_live_pipeline(ticker)
        except Exception as e:
            print(f"❌ Error en {ticker}: {e}")