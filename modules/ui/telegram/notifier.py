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
            logger.error(f"Failed to send Telegram notification: {e}", extra={"is_telegram": True})

class TelegramLogHandler(logging.Handler):
    """
    Custom Logging Handler to forward ERRORS to Telegram.
    """
    def emit(self, record):
        # Prevent infinite loops if telegram itself errors
        if getattr(record, "is_telegram", False):
            return
            
        try:
            msg = self.format(record)
            if record.levelno >= logging.ERROR:
                # Add Emoji based on level
                prefix = "⚠️ <b>WARNING</b>" if record.levelno == logging.WARNING else "🚨 <b>SYSTEM ERROR</b>"
                if record.levelno >= logging.CRITICAL:
                    prefix = "🔥 <b>CRITICAL FAILURE</b>"
                
                formatted_msg = f"{prefix}\n<pre>{msg}</pre>"
                TelegramNotifier.send(formatted_msg)
        except Exception:
            self.handleError(record)
