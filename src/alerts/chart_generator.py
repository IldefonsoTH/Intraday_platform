import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import polars as pl
import pandas as pd
import os
from datetime import datetime

class ChartGenerator:
    def __init__(self, output_dir: str = "data/charts"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # USAMOS UN ESTILO ESTÁNDAR PARA EVITAR ERRORES
        plt.style.use('ggplot')

    def generate_signal_chart(self, df: pl.DataFrame, ticker: str, signal_type: str) -> str:
        """Genera un gráfico de Precio y RSI y devuelve la ruta de la imagen."""
        
        # 1. Preparación de datos (Convertimos a Pandas solo para matplotlib)
        # Usamos las últimas 50 velas para que el gráfico sea legible
        plot_df = df.tail(50).to_pandas()
        plot_df['Datetime'] = pd.to_datetime(plot_df['Datetime'])
        
        # 2. Configuración del lienzo (2 subplots: Precio y RSI)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)
        fig.suptitle(f"📊 Señal Detectada: {ticker} - {signal_type.upper()}", fontsize=16, fontweight='bold')

        # --- PANEL 1: PRECIO Y SMA_200 ---
        color = 'green' if signal_type == 'long' else 'red'
        ax1.plot(plot_df['Datetime'], plot_df['Close'], label='Precio Cierre', color='black', alpha=0.7)
        ax1.plot(plot_df['Datetime'], plot_df['SMA_200'], label='SMA 200', color='orange', linestyle='--')
        
        # Marcar la vela de la señal
        last_candle = plot_df.iloc[-1]
        ax1.scatter(last_candle['Datetime'], last_candle['Close'], color=color, s=200, marker='^' if signal_type == 'long' else 'v', label='SEÑAL', zorder=5)
        
        ax1.set_ylabel('Precio ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # --- PANEL 2: RSI ---
        ax2.plot(plot_df['Datetime'], plot_df['RSI'], label='RSI (14)', color='purple')
        
        # Líneas de sobreventa/sobrecompra
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
        ax2.fill_between(plot_df['Datetime'], 70, 30, color='purple', alpha=0.1) # Zona neutral
        
        ax2.set_ylabel('RSI', fontsize=12)
        ax2.set_ylim(0, 100)
        ax2.grid(True, alpha=0.3)

        # Formateo del eje X (Fechas)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        # 3. Guardado de la imagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{ticker}_{signal_type}_{timestamp}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        plt.tight_layout(rect=[0, 0, 1, 0.97]) # Ajuste para el título
        plt.savefig(filepath, dpi=100)
        plt.close(fig) # Liberar memoria
        
        return filepath