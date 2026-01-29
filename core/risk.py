import logging
from collections import deque
import time
from config.config import Config

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        # State
        self.daily_start_balance = 0.0
        self.current_daily_loss = 0.0
        self.loss_streak = 0
        self.win_streak = 0
        self.trades_today = 0
        self.cooldown_until = 0  # Timestamp
        self.is_hard_stopped = False
        
        # Hourly Limit Tracking
        self.trade_timestamps = deque() 
        self.max_trades_hourly = 10 # Hardcoded safety or Config

        # Config Shortcuts
        self.base_risk = Config.RISK_PER_TRADE_PERCENT  # e.g. 0.25 or 0.5
        self.max_daily_loss_pct = Config.MAX_DAILY_LOSS_PERCENT

    def snapshot_account(self, balance: float):
        """
        Called at start of day (00:00) to record initial balance.
        """
        self.daily_start_balance = balance
        self.current_daily_loss = 0.0
        self.trades_today = 0
        self.is_hard_stopped = False
        self.trade_timestamps.clear()
        logger.info(f"Daily Risk Snapshot: Start Balance = {balance}")

    def update_metrics(self, profit: float):
        """
        Called after a trade closes. Updates streaks and daily PnL.
        """
        self.trades_today += 1
        self.trade_timestamps.append(time.time())
        
        if profit < 0:
            self.loss_streak += 1
            self.win_streak = 0
        else:
            self.win_streak += 1
            self.loss_streak = 0

    def can_trade(self, current_equity: float, current_time_ts: float) -> tuple[bool, str]:
        """
        Checks hard kill switches.
        """
        if self.daily_start_balance <= 0:
            return False, "RISK_NOT_INITIALIZED"

        if self.is_hard_stopped:
            return False, "HARD_STOP_ACTIVE"

        # Check Daily Loss
        daily_drawdown = self.daily_start_balance - current_equity
        max_loss_amount = self.daily_start_balance * (self.max_daily_loss_pct / 100.0)

        if daily_drawdown >= max_loss_amount:
            self.is_hard_stopped = True
            return False, f"DAILY_LOSS_LIMIT: {daily_drawdown:.2f} >= {max_loss_amount:.2f}"

        # Check Cooldown
        if current_time_ts < self.cooldown_until:
            return False, "RISK_COOLDOWN"

        # Check Hourly Frequency
        self._clean_trade_timestamps(current_time_ts)
        if len(self.trade_timestamps) >= self.max_trades_hourly:
            return False, "HOURLY_TRADE_LIMIT"

        return True, "OK"
    
    def _clean_trade_timestamps(self, now: float):
        # Remove trades older than 1 hour (3600s)
        while self.trade_timestamps and (now - self.trade_timestamps[0] > 3600):
            self.trade_timestamps.popleft()

    def get_adaptive_risk(self, current_equity: float) -> float:
        """
        Calculates risk % based on streaks and drawdown.
        Base = 0.25% (or configured)
        Defensive = Half Risk
        """
        risk = self.base_risk
        
        # Defensive Condition 1: Loss Streak
        if self.loss_streak >= 2:
            risk = risk / 2.0
            
        # Defensive Condition 2: Deep Day Drawdown (> 50% of limit)
        daily_drawdown = self.daily_start_balance - current_equity
        max_loss_amount = self.daily_start_balance * (self.max_daily_loss_pct / 100.0)
        
        if daily_drawdown > (max_loss_amount * 0.5):
            risk = risk / 2.0
        
        return risk

    def calculate_lot_size(self, balance: float, entry_price: float, sl_price: float, risk_pct: float) -> float:
        """
        Calculates lot size based on risk percentage and stop loss distance.
        Assumes standard Forex lot (100,000 units).
        """
        if balance <= 0 or entry_price <= 0 or sl_price <= 0:
            return 0.0

        risk_amount = balance * (risk_pct / 100.0)
        sl_distance = abs(entry_price - sl_price)
        
        if sl_distance == 0:
            return 0.0
        
        raw_lots = risk_amount / (100000 * sl_distance)
        lots = max(0.01, round(raw_lots, 2))
        return lots
