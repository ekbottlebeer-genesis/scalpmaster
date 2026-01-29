# ScalpMaster v1.2 System Architecture

## 1. Modular Folder Structure

The project follows a strict modular design to separate concerns and ensure maintainability.

```text
ScalpMaster/
├── config/                 # Configuration Management
│   ├── config.py           # Unified config loader
│   └── settings.yaml       # Trading parameters (Non-secret)
├── core/                   # Core Business Logic (The "Brain")
│   ├── bot.py              # Main Bot Controller (Orchestrator)
│   ├── risk.py             # RiskManager (Hard-Kill Switch)
│   └── events.py           # Event Bus / Signal definitions
├── strategies/             # Trading Logic
│   └── checklist.py        # The "Rule Checklist" Engine
├── modules/                # Specialized Modules
│   ├── data/               # Market Data Adapters
│   │   └── mt5_adapter.py  # MT5 Connector
│   ├── execution/          # Order Management
│   │   └── trade_manager.py # Trade Lifecycle
│   ├── ai/                 # AI Regime Filter
│   │   └── regime.py       # Regime Classification
│   └── ui/                 # User Interface
│       └── telegram_bot.py # Command Centre
├── logs/                   # Local logs (GITIGNORED)
├── tests/                  # Unit and Integration Tests
├── docs/                   # Documentation
├── scripts/                # Operational Scripts (run_bot.bat)
├── .env                    # Secrets (GITIGNORED)
└── main.py                 # Entry Point
```

## 2. Module Responsibilities

| Module | Responsibility | Key Constraints |
| :--- | :--- | :--- |
| **`core/bot.py`** | **Orchestrator**. Runs the main loop. Fetches data, queries Strategy, checks Risk, triggers Execution. | No trading logic here. Pure coordination. |
| **`core/risk.py`** | **Guardian**. Tracks daily PnL & Balance. **BLOCKS** any trade if `DailyLoss >= MaxLimit`. | **MUST** be checked before every order. |
| **`strategies/checklist.py`** | **Decision Maker**. Implements the strategy as a series of boolean checks (e.g., `is_trend_up()`, `is_rsi_valid()`). | Returns `True`/`False` + Signal. No execution logic. |
| **`modules/ai`** | **Filter**. Provides "Market Regime" context (e.g., "Trending", "Ranging"). | **NEVER** generates buy/sell signals. Only filter. |
| **`modules/execution`** | **Action**. Sends orders to MT5. Manages SL/TP and partial closes. | Only acts on confirmed signals from Core. |
| **`modules/ui`** | **Interface**. Sends alerts to Telegram. Receives commands (`/status`, `/stop`). | Runs in a separate thread. |

## 3. Data Flow

```mermaid
graph TD
    A[MT5 Terminal] -->|Tick Data| B(Data Adapter)
    B -->|OHLCV Data| C{AI Regime Filter}
    C -->|Regime (e.g. Range)| D[Strategy Checklist]
    B -->|Price Data| D
    D -->|Signal (Buy/Sell/None)| E{Risk Manager}
    E -->|Approved?| F[Order Manager]
    E -->|Denied?| G[Log & Alert]
    F -->|Send Order| A
    F -->|Update Status| H[Telegram UI]
```

## 4. Configuration & Environment

-   **Loading**: `config/config.py` is the single source of truth.
-   **Secrets**: Loaded from `.env` (API Keys, Login IDs).
-   **Tuning**: Loaded from `config/settings.yaml` (Pairs, Risk %, Indicator Period).
-   **Hot-Reload**: Not supported. Restart bot to apply config changes.

## 5. Failure Isolation & Recovery

### Strategy
1.  **Exception Handling**: Each module (`Data`, `Strategy`, `Execution`) wraps critical calls in `try-except` blocks.
    -   *Example*: If `Telegram` fails, log error but **KEEP TRADING**.
    -   *Example*: If `MT5` disconnects, **PAUSE** trading and attempt reconnect.

2.  **Process Supervision**:
    -   We rely on the **`scripts/run_bot.bat`** loop.
    -   If a critical error (e.g., Segfault, Unhandled Exception) kills the Python process, the batch script automatically restarts it after 5 seconds.

3.  **State Persistence**:
    -   Trades are tracked via **Magic Number** on the broker side. Restarting the bot re-scans open trades from MT5, ensuring no state is lost.
