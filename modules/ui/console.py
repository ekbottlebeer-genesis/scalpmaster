import logging
import sys
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsoleUI:
    """
    Handles pretty terminal output for the ScalpMaster dashboard.
    """
    
    @staticmethod
    def print_header(count: int, timestamp: datetime):
        print(f"\n🔍 Scanning {count} assets at {timestamp.strftime('%H:%M:%S')}...")
        print("-" * 60)

    @staticmethod
    def print_row(symbol: str, bias: str, rsi: float, status: str, error: bool = False):
        """
        Prints a formatted row.
        Example: 📊 BTCUSDT: SHORT | RSI: 66.0 | Wait Pullback...
        """
        icon = "📊"
        if error:
            icon = "⚠️"
        elif "TRADE FOUND" in status or "ZONE" in status:
            icon = "🔥"
        
        # Simple ASCII formatting
        # Using simple print to avoid logger prefixes for dashboard view
        # We assume bias/status are short text
        # truncating floats
        
        row = f"   {icon} {symbol:<7}: {bias:<5} | RSI: {rsi:.1f} | {status}"
        print(row)
        
    @staticmethod
    def print_section_end():
        print("") # Newline
