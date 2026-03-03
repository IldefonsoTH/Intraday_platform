import polars as pl
from pathlib import Path
from typing import Union
import datetime

class FeatureProcessor:
    """Clase para transformar datos crudos en indicadores cuantitativos."""
    
    def __init__(self, raw_path: str = "data/raw", processed_path: str = "data/processed"):
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)
        self.processed_path.mkdir(parents=True, exist_ok=True)

    def calculate_indicators(self, data_input: Union[str, pl.DataFrame]) -> pl.DataFrame:
        """
        Calcula indicadores técnicos. Acepta nombre de archivo o DataFrame.
        """
        # 1. Validación de Entrada
        if isinstance(data_input, str):
            df = pl.read_parquet(self.raw_path / data_input)
            base_name = data_input
        elif isinstance(data_input, pl.DataFrame):
            df = data_input
            base_name = f"live_{datetime.datetime.now().strftime('%H%M%S')}.parquet"
        else:
            raise TypeError("La entrada debe ser un string (ruta) o un DataFrame de Polars.")

        # --- Pipeline de Cálculo Vectorizado ---

        # 2. TR y ATR (Volatilidad para Gestión de Riesgo)
        # Calculamos el True Range y el ATR en un solo bloque eficiente
        df = df.with_columns([
            pl.max_horizontal([
                (pl.col("High") - pl.col("Low")),
                (pl.col("High") - pl.col("Close").shift(1)).abs(),
                (pl.col("Low") - pl.col("Close").shift(1)).abs()
            ]).alias("TR")
        ]).with_columns([
            pl.col("TR").rolling_mean(window_size=14).alias("ATR")
        ])

        # 3. RSI y SMA_200 (Filtros de Señal)
        # Optimizamos el RSI usando expresiones puras de Polars para evitar errores de alineación
        df = df.with_columns([
            pl.col("Close").rolling_mean(window_size=200).alias("SMA_200"),
            (pl.col("Close").diff()).alias("diff")
        ]).with_columns([
            pl.when(pl.col("diff") >= 0).then(pl.col("diff")).otherwise(0).alias("gain"),
            pl.when(pl.col("diff") < 0).then(pl.col("diff").abs()).otherwise(0).alias("loss")
        ]).with_columns([
            (100 - (100 / (1 + (pl.col("gain").rolling_mean(14) / (pl.col("loss").rolling_mean(14) + 1e-9))))).alias("RSI")
        ]).drop(["diff", "gain", "loss"]) # Limpiamos columnas temporales

        # 4. Limpieza y Persistencia
        df = df.drop_nulls()
        output_file = self.processed_path / f"processed_{base_name}"
        df.write_parquet(output_file)
        
        print(f"✅ Features calculadas y guardadas: {output_file.name}")
        return df