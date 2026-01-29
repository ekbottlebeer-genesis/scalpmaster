from dataclasses import dataclass
from typing import List, Tuple
from core.context import TradeContext

@dataclass
class TradingDecision:
    can_trade: bool
    reasons: List[str]

class StrategyChecklist:
    """
    Layered Pre-Trade Checklist Engine.
    Evaluates market context against 8 layers of strict rules.
    """

    MAX_SPREAD_POINTS = 20  # Configurable later
    MIN_ATR = 0.00005       # Minimal volatility requirement

    def run(self, ctx: TradeContext) -> TradingDecision:
        reasons = []

        # Layer 1: System Safety
        passed, reason = self._check_system_safety(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 2: Risk & Drawdown
        passed, reason = self._check_risk(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 3: Market Quality (Chop/Regime)
        passed, reason = self._check_market_quality(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 4: Trend & Bias
        passed, reason = self._check_trend_bias(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 5: Entry Setup (Signal)
        # Note: This checks if a signal EXISTS. It doesn't generate one.
        # We assume the context might carry a "candidate_signal" or we check technicals here.
        # For this design, we'll check if technicals align for *some* entry.
        passed, reason = self._check_entry_setup(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 6: Volatility Expansion
        passed, reason = self._check_volatility(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 7: Time Constraints
        passed, reason = self._check_time_constraints(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        # Layer 8: Order Validation
        passed, reason = self._check_order_validation(ctx)
        if not passed:
            return TradingDecision(False, [reason])

        return TradingDecision(True, ["ALL CHECKS PASSED"])

    def _check_system_safety(self, ctx: TradeContext) -> Tuple[bool, str]:
        if ctx.spread > self.MAX_SPREAD_POINTS:
            return False, f"SPREAD_TOO_HIGH: {ctx.spread} > {self.MAX_SPREAD_POINTS}"
        return True, ""

    def _check_risk(self, ctx: TradeContext) -> Tuple[bool, str]:
        # 'risk_status' dict should contain 'can_trade' flag from RiskManager
        if not ctx.risk_status.get('can_trade', False):
            return False, "RISK_LIMIT_HIT"
        return True, ""

    def _check_market_quality(self, ctx: TradeContext) -> Tuple[bool, str]:
        # Reject if AI regime says "CHOP" or "UNDEFINED"
        if ctx.market_regime in ["CHOP", "UNDEFINED", "RANGE_TIGHT"]:
             return False, f"BAD_REGIME: {ctx.market_regime}"
        return True, ""

    def _check_trend_bias(self, ctx: TradeContext) -> Tuple[bool, str]:
        # Reject if Trend Bias is Neutral/Conflicting
        if ctx.trend_bias == "NEUTRAL":
            return False, "TREND_NEUTRAL"
        return True, ""

    def _check_entry_setup(self, ctx: TradeContext) -> Tuple[bool, str]:
        # Placeholder logic: In a real scenario, we'd check if Price closed x EMA or RSI < 30 etc.
        # For now, we assume if we got this far, we check generic "Signal" validity from context
        # Or we implement the actual "Signal Generation" logic here?
        # Specification says "Checklist", implying validation. 
        # But commonly this layer *confirms* the signal found by scanning.
        
        # Let's say we check strict RSI bounds for the Trend Bias
        rsi = ctx.indicators.get('RSI_14', 50)
        
        if ctx.trend_bias == "LONG":
            if rsi > 70: return False, "RSI_OVERBOUGHT_FOR_LONG"
        elif ctx.trend_bias == "SHORT":
            if rsi < 30: return False, "RSI_OVERSOLD_FOR_SHORT"
            
        return True, ""

    def _check_volatility(self, ctx: TradeContext) -> Tuple[bool, str]:
        atr = ctx.indicators.get('ATR_14', 0)
        if atr < self.MIN_ATR:
            return False, f"LOW_VOLATILITY: ATR {atr}"
        return True, ""

    def _check_time_constraints(self, ctx: TradeContext) -> Tuple[bool, str]:
        if ctx.is_news_event:
            return False, "NEWS_EVENT_ACTIVE"
        if ctx.cooldown_remaining > 0:
            return False, f"COOLDOWN_ACTIVE: {ctx.cooldown_remaining}s"
        return True, ""

    def _check_order_validation(self, ctx: TradeContext) -> Tuple[bool, str]:
        # This would usually check SL distance vs Price.
        # Since Context doesn't have a proposed trade price, we can perform a sanity check
        # on recent candle size (e.g. dont trade if recent candle range is 0)
        if ctx.current_price <= 0:
            return False, "INVALID_PRICE"
        return True, ""
