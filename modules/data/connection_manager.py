import logging
import time
from config.config import Config
from modules.data.mt5_loader import MT5

logger = logging.getLogger(__name__)

class ConnectionManager:
    @staticmethod
    def initialize():
        """
        Initializes the connection to MetaTrader 5.
        Returns:
            bool: True if successful, False otherwise.
        """
        # If path is specified and we are on Windows (checked indirectly by MT5 load), 
        # normally we would pass path to initialize. 
        # The Mock accepts arguments so this is safe.
        
        # 1. Initialize Terminal
        if not MT5.initialize(path=Config.MT5_PATH):
            logger.error(f"MT5 Initialize failed, error code = {MT5.last_error()}")
            return False

        # 2. Login
        authorized = MT5.login(
            login=Config.MT5_LOGIN, 
            password=Config.MT5_PASSWORD, 
            server=Config.MT5_SERVER
        )
        
        if authorized:
            logger.info(f"Connected to MT5 account #{Config.MT5_LOGIN}")
        else:
            logger.error(f"MT5 Login failed, error code = {MT5.last_error()}")
            MT5.shutdown()
            return False

        return True

    @staticmethod
    def shutdown():
        """Shuts down the MT5 connection."""
        MT5.shutdown()
        logger.info("MT5 connection shut down.")

    @staticmethod
    def ensure_connected():
        """
        Checks connection status and attempts to reconnect if dropped.
        Returns:
            bool: True if connected.
        """
        info = MT5.terminal_info()
        if info is None or not info.connected:
            logger.warning("MT5 connection lost. Attempting reconnect...")
            return ConnectionManager.initialize()
        return True
