import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config.config import Config
from modules.ui.telegram.handlers import register_handlers

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.allowed_chat_id = str(Config.TELEGRAM_CHAT_ID)
        self.app = None

    async def whitelist_middleware(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Security Middleware: Rejects messages from unauthorized users.
        """
        if not update.effective_chat:
            return
            
        chat_id = str(update.effective_chat.id)
        if chat_id != self.allowed_chat_id:
            logger.warning(f"Unauthorized access attempt from {chat_id}")
            # Silently ignore or maybe send "Access Denied" if you want
            return 
            
        # If authorized, handlers will process it naturally.
        # Note: PTB doesn't have "middleware" in the express/flask sense easily.
        # We usually use a Filter.
        pass

    def run(self):
        """
        Starts the polling loop.
        Note: This blocks! Should be run in a separate thread or process.
        """
        if not self.token:
            logger.error("Telegram Token not set. Bot disabled.")
            return

        self.app = ApplicationBuilder().token(self.token).build()

        # Add Security Filter to all handlers
        # We'll create a generic filter
        whitelist_filter = filters.Chat(chat_id=int(self.allowed_chat_id))

        # Register all command handlers
        register_handlers(self.app, whitelist_filter)

        logger.info("Telegram Bot Polling Started...")
        
        # Explicitly create loop for this thread (Required for threading.Thread)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.app.run_polling()
