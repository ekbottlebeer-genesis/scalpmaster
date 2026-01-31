import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from config.config import Config
from modules.ui.telegram.handlers import register_handlers

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, engine=None):
        self.token = Config.TELEGRAM_TOKEN
        self.allowed_chat_id = str(Config.TELEGRAM_CHAT_ID)
        self.app = None
        self.engine = engine



    async def post_init(self, application):
        """
        Post-initialization hook to set bot data and commands.
        """
        # Store engine in bot_data for commands to access
        application.bot_data["engine"] = self.engine
        
        # Set Menu Commands
        commands_list = [
            ("status", "System Overview & PnL"),
            ("scan", "Force Market Scan"),
            ("panic", "🚨 CLOSE ALL TRADES"),
            ("mode", "Show Current Mode"),
            ("news", "Check News Status"),
            ("risk", "View/Set Risk Settings"),
            ("help", "Show All Commands")
        ]
        await application.bot.set_my_commands(commands_list)
        logger.info("Telegram Menu Commands Registered.")

    def run(self):
        """
        Starts the polling loop.
        Note: This blocks! Should be run in a separate thread or process.
        """
        if not self.token:
            logger.error("Telegram Token not set. Bot disabled.")
            return

        self.app = ApplicationBuilder().token(self.token).post_init(self.post_init).build()

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
