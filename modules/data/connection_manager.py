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
            err_code = MT5.last_error()
            logger.error(f"MT5 Initialize failed, error code = {err_code}")
            
            if "10003" in str(err_code) or err_code == -10003:
                logger.critical("Error -10003: INVALID MT5 PATH.")
                logger.critical(f"Please check 'MT5_PATH' in your .env file. Current value: '{Config.MT5_PATH}'")
                logger.critical("Ensure it points to the 'terminal64.exe' file, NOT just the folder.")
            
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
