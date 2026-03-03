import yfinance as yf
import polars as pl
from pathlib import Path
from datetime import datetime
from typing import Optional

class DataDownloader:
    """Clase para gestionar la descarga y guardado de datos históricos[cite: 10]."""
    
    def __init__(self, storage_path: str = "data/raw"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def fetch_history(self, ticker: str, interval: str = "1m", period: str = "5d") -> Optional[pl.DataFrame]:
        """
        Descarga datos de Yahoo Finance y los convierte a formato Polars.
        Intervalos válidos: 1m, 5m, 15m[cite: 10].
        """
        try:
            print(f"Descargando {ticker} (intervalo: {interval})...")
            df_raw = yf.download(ticker, period=period, interval=interval, progress=False)
            
            if df_raw.empty:
                print(f"⚠️ No se encontraron datos para {ticker}")
                return None
            
            # NORMALIZACIÓN: Quitamos el MultiIndex de Yahoo Finance
            df_raw.columns = [col[0] if isinstance(col, tuple) else col for col in df_raw.columns]
            df_raw = df_raw.reset_index()
            
            # Convertimos a Polars
            df = pl.from_pandas(df_raw)
            
            # Guardamos en formato Parquet para máxima eficiencia 
            filename = f"{ticker}_{interval}_{datetime.now().strftime('%Y%m%d')}.parquet"
            save_path = self.storage_path / filename
            df.write_parquet(save_path)
            
            print(f"✅ Guardado exitoso: {save_path}")
            return df

        except Exception as e:
            print(f"❌ Error en la descarga: {e}")
            return None

# --- Bloque de prueba ---
if __name__ == "__main__":
    downloader = DataDownloader()
    # Probamos con Bitcoin por su alta volatilidad intradía
    data = downloader.fetch_history("BTC-USD", interval="5m", period="5d")