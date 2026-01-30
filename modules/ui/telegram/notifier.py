import logging
import requests
from config.config import Config

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """
    Simple synchronous Telegram notifier using requests.
    Used for sending alerts from the main thread (Startup, Trade, Error).
    """
    
    @staticmethod
    def send(message: str):
        """
        Sends a message to the configured Telegram Chat.
        """
        token = Config.TELEGRAM_TOKEN
        chat_id = Config.TELEGRAM_CHAT_ID
        
        if not token or not chat_id:
            logger.warning("Telegram Notification skipped: Token or Chat ID missing.")
            return

        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
