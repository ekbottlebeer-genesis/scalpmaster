import logging

logger = logging.getLogger(__name__)

class PostTradeAdaptor:
    """
    Adjusts strategy thresholds based on feedback loop.
    Slowly adapts to market feedback (Win/Loss).
    """
    def __init__(self):
        # Default Thresholds
        self.min_adx = 25.0
        self.rsi_overbought = 70.0
        self.rsi_oversold = 30.0
        
        # Adaptation Step Sizes
        self.step_adx = 1.0
        self.step_rsi = 1.0
        
        # Limits
        self.max_adx = 35.0
        self.min_rsi_ob = 60.0
        self.max_rsi_ob = 85.0

    def update_thresholds(self, trade_result: float):
        """
        trade_result: PnL (+ve for win, -ve for loss)
        """
        if trade_result < 0:
            # Loss -> Tighten Up!
            # Demand stronger trend (Higher ADX)
            self.min_adx = min(self.min_adx + self.step_adx, self.max_adx)
            
            # Demand better RSI extremes? 
            # Or maybe just depend on trend.
            logger.info(f"Adaptor: Loss detected. Tightened Min ADX to {self.min_adx}")
            
        elif trade_result > 0:
            # Win -> Relax slightly (revert to mean/baseline)
            # But don't become too loose.
            self.min_adx = max(self.min_adx - (self.step_adx * 0.5), 20.0)
            logger.info(f"Adaptor: Win detected. Relaxed Min ADX to {self.min_adx}")

    def get_current_thresholds(self) -> dict:
        return {
            'min_adx': self.min_adx,
            'rsi_overbought': self.rsi_overbought,
            'rsi_oversold': self.rsi_oversold
        }
