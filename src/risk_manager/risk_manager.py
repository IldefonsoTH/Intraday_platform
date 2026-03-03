class RiskManager:
    """
    Motor de Gestión de Riesgo (Capa 4).
    Controla el tamaño de posición y la exposición máxima.
    """
    def __init__(self, account_balance: float, max_risk_per_trade: float = 0.01):
        # Aseguramos que los nombres coincidan con lo que pide el Main
        self.balance = account_balance
        self.max_risk_pct = max_risk_per_trade  # Ej: 0.005 para 0.5%
        self.max_exposure_pct = 0.05            # 5% máximo de la cuenta en una sola operación
        self.active_exposure = 0.0              # Para control de varias posiciones

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calcula el tamaño de la posición en unidades (BTC).
        Devuelve un FLOAT para que el 'if pos_size > 0' del main funcione.
        """
        # 1. Validar si ya estamos muy expuestos
        if self.active_exposure >= self.max_exposure_pct:
            print("🚨 Riesgo bloqueado: Exposición máxima alcanzada.")
            return 0.0

        # 2. Calcular cuánto dinero arriesgamos (ej: $10,000 * 0.005 = $50)
        risk_amount = self.balance * self.max_risk_pct
        
        # 3. Calcular distancia al Stop Loss
        stop_distance = abs(entry_price - stop_loss)

        if stop_distance <= 0:
            return 0.0

        # 4. Calcular unidades: Tamaño = Riesgo / Distancia
        position_size = risk_amount / stop_distance
        
        # 5. Verificación de seguridad: Que la posición no valga más que el capital total
        if (position_size * entry_price) > self.balance:
            position_size = self.balance / entry_price

        return float(position_size)