import logging
import random
from dataclasses import dataclass
from typing import List

logger = logging.getLogger(__name__)

@dataclass
class SimPosition:
    ticket: int
    symbol: str
    type: int  # 0=BUY, 1=SELL
    volume: float
    price: float
    sl: float
    tp: float
    magic: int

class SimulatedExecution:
    """
    Mock Execution Engine for Dry-Run mode.
    Mimics MT5 behavior but stores trades in memory.
    """
    def __init__(self):
        self.positions: List[SimPosition] = []
        self._ticket_counter = 1000
        logger.warning("[SIMULATION] ScalpMaster running in DRY-RUN mode. No real orders will be sent.")

    def get_open_positions(self, symbol: str = None) -> list:
        if symbol:
            return [p for p in self.positions if p.symbol == symbol]
        return self.positions

    def count_open_trades(self, symbol: str) -> int:
        return len(self.get_open_positions(symbol))

    def execute_trade(self, symbol: str, direction: str, volume: float, sl: float, tp: float, comment: str = "") -> bool:
        # Check rule (mimic OrderManager)
        if self.count_open_trades(symbol) > 0:
            logger.warning(f"[SIMULATION] Trade rejected: Position already exists for {symbol}")
            return False

        self._ticket_counter += 1
        ticket = self._ticket_counter
        
        # Determine Type
        # MT5 constants: BUY=0, SELL=1
        type_int = 0 if direction == "BUY" else 1
        
        # Assume perfect fill at requested price (or 1 pip slippage sim?)
        # For now, simplistic perfect fill.
        # But wait, execute_trade DOES NOT take Price as input in OrderManager override?
        # Ah, OrderManager gets it from Tick. We should probably simulate getting tick or just use a dummy price.
        # Let's say we assume the caller logic checks price. But execute_trade signature is (symbol, dir, vol, sl, tp).
        # We need a price.
        
        # We can't fetch real tick in simulation if MT5 is offline? 
        # Actually dry_run usually connects to MT5 for Data, just mocks Execution.
        # So we SHOULD fetch price to be realistic.
        from modules.data.mt5_loader import MT5
        tick = MT5.symbol_info_tick(symbol)
        fill_price = tick.ask if direction == "BUY" else tick.bid if tick else 1.0

        pos = SimPosition(
            ticket=ticket,
            symbol=symbol,
            type=type_int,
            volume=float(volume),
            price=fill_price,
            sl=float(sl),
            tp=float(tp),
            magic=123456 # Config.MAGIC_NUMBER
        )
        
        self.positions.append(pos)
        logger.info(f"[SIMULATION] Trade EXECUTED: {direction} {volume} {symbol} @ {fill_price}. Ticket: {ticket}")
        return True

    def close_trade(self, ticket: int, symbol: str) -> bool:
        # Find position
        pos = next((p for p in self.positions if p.ticket == ticket), None)
        if not pos:
            logger.error(f"[SIMULATION] Close failed: Ticket {ticket} not found")
            return False
            
        self.positions.remove(pos)
        logger.info(f"[SIMULATION] Trade CLOSED: Ticket {ticket}")
        return True
