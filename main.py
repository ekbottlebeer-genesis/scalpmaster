import logging
import threading
import sys
import time

# Configure Logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

from config.config import Config
from core.bot import ScalpMasterBot
from modules.ui.telegram.bot import TelegramBot
from modules.ui.telegram.notifier import TelegramLogHandler

# Add Telegram Handler to Root Logger
tg_handler = TelegramLogHandler()
tg_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('%(name)s: %(message)s')
tg_handler.setFormatter(formatter)
logging.getLogger().addHandler(tg_handler)

logger = logging.getLogger("Main")

def main():
    logger.info("="*40)
    logger.info("   SCALPMASTER v1.2 - SYSTEM STARTUP   ")
    logger.info("="*40)

    # 1. Validate Config
    try:
        Config.validate()
    except ValueError as e:
        logger.critical(f"Configuration Error: {e}")
        return

    # 2. Initialize Components
    bot = ScalpMasterBot()
    telegram = TelegramBot(engine=bot)

    # 3. Start Telegram (Daemon Thread)
    # Critical Audit Fix: Prevent blocking main loop
    if Config.TELEGRAM_TOKEN:
        logger.info("Starting Telegram Bot (Background Service)...")
        ui_thread = threading.Thread(target=telegram.run, daemon=True)
        ui_thread.start()
    else:
        logger.warning("Telegram Token missing. UI disabled.")

    # 4. Start Strategy (Main Thread)
    logger.info("Starting Strategy Engine...")
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Shutdown Signal Received.")
        bot.stop()
    except Exception as e:
        logger.critical(f"Fatal System Error: {e}")
        bot.stop()
    
    logger.info("System Shutdown Complete.")

if __name__ == "__main__":
    main()
