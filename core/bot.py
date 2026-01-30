import time
import logging
from datetime import datetime
from typing import Dict

from config.config import Config
from core.context import TradeContext
from core.risk import RiskManager
from modules.data.connection_manager import ConnectionManager
from modules.data.market_data import MarketData
from modules.data.mt5_loader import MT5
from modules.indicators.indicators import Indicators
from modules.ai.regime_filter import RegimeFilter
from strategies.checklist import StrategyChecklist
from modules.data.news_loader import NewsLoader
from modules.ui.telegram.notifier import TelegramNotifier
from modules.ui.console import ConsoleUI

# Execution Engines
from modules.execution.order_manager import OrderManager
from modules.execution.simulator import SimulatedExecution

logger = logging.getLogger(__name__)

class ScalpMasterBot:
    def __init__(self):
        self.is_running = False
        
        # Initialize Core Modules
        self.risk_manager = RiskManager()
        self.regime_filter = RegimeFilter()
        self.checklist = StrategyChecklist()
        self.news_loader = NewsLoader()
        
        # Select Execution Engine
        if Config.DRY_RUN:
            logger.info("Initializing in DRY-RUN (Simulation) Mode")
            self.execution = SimulatedExecution()
        else:
            logger.info("Initializing in LIVE TRADING Mode")
            self.execution = OrderManager()
            
        # State Tracking
        self.last_scan_time = 0

    def start(self):
        """
        Main Entry Point. Starts the infinite strategy loop.
        """
        self.is_running = True
        logger.info(f"ScalpMaster v1.2 Started. Loop Interval: {Config.LOOP_INTERVAL}s")
        TelegramNotifier.send("🚀 <b>ScalpMaster v1.2 Started</b>\nMonitoring markets...")
        
        if not ConnectionManager.initialize():
            logger.critical("Failed to connect to MT5. Exiting.")
            return

        # Snapshot Account for Risk Manager
        self._risk_snapshot()

        try:
            while self.is_running:
                self.run_tick()
                time.sleep(Config.LOOP_INTERVAL)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            logger.exception(f"Crash in Main Loop: {e}")
            self.stop()

    def stop(self):
        self.is_running = False
        ConnectionManager.shutdown()
        logger.info("ScalpMaster Stopped.")
        TelegramNotifier.send("🛑 <b>ScalpMaster Stopped</b>")

    def _risk_snapshot(self):
        # account_info() returns tuple/struct in MT5
        # Mock returns None or Object
        # We need balance.
        # REAL MT5: mt5.account_info().balance
        info = MT5.account_info()
        balance = 10000.0 # Default fallback
        if info and hasattr(info, 'balance'):
            balance = info.balance
        
        self.risk_manager.snapshot_account(balance)

    def run_tick(self):
        """
        Single iteration of the strategy loop.
        """
        if not ConnectionManager.ensure_connected():
            return

        current_time = datetime.now()
        
        # Iterate over monitored pairs
        if not Config.TRADING_PAIRS:
            return

        ConsoleUI.print_header(len(Config.TRADING_PAIRS), current_time)
        
        # Iterate over monitored pairs
        for symbol in Config.TRADING_PAIRS:
            try:
                self._process_symbol(symbol, current_time)
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                ConsoleUI.print_row(symbol, "ERR", 0.0, f"Error: {str(e)}", error=True)
                
        ConsoleUI.print_section_end()

    def _process_symbol(self, symbol: str, now: datetime):
        # 0. Skip if position exists (One trade per pair rule)
        if self.execution.count_open_trades(symbol) > 0:
            ConsoleUI.print_row(symbol, "---", 0.0, "Active Position (Skipped)", error=False)
            return

        # 0. Check connection/availability specific to symbol?
        # Done inside MarketData methods mostly.

        # 1. Fetch Data
        # We need enough candles for Indicators (e.g. 200 EMA + buffer) -> 500
        df = MarketData.get_candles_df(symbol, Config.TIMEFRAME, 500)
        if df.empty:
            return

        # 2. Add Indicators
        df = Indicators.add_all(df)
        if df.empty:
            return

        # 3. AI Analysis
        regime = self.regime_filter.detect_regime(df)
        
        # Determine Trend Bias (Simple Logic for Context population)
        # Real logic should probably be in strategies/trend.py but putting helper here
        # bias = "LONG" if Close > EMA200 else "SHORT"
        last_row = df.iloc[-1]
        bias = "NEUTRAL"
        ema200 = last_row.get('EMA_200')
        close = last_row.get('close')
        
        if ema200 and close:
            bias = "LONG" if close > ema200 else "SHORT"

        # 4. Build Context
        # Spread
        tick = MarketData.get_tick_info(symbol)
        spread = 0.0
        current_price = 0.0
        if tick:
            spread_points = (tick.ask - tick.bid) / 0.00001 # approx points
            spread = spread_points
            current_price = tick.ask if bias == "LONG" else tick.bid # Rough guess

        # 4.1 Check Risk State
        can_trade_risk, risk_reason = self.risk_manager.can_trade(
             current_equity=self._get_equity(), # Helper needed
             current_time_ts=now.timestamp()
        )
        
        # 4.2 Check News State
        is_news = self.news_loader.is_news_imminent(symbol)

        ctx = TradeContext(
            symbol=symbol,
            timestamp=now,
            current_price=current_price,
            spread=spread,
            session_name="NY", # Default to NY for now. Logic: datetime -> time range check
            is_news_event=is_news,
            indicators={
                'RSI_14': last_row.get('RSI_14', 50),
                'ATR_14': last_row.get('ATR_14', 0),
                'ADX_14': last_row.get('ADX_14', 0),
            },
            market_regime=regime,
            trend_bias=bias,
            cooldown_remaining=0, 
            pullback_candles=0, # Not strictly used in Checklist v1
            risk_status={'can_trade': can_trade_risk, 'reason': risk_reason}
        )

        # 5. Run Checklist
        decision = self.checklist.run(ctx)
        
        # 6. UI Output
        # Extract status from decision reasons or context
        status_msg = decision.reasons[0] if decision.reasons else "Unknown"
        if decision.can_trade:
             status_msg = "🔥 TRADE FOUND!"
        
        rsi_val = ctx.indicators.get('RSI_14', 0.0)
        ConsoleUI.print_row(symbol, bias, rsi_val, status_msg)
        
        if decision.can_trade:
            # 7. Execute!
            self._execute_signal(symbol, bias, ctx)
        else:
            # Silent fail usually, or debug log if in verbose
            # logger.debug(f"{symbol} ignored: {decision.reasons}")
            pass

    def _execute_signal(self, symbol: str, direction: str, ctx: TradeContext):
        # Double check Risk (Redundant but safe)
        can_trade, _ = self.risk_manager.can_trade(self._get_equity(), datetime.now().timestamp())
        if not can_trade:
            return

        # Calculate Size
        # Mocking specific entry/sl for now as Checklist didn't provide specific levels
        # In full implementation, Strategy would return Entry/SL/TP
        # Here we assume Market Order + generic 10 pip SL for demo
        sl_pips = 10
        tp_pips = 20
        point = 0.00001
        
        current_price = ctx.current_price
        if direction == "LONG":
            sl = current_price - (sl_pips * point * 10)
            tp = current_price + (tp_pips * point * 10)
            mt5_dir = "BUY"
        else:
            sl = current_price + (sl_pips * point * 10)
            tp = current_price - (tp_pips * point * 10)
            mt5_dir = "SELL"
            
        risk_pct = self.risk_manager.get_adaptive_risk(self._get_equity())
        
        volume = self.risk_manager.calculate_lot_size(
            balance=self._get_balance(),
            entry_price=current_price,
            sl_price=sl,
            risk_pct=risk_pct
        )
        
        if volume > 0:
            logger.info(f"Signal Confirmed: {mt5_dir} {symbol}. Risk={risk_pct}%. Lots={volume}")
            success = self.execution.execute_trade(symbol, mt5_dir, volume, sl, tp)
            
            if success:
                # Notify Telegram
                msg = (
                    f"✅ <b>Order Placed</b>\n"
                    f"Symbol: <code>{symbol}</code>\n"
                    f"Side: <b>{mt5_dir}</b>\n"
                    f"Lots: {volume}\n"
                    f"Price: {current_price}\n"
                    f"Risk: {risk_pct}%"
                )
                TelegramNotifier.send(msg)

    def _get_equity(self):
        info = MT5.account_info()
        return info.equity if info else 10000.0

    def _get_balance(self):
        info = MT5.account_info()
        return info.balance if info else 10000.0
