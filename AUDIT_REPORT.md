# ScalpMaster Hardening Audit Report

**Date**: 2026-01-29
**Auditor**: Antigravity
**Scope**: Risk, Execution, UI, Config.

## 🚨 Critical Vulnerabilities

### 1. Telegram Blocking Strategy Loop
**Severity**: **CRITICAL**
**Location**: `modules/ui/telegram/bot.py` -> `run()`
**Issue**: `self.app.run_polling()` is a blocking call. If called from `main.py`, the strategy will **never execute**. 
**Fix**: Run the Telegram Bot in a separate `threading.Thread` or use `asyncio` loop handling if refactoring the entire core to async. For the current design, a Daemon Thread is required.
```python
# In main.py
t = threading.Thread(target=bot.run, daemon=True)
t.start()
```

### 2. Race Conditions in OrderManager
**Severity**: **HIGH**
**Location**: `modules/execution/order_manager.py` -> `execute_trade`
**Issue**: The check `count_open_trades > 0` followed by `order_send` is not atomic. If a manual trade (via Telegram `/open`) and a strategy trade occur simultaneously, both might pass the check before the first one fills.
**Fix**: Add a `threading.Lock` to `OrderManager`.
```python
with self._lock:
    if self.count_open_trades(...) > 0: return False
    ...
    MT5.order_send(...)
```

### 3. Missing Overtrading Protection (Hourly Limit)
**Severity**: **MEDIUM**
**Location**: `core/risk.py`
**Issue**: The `RiskManager` tracks `trades_today` but does not enforce a `MAX_TRADES_HOURLY` limit. Fast-scalping strategies can burn equity rapidly during a "tilt" hour even if daily limit isn't hit.
**Fix**: Implement a `trades_this_hour` deque or counter reset logic in `update_metrics`.

## ⚠️ Medium Risks (Prop-Firm Compliance)

### 4. News Data Vacuum
**Severity**: **MEDIUM**
**Location**: `strategies/checklist.py`
**Issue**: Layer 7 checks `ctx.is_news_event`, but there is currently **no implementation** sourcing this data. The bot is effectively blind to news.
**Fix**: Implement `modules/data/news_loader.py` (e.g. ForexFactory scraper or API) to populate the context.

### 5. Logging of Secrets
**Severity**: **LOW**
**Location**: General
**Issue**: Ensure `Config.MT5_PASSWORD`/`LOGIN` are never logged. Currently `Config.validate()` is safe, but future usage in `main.py` startup logs must be masked.
**Fix**: Use a `mask_secret(str)` helper in logs.

## ✅ Passing Checks
-   **Whitelist**: Telegram `whitelist_middleware` is correctly implemented.
-   **Hard Stop**: `RiskManager.can_trade` correctly enforces Daily Loss logic.
-   **Isolation**: `MagicNumber` usage prevents interference with manual trades.
