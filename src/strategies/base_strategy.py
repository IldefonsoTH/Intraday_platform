from abc import ABC, abstractmethod
import polars as pl

class BaseStrategy(ABC):
    """Interfaz abstracta para todas las estrategias de la plataforma."""
    
    @abstractmethod
    def generate_signals(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Debe devolver un DataFrame con una columna 'Signal':
        1: Long, -1: Short, 0: None
        """
        pass

class VWAPPullback(BaseStrategy):
    """
    Estrategia de retroceso al VWAP.
    Filtros: SMA 200 (Tendencia) y RSI (Fuerza/Agotamiento).
    """
    
    def generate_signals(self, df: pl.DataFrame) -> pl.DataFrame:
        df = df.with_columns([
            pl.when(
                (pl.col("Close") > pl.col("VWAP")) & 
                (pl.col("Close").shift(1) <= pl.col("VWAP").shift(1)) &
                (pl.col("Close") > pl.col("SMA_200")) &
                (pl.col("RSI") < 60)  # 🛡️ No compramos si está sobrecomprado
            )
            .then(1)
            .when(
                (pl.col("Close") < pl.col("VWAP")) & 
                (pl.col("Close").shift(1) >= pl.col("VWAP").shift(1)) &
                (pl.col("Close") < pl.col("SMA_200")) &
                (pl.col("RSI") > 40)  # 🛡️ No vendemos si está sobrevendido
            )
            .then(-1)
            .otherwise(0)
            .alias("Signal")
        ])
        return df