import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load secrets from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

def load_settings():
    """Loads configuration from settings.yaml."""
    settings_path = BASE_DIR / "config" / "settings.yaml"
    if not settings_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {settings_path}")
    
    with open(settings_path, "r") as f:
        return yaml.safe_load(f)

# Load settings
_settings = load_settings()

class Config:
    # Secrets (from .env)
    MT5_LOGIN = int(os.getenv("MT5_LOGIN", 0))
    MT5_PASSWORD = os.getenv("MT5_PASSWORD", "")
    MT5_SERVER = os.getenv("MT5_SERVER", "")
    MT5_PATH = os.getenv("MT5_PATH", "")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Trading Settings (from settings.yaml)
    TRADING_PAIRS = _settings.get("trading", {}).get("pairs", [])
    TIMEFRAME = _settings.get("trading", {}).get("timeframe", "M1")
    MAGIC_NUMBER = _settings.get("trading", {}).get("magic_number", 123456)

    # Risk Settings
    MAX_DAILY_LOSS_PERCENT = _settings.get("risk", {}).get("max_daily_loss_percent", 4.0)
    RISK_PER_TRADE_PERCENT = _settings.get("risk", {}).get("risk_per_trade_percent", 0.5)
    MAX_OPEN_TRADES = _settings.get("risk", {}).get("max_open_trades", 1)

    # System Settings
    LOG_LEVEL = _settings.get("system", {}).get("log_level", "INFO")
    LOOP_INTERVAL = _settings.get("system", {}).get("loop_interval_seconds", 1)
    DRY_RUN = _settings.get("system", {}).get("dry_run", False)

    @classmethod
    def validate(cls):
        """
        Strictly validates that all required configuration is present.
        Raises ValueError if any critical config is missing.
        """
        missing_secrets = []
        if not cls.MT5_LOGIN:
            missing_secrets.append("MT5_LOGIN")
        if not cls.MT5_PASSWORD:
            missing_secrets.append("MT5_PASSWORD")
        if not cls.MT5_SERVER:
            missing_secrets.append("MT5_SERVER")
        if not cls.MT5_PATH:
            missing_secrets.append("MT5_PATH")
        if not cls.TELEGRAM_TOKEN:
            missing_secrets.append("TELEGRAM_TOKEN")
        
        if missing_secrets:
            raise ValueError(
                f"Missing critical SECRETS in .env file: {', '.join(missing_secrets)}. "
                "Please copy .env.example to .env and fill in real values."
            )

        missing_settings = []
        if not cls.TRADING_PAIRS:
            missing_settings.append("trading.pairs")
        if not cls.MAX_DAILY_LOSS_PERCENT:
            missing_settings.append("risk.max_daily_loss_percent")
            
        if missing_settings:
            raise ValueError(
                f"Missing critical SETTINGS in settings.yaml: {', '.join(missing_settings)}."
            )

        print("[Config] Validation Successful.")

# Usage: 
# from config.config import Config
# Config.validate()
