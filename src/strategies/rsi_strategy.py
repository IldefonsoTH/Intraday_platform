import polars as pl
from typing import Tuple, Optional

class RSISymbolicStrategy:
    def __init__(self, rsi_overbought: int = 70, rsi_oversold: int = 30):
        self.upper = rsi_overbought
        self.lower = rsi_oversold

    def generate_signal(self, df: pl.DataFrame) -> Tuple[Optional[str], float, float, float]:
        """
        Analiza la última vela usando Polars nativo (Capa 3).
        """
        # Validamos que tengamos datos suficientes tras el drop_nulls() de la SMA_200
        if df.height < 2:
            return None, 0.0, 0.0, 0.0

        # Acceso ultra-rápido a los últimos valores
        # row(-1) nos da la vela actual, row(-2) la anterior
        current_row = df.row(-1, named=True)
        prev_row = df.row(-2, named=True)

        current_rsi = current_row["RSI"]
        prev_rsi = prev_row["RSI"]
        price = current_row["Close"]
        atr = current_row["ATR"]

        signal = None
        sl = 0.0
        tp = 0.0

        # Lógica: Cruce de salida de sobreventa (Bullish)
        if prev_rsi < self.lower and current_rsi >= self.lower:
            signal = "long"
            sl = price - (atr * 1.5)  # SL dinámico basado en volatilidad
            tp = price + (atr * 3.0)  # Ratio R/R 1:2 sugerido
        
        # Lógica: Cruce de salida de sobrecompra (Bearish)
        elif prev_rsi > self.upper and current_rsi <= self.upper:
            signal = "short"
            sl = price + (atr * 1.5)
            tp = price - (atr * 3.0)

        return signal, price, sl, tp