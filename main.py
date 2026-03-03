import polars as pl
import datetime
import time
import os
from src.data_loader.downloader import DataDownloader
from src.processors.feature_engineering import FeatureProcessor
from src.strategies.rsi_strategy import RSISymbolicStrategy
from src.risk_manager.position_sizer import RiskManager
from src.alerts.telegram_provider import TelegramNotifier
from src.alerts.chart_generator import ChartGenerator
from src.alerts.trade_logger import TradeLogger

def run_live_pipeline(ticker: str):
    # --- CONFIGURACIÓN DE ACCESO ---
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    # 0. INICIALIZACIÓN DE SEGURIDAD
    signal = None
    entry_price = 0.0
    sl = 0.0
    tp = 0.0
    
    # 1. Ingesta (Capa 1)
    downloader = DataDownloader()
    raw_data = downloader.fetch_history(ticker, interval="5m", period="1d")
    
    # 2. Procesamiento (Capa 2)
    processor = FeatureProcessor()
    df_processed = processor.calculate_indicators(raw_data) 
    
    # 3. Estrategia con Filtro SMA_200 (Capa 3)
    strategy = RSISymbolicStrategy(rsi_overbought=70, rsi_oversold=30)
    signal, entry_price, sl, tp = strategy.generate_signal(df_processed)
    
    # # --- BLOQUE DE PRUEBA SINTÉTICA (Forzado para validar Gráficos) ---
    # if not signal:
    #     print(f"🧪 Forzando señal de prueba para {ticker}...")
    #     signal = "long"
    #     entry_price = df_processed['Close'][-1]
    #     sl = entry_price * 0.98  # Stop Loss al 2%
    #     tp = entry_price * 1.05  # Take Profit al 5%
    # # -----------------------------------------------------------------

    # 4. Gestión de Riesgo (Capa 4)
    rm = RiskManager(account_balance=10000.0, max_risk_per_trade=0.005)    

    # 5. Notificación con Soporte Visual (Capa 6)
    if signal:
        pos_size = rm.calculate_position_size(entry_price, sl)
        
        if isinstance(pos_size, (int, float)) and pos_size > 0:
            print(f"🎨 Generando gráfico para {ticker}...")
            # A. Generar el gráfico técnico
            chart_gen = ChartGenerator()
            chart_file = chart_gen.generate_signal_chart(df_processed, ticker, signal)
            
            # B. Enviar notificación completa (Imagen + Texto)
            notifier = TelegramNotifier(token=TOKEN, chat_id=CHAT_ID)
            notifier.send_signal(
                symbol=ticker,
                signal_type=signal,
                price=entry_price,
                sl=sl,
                tp=tp,
                risk_pct=0.5,
                chart_path=chart_file
            )
            print(f"🚀 {datetime.datetime.now()} - ALERTA VISUAL ENVIADA: {ticker} ({signal})")
        else:
            print(f"⚠️ Señal {signal} para {ticker} bloqueada por gestión de riesgo.")
        
        # C. REGISTRO EN LOG DE AUDITORÍA
        logger = TradeLogger()
        # Obtenemos el RSI actual para el log
        current_rsi = df_processed['RSI'][-1]
        
        logger.log_signal(
            symbol=ticker,
            signal=signal,
            price=entry_price,
            sl=sl,
            tp=tp,
            rsi=current_rsi
        )
    else:
        # Esto solo se ejecutaría si quitaras el bloque de prueba sintética
        ultimo_rsi = df_processed['RSI'][-1]
        print(f"😴 {datetime.datetime.now()} - {ticker}: Sin ventaja (RSI: {ultimo_rsi:.2f})")

if __name__ == "__main__":
    # Cargamos las variables desde el entorno (GitHub Secrets)
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    
    watchlist = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "AVAX-USD"]
    
    print(f"🕒 Ejecución programada: {datetime.datetime.now()}")
    for ticker in watchlist:
        try:
            run_live_pipeline(ticker)
        except Exception as e:
            print(f"❌ Error en {ticker}: {e}")
    
    # IMPORTANTE: No usamos while True en GitHub Actions. 
    # El script termina y GitHub lo reinicia según el cron.