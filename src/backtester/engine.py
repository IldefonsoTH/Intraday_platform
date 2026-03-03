import polars as pl
from src.risk_manager.position_sizer import RiskManager

import polars as pl
from src.risk_manager.position_sizer import RiskManager

import polars as pl
from src.risk_manager.position_sizer import RiskManager

class BacktestEngine:
    """Motor de simulación histórica con gestión de trayectoria de precios."""
    
    def __init__(self, initial_capital: float = 10000.0, commission: float = 0.001):
        self.capital = initial_capital
        self.equity_curve = [initial_capital]
        self.commission = commission
        self.trades = []
        self.active_position = None

    def run(self, df: pl.DataFrame, risk_manager: RiskManager):
        data = df.to_dicts()
        
        for i, row in enumerate(data):
            # 1. Búsqueda de señal
            if self.active_position is None:
                if row["Signal"] != 0:
                    price = row["Close"]
                    plan = risk_manager.calculate_position_size(price, row["ATR"])
                    
                    if plan["units"] > 0:
                        self.active_position = {
                            "type": row["Signal"],
                            "entry_price": price,
                            "units": plan["units"],
                            "sl": plan["stop_loss_price"],
                            "tp": plan["take_profit_price"],
                            "entry_date": row["Datetime"]
                        }
                        self.capital -= (plan["units"] * price * self.commission)

            # 2. Monitoreo de posición activa
            else:
                pos = self.active_position
                high, low = row["High"], row["Low"]
                
                # Lógica Trailing Stop
                if pos["type"] == 1: # LONG
                    if (high - pos["entry_price"]) > row["ATR"] and pos["sl"] < pos["entry_price"]:
                        pos["sl"] = pos["entry_price"]
                elif pos["type"] == -1: # SHORT
                    if (pos["entry_price"] - low) > row["ATR"] and pos["sl"] > pos["entry_price"]:
                        pos["sl"] = pos["entry_price"]

                exit_price = None
                result = None

                # Verificación de Salidas
                if pos["type"] == 1:
                    if low <= pos["sl"]:
                        exit_price = pos["sl"]
                        result = "SL/BE"
                    elif high >= pos["tp"]:
                        exit_price = pos["tp"]
                        result = "TP"
                elif pos["type"] == -1:
                    if high >= pos["sl"]:
                        exit_price = pos["sl"]
                        result = "SL/BE"
                    elif low <= pos["tp"]:
                        exit_price = pos["tp"]
                        result = "TP"

                if exit_price:
                    pnl = (exit_price - pos["entry_price"]) * pos["units"] if pos["type"] == 1 else (pos["entry_price"] - exit_price) * pos["units"]
                    pnl -= (pos["units"] * exit_price * self.commission)
                    
                    self.capital += pnl
                    self.equity_curve.append(self.capital)
                    self.trades.append({
                        "entry_date": pos["entry_date"],
                        "exit_date": row["Datetime"],
                        "result": result,
                        "pnl": pnl,
                        "final_capital": self.capital
                    })
                    self.active_position = None

        # --- 3. CIERRE FORZADO (FUERA DEL BUCLE FOR) ---
        if self.active_position:
            pos = self.active_position
            last_price = data[-1]["Close"]
            pnl = (last_price - pos["entry_price"]) * pos["units"] if pos["type"] == 1 else (pos["entry_price"] - last_price) * pos["units"]
            pnl -= (pos["units"] * last_price * self.commission)
            self.capital += pnl
            self.equity_curve.append(self.capital)
            self.trades.append({
                "entry_date": pos["entry_date"],
                "exit_date": data[-1]["Datetime"],
                "result": "LIQUIDADO",
                "pnl": pnl,
                "final_capital": self.capital
            })
            self.active_position = None

        print(f"--- Fin del Backtest Profesional ---")
        print(f"Capital Final: ${self.capital:.2f} | Trades: {len(self.trades)}")
        return pl.DataFrame(self.trades)

# --- Prueba del Motor ---
if __name__ == "__main__":
    # Cargamos datos procesados (asegúrate de que el nombre sea el correcto)
    df_test = pl.read_parquet("data/processed/processed_BTC-USD_5m_20260303.parquet")
    
    # Inyectamos señales de prueba (VWAP Pullback)
    from src.strategies.base_strategy import VWAPPullback
    strategy = VWAPPullback()
    df_with_signals = strategy.generate_signals(df_test)
    
    # Ejecutamos
    rm = RiskManager(total_capital=10000)
    engine = BacktestEngine()
    history = engine.run(df_with_signals, rm)