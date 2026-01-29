from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass(frozen=True)
class TradeContext:
    """
    Immutable snapshot of the market environment and internal state
    at a specific point in time (usually candle close).
    """
    # Market Data
    symbol: str
    timestamp: datetime
    current_price: float
    spread: float
    
    # Internal State
    session_name: str
    is_news_event: bool
    
    # Technicals (Snapshot)
    indicators: Dict[str, float]
    market_regime: str  # e.g. "TREND_UP", "RANGE", "UNDEFINED"
    
    # Strategy State
    trend_bias: str  # "LONG", "SHORT", "NEUTRAL"
    cooldown_remaining: int
    pullback_candles: int
    
    # Risk State
    risk_status: Dict[str, Any]  # e.g. {'can_trade': True, 'daily_pnl': 500.0}

    # Helper to check validity (though data structure serves as data holder mainly)
    def __repr__(self):
        return (f"TradeContext({self.symbol} @ {self.timestamp}, "
                f"Regime={self.market_regime}, Bias={self.trend_bias})")
