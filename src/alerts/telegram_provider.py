import requests
import os

class TelegramNotifier:
    """Proveedor de notificaciones para Telegram (Capa 6)."""

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_signal(self, symbol: str, signal_type: str, price: float, sl: float, tp: float, risk_pct: float, chart_path: str = None):
        """
        Envía la señal de trading. Si se proporciona chart_path, envía una foto con caption.
        """
        # 1. Construir el mensaje formateado
        emoji = "🚀" if signal_type == "long" else "📉"
        message = (
            f"{emoji} **NUEVA SEÑAL: {symbol}**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"**Tipo:** {signal_type.upper()}\n"
            f"**Precio:** ${price:,.2f}\n"
            f"**SL:** ${sl:,.2f} | **TP:** ${tp:,.2f}\n"
            f"**Riesgo:** {risk_pct}%\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"⚠️ *Valida la estructura antes de entrar.*"
        )

        if chart_path and os.path.exists(chart_path):
            # Enviar como foto con el mensaje de pie de foto
            self._send_photo(chart_path, message)
        else:
            # Enviar solo como texto si no hay gráfico
            self._send_text(message)

    def _send_text(self, message: str):
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"❌ Error enviando texto a Telegram: {e}")

    def _send_photo(self, photo_path: str, caption: str):
        url = f"{self.base_url}/sendPhoto"
        try:
            with open(photo_path, "rb") as photo:
                payload = {"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"}
                files = {"photo": photo}
                requests.post(url, data=payload, files=files)
        except Exception as e:
            print(f"❌ Error enviando foto a Telegram: {e}")
            # Si falla la foto, enviamos al menos el texto
            self._send_text(caption)