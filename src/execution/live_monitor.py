import time
import datetime
import polars as pl
from src.data_loader.downloader import DataDownloader
from src.processors.feature_engineering import FeatureProcessor
from src.strategies.base_strategy import VWAPPullback
from src.risk_manager.position_sizer import RiskManager

class LiveMonitor:
    def __init__(self, ticker: str, capital: float = 10000.0):
        self.ticker = ticker
        self.capital = capital
        self.downloader = DataDownloader()
        self.processor = FeatureProcessor()
        self.strategy = VWAPPullback()
        self.rm = RiskManager(total_capital=capital, risk_per_trade=0.005)

    def check_market(self):
        print(f"\n🔍 [{datetime.datetime.now().strftime('%H:%M:%S')}] Analizando {self.ticker}...")
        
        # 1. Descarga ultra rápida de los últimos datos
        # Usamos 1 día para tener suficiente historial para la SMA 200
        df_raw = self.downloader.fetch_history(self.ticker, interval="5m", period="1d")
        
        # 2. Procesar indicadores
        # Nota: Adaptamos calculate_indicators si es necesario para recibir DF directamente
        # Por ahora usamos el flujo de archivos que ya tenemos
        import glob
        import os
        list_of_files = glob.glob('data/raw/*.parquet')
        latest_file = max(list_of_files, key=os.path.getctime)
        
        df_processed = self.processor.calculate_indicators(latest_file.split('\\')[-1])
        
        # 3. Generar señal sobre la ÚLTIMA vela cerrada
        df_signals = self.strategy.generate_signals(df_processed)
        last_candle = df_signals.tail(1).to_dicts()[0]
        
        signal = last_candle["Signal"]
        price = last_candle["Close"]
        
        if signal != 0:
            plan = self.rm.calculate_position_size(price, last_candle["ATR"])
            self.alert(signal, price, plan)
        else:
            print(f"😴 Sin señales. Precio actual: ${price:.2f} | RSI: {last_candle['RSI']:.2f}")

    def alert(self, signal, price, plan):
        side = "🟢 COMPRA (LONG)" if signal == 1 else "🔴 VENTA (SHORT)"
        print("="*40)
        print(f"🚨 ¡SEÑAL DETECTADA EN {self.ticker}! 🚨")
        print(f"Tipo: {side}")
        print(f"Precio Entrada: ${price:.2f}")
        print(f"TP Sugerido: ${plan['take_profit_price']}")
        print(f"SL Sugerido: ${plan['stop_loss_price']}")
        print(f"Tamaño Posición: {plan['units']} unidades")
        print(f"Riesgo Operación: ${plan['risk_amount']}")
        print("="*40)

    def start(self):
        print(f"🚀 Iniciando Monitor en Vivo para {self.ticker}...")
        while True:
            try:
                self.check_market()
                # Esperamos 5 minutos para la siguiente vela
                # Optimización: esperar hasta el próximo múltiplo de 5 min
                time.sleep(300) 
            except KeyboardInterrupt:
                print("\n🛑 Monitor detenido por el usuario.")
                break
            except Exception as e:
                print(f"❌ Error en el monitor: {e}")
                time.sleep(60)

if __name__ == "__main__":
    monitor = LiveMonitor("BTC-USD")
    monitor.start()