import logging
import time
import threading
from modules.data.mt5_loader import MT5
from config.config import Config

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self):
        self.magic_number = Config.MAGIC_NUMBER
        self.slippage = 10 
        self._lock = threading.Lock() 

    def get_open_positions(self, symbol: str = None) -> list:
        """
        Returns a list of open positions matching the Magic Number.
        If symbol is provided, filters by symbol.
        """
        if symbol:
            positions = MT5.positions_get(symbol=symbol)
        else:
            positions = MT5.positions_get()

        if positions is None:
            return []

        # Filter by magic number
        my_positions = [p for p in positions if p.magic == self.magic_number]
        return my_positions

    def count_open_trades(self, symbol: str) -> int:
        """Returns number of open trades for a symbol managed by this bot."""
        return len(self.get_open_positions(symbol))

    def execute_trade(self, symbol: str, direction: str, volume: float, sl: float, tp: float, comment: str = "") -> bool:
        """
        Executes a market order.
        direction: "BUY" or "SELL"
        volume: Lots
        sl: Stop Loss Price
        tp: Take Profit Price
        """
        # 1. Check existing positions (One trade per symbol rule)
        # Note: Depending on strategy, we might allow scaling. For now, strict 1 trade.
        # This check might be done upstream in logic, but good as a safety guard here.
        # But maybe we want to allow multiple? The spec said "One trade per symbol".
        # 1. Check existing positions (One trade per symbol rule)
        # Thread Safety: Lock this check + execution block
        with self._lock:
            if self.count_open_trades(symbol) > 0:
                logger.warning(f"Trade rejected: Position already exists for {symbol}")
                return False

            # 2. Get current price for filling info
            tick = MT5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Trade failed: No tick data for {symbol}")
                return False

            if direction == "BUY":
                order_type = MT5.ORDER_TYPE_BUY
                price = tick.ask
            elif direction == "SELL":
                order_type = MT5.ORDER_TYPE_SELL
                price = tick.bid
            else:
                logger.error(f"Invalid direction: {direction}")
                return False

            # 3. Construct Request
            request = {
                "action": MT5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": float(volume),
                "type": order_type,
                "price": price,
                "sl": float(sl),
                "tp": float(tp),
                "deviation": self.slippage,
                "magic": self.magic_number,
                "comment": comment or "ScalpMaster v1.2",
                "type_time": MT5.ORDER_TIME_GTC,
                "type_filling": MT5.ORDER_FILLING_IOC, # Immediate or Cancel often safer than FOK
            }

            # 4. Send Order
            result = MT5.order_send(request)
        
        # 5. Check Result
        if result is None:
            logger.error("Order send failed: Result is None")
            return False
            
        if result.retcode != 10009: # 10009 is TRADE_RETCODE_DONE
            logger.error(f"Order failed: {result.retcode} ({result.comment})")
            return False
            
        logger.info(f"Trade Executed: {direction} {volume} {symbol} @ {price}. Ticket: {result.order}")
        return True

    def close_trade(self, ticket: int, symbol: str) -> bool:
        """
        Closes a specific trade by ticket.
        """
        # To close, we open an opposite order with position ticket specified? 
        # Or usually just TRADE_ACTION_DEAL with TYPE_OPPOSITE.
        # Actually simpler is usually just SELL for BUY position.
        
        # We need position info to get volume
        positions = MT5.positions_get(ticket=ticket)
        if not positions:
            logger.error(f"Cannot close trade {ticket}: Position not found")
            return False
            
        position = positions[0]
        
        tick = MT5.symbol_info_tick(symbol)
        if not tick:
            return False
            
        if position.type == MT5.ORDER_TYPE_BUY:
            type_close = MT5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            type_close = MT5.ORDER_TYPE_BUY
            price = tick.ask

        request = {
            "action": MT5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": position.volume, # Close full volume
            "type": type_close,
            "position": ticket, # Important!
            "price": price,
            "deviation": self.slippage,
            "magic": self.magic_number,
            "type_time": MT5.ORDER_TIME_GTC,
            "type_filling": MT5.ORDER_FILLING_IOC,
        }

        result = MT5.order_send(request)
        if result.retcode != 10009:
            logger.error(f"Close failed: {result.retcode}")
            return False
            
        logger.info(f"Trade Closed: {ticket} for {symbol}")
        return True
