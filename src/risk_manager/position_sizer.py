import polars as pl
from typing import Union

class RiskManager:
    """Motor de gestión de riesgo profesional (Capa 4)."""
    
    def __init__(self, account_balance: float, max_risk_per_trade: float = 0.01):
        # Sincronizado con los argumentos que envía el main.py
        self.balance = account_balance
        self.max_risk_pct = max_risk_per_trade 
        self.max_exposure_pct = 0.05  # 5% máximo de la cuenta por trade
        self.active_exposure = 0.0

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calcula cuántas unidades comprar basándose en el riesgo.
        Fórmula: Unidades = (Capital * %Riesgo) / (Distancia al Stop Loss)
        """
        # 1. Distancia al Stop Loss
        stop_distance = abs(entry_price - stop_loss)
        
        if stop_distance <= 0:
            print("⚠️ Distancia de Stop Loss inválida.")
            return 0.0

        # 2. Monto de dinero en riesgo (Ej: $10,000 * 0.005 = $50)
        amount_to_risk = self.balance * self.max_risk_pct
        
        # 3. Cálculo de unidades
        units = amount_to_risk / stop_distance
        total_notional_value = units * entry_price
        
        # 4. Validación de exposición máxima (Capa de seguridad)
        max_allowed_value = self.balance * self.max_exposure_pct
        if total_notional_value > max_allowed_value:
            units = max_allowed_value / entry_price
            print(f"⚖️ Posición ajustada por límite de exposición (5% de la cuenta).")

        return float(units)

# --- Bloque de prueba cuantitativa ---
if __name__ == "__main__":
    # Test rápido para verificar que no hay errores de nombres
    rm = RiskManager(account_balance=10000, max_risk_per_trade=0.01)
    
    # Supongamos BTC a $60,000 con un SL a $59,500 (distancia de $500)
    unidades = rm.calculate_position_size(entry_price=60000, stop_loss=59500)
    
    print(f"--- Smoke Test RiskManager ---")
    print(f"Unidades a comprar: {unidades:.6f} BTC")
    print(f"Valor total de la posición: ${unidades * 60000:.2f}")