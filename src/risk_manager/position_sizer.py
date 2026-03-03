import polars as pl
from typing import Union, Tuple

class RiskManager:
    """Motor de gestión de riesgo profesional con ATR Adaptativo (Capa 4)."""
    
    def __init__(self, account_balance: float, max_risk_per_trade: float = 0.01):
        self.balance = account_balance
        self.max_risk_pct = max_risk_per_trade 
        self.max_exposure_pct = 0.10  # Subimos a 10% para dar más margen a cripto
        self.atr_multiplier = 2.0     # Cuántas veces el ATR alejamos el Stop Loss
        self.reward_risk_ratio = 2.0  # Buscamos ganar 2 veces lo que arriesgamos

    def get_trade_levels(self, entry_price: float, atr: float, signal_type: str) -> Tuple[float, float]:
        """
        Calcula niveles de SL y TP basados en volatilidad (ATR).
        SL = Precio - (ATR * Multiplicador)
        TP = Precio + (Distancia_SL * RR_Ratio)
        """
        volatility_distance = atr * self.atr_multiplier
        
        if signal_type.upper() == "LONG":
            sl = entry_price - volatility_distance
            tp = entry_price + (volatility_distance * self.reward_risk_ratio)
        else: # SHORT
            sl = entry_price + volatility_distance
            tp = entry_price - (volatility_distance * self.reward_risk_ratio)
            
        return round(sl, 4), round(tp, 4)

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calcula el tamaño de la posición basándose en el riesgo monetario.
        """
        stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance <= 0:
            return 0.0

        # Dinero real que estamos dispuestos a perder (Ej: 1% de $10,000 = $100)
        amount_to_risk = self.balance * self.max_risk_pct
        
        # Unidades necesarias para que esa distancia equivalga a nuestro riesgo
        units = amount_to_risk / stop_distance
        total_notional_value = units * entry_price
        
        # Validación de exposición máxima (No invertir más del 10% del capital total en un solo trade)
        max_allowed_value = self.balance * self.max_exposure_pct
        if total_notional_value > max_allowed_value:
            units = max_allowed_value / entry_price
            # print(f"⚖️ Exposición limitada al 10% del balance.")

        return float(units)

# --- Bloque de prueba cuantitativa ---
if __name__ == "__main__":
    # Test con volatilidad: BTC a $60,000 con un ATR de $400
    rm = RiskManager(account_balance=10000, max_risk_per_trade=0.01)
    
    entry = 60000.0
    atr_val = 400.0 # El mercado se mueve $400 en promedio por vela
    
    sl, tp = rm.get_trade_levels(entry, atr_val, "LONG")
    unidades = rm.calculate_position_size(entry, sl)
    
    print(f"--- Smoke Test RiskManager (ATR Adaptativo) ---")
    print(f"Entrada: ${entry} | ATR: ${atr_val}")
    print(f"Stop Loss Sugerido (2xATR): ${sl}")
    print(f"Take Profit Sugerido (2:1): ${tp}")
    print(f"Unidades a comprar: {unidades:.6f} BTC")
    print(f"Riesgo real: ${abs(entry - sl) * unidades:.2f} (Debe ser approx $100)")