import csv
import os
from datetime import datetime

class TradeLogger:
    """Auditor de señales para análisis de rendimiento (Capa 5)."""
    
    def __init__(self, file_path: str = "data/trade_log.csv"):
        self.file_path = file_path
        self._prepare_log()

    def _prepare_log(self):
        """Crea el archivo con encabezados si no existe."""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            with open(self.file_path, mode='w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Symbol", "Signal", "Entry_Price", 
                    "Stop_Loss", "Take_Profit", "RSI_Value"
                ])

    def log_signal(self, symbol: str, signal: str, price: float, sl: float, tp: float, rsi: float, atr: float):
        """Registra una nueva señal en el CSV."""
        with open(self.file_path, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                symbol,
                signal.upper(),
                round(price, 2),
                round(sl, 2),
                round(tp, 2),
                round(rsi, 2),
                round(atr, 4)
            ])