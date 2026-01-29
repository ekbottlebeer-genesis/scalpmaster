# ScalpMaster v1.2 - Intelligent Defensve Scalper

> **Philosophy**: Survival First. Market quality dictates participation. "Better to miss a trade than lose capital."

ScalpMaster is a modular, production-grade automated trading system for MetaTrader 5. It distinguishes itself through a rigorous **"Defence-in-Depth"** architecture, where an AI Regime Filter and an 8-Layer Rule Checklist must strictly agree before any risk is taken.

---

## 1. Core Architecture

The system is built on a Hexagonal Architecture principle, ensuring the Core Logic is isolated from external adapters (MT5, Telegram).

-   **Core**: Pure python logic (`StrategyChecklist`, `RiskManager`, `TradeContext`).
-   **Adapters**: `MT5Loader`, `TelegramBot`.
-   **AI Layer**: `RegimeFilter` (Scikit-Learn).
-   **Safety**: `run_bot.bat` infinite loop + Crash recovery.

---

## 2. Strategy Engine (The "Brain")

ScalpMaster does not rely on a single "Golden Indicator". Instead, it uses a **Chain of Responsibility** checklist. A trade proposal must pass **ALL 8 LAYERS** to execute.

| Layer | Name | Responsibility | Failure Example |
| :--- | :--- | :--- | :--- |
| **1** | **Safety** | Broker connection & Spread checks. | Spread > 20 points. |
| **2** | **Risk** | Account health & Daily limits. | Daily Loss > 4%. |
| **3** | **Market Quality** | AI Regime Classification. | AI detects "CHOP". |
| **4** | **Trend Bias** | EMA Structure & Price Action. | Price inside Clouds. |
| **5** | **Entry Setup** | Signal Triggers (e.g. RSI). | RSI Neutral (45-55). |
| **6** | **Volatility** | Expansion requirements. | ATR < 5 pips (Dead market). |
| **7** | **Time** | Session & Cooldowns. | News Event in 5 mins. |
| **8** | **Order Valid** | SL/TP Ratios & Pricing. | Stop Loss too close. |

---

## 3. Risk Engine (The "Guardian")

The `RiskManager` module operates independently of the strategy. It has veto power over all trades.

### A. Hard Limits
-   **Max Daily Loss**: Defaults to **4%**. If hit, the bot enters a **Hard Stop** state until the next daily reset.
-   **Max Drawdown**: Total equity protection.

### B. Adaptive Sizing
-   **Base Risk**: **0.25%** per trade.
-   **Defensive Mode**: Risk is **HALVED** (0.125%) if:
    -   Loss Streak >= 2 trades.
    -   Daily Drawdown > 50% of Limit.

---

## 4. AI & Adaptability

**What AI Does:**
-   **Regime Classification**: Analyzes OHLCV data to tag the market as `TREND_UP`, `TREND_DOWN`, `RANGE`, or `CHOP`.
-   **Optimization**: `PostTradeAdaptor` slowly tightens thresholds after losses (demanding higher quality) and relaxes them after wins.

**What AI Does NOT Do:**
-   **Signal Generation**: The AI **NEVER** says "Buy Now". It only says "Conditions are Safe".

---

## 5. Command Centre (Telegram)

Operate the bot remotely via Telegram.
**Security**: Only the Chat ID specified in `.env` is allowed. All others are ignored.

| Command | Function |
| :--- | :--- |
| `/status` | View Balance, PnL, Regime, and Open Trades. |
| `/scan` | Force a manual market scan cycle immediately. |
| `/panic` | **EMERGENCY**. Closes ALL open positions immediately. |
| `/mode [dry/live]` | Switch between Simulation and Live Execution. |
| `/risk [val]` | Dynamically adjust risk percentage. |
| `/news` | Check for upcoming high-impact economic events. |
| `/health` | Verify system heartbeat and lag. |

---

## 6. Setup & Operations

### Prerequisites
-   Python 3.9+
-   MetaTrader 5 Terminal (Windows Only)
-   *Mac Users*: Development supported via **Mock Layer**.

### Installation
1.  **Clone & Install**:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Configuration**:
    -   Copy `.env.example` to `.env` and fill valid MT5/Telegram credentials.
    -   Edit `config/settings.yaml` for Pairs and Timeframes.

### Running
-   **Live/Dry-Run**:
    ```bash
    python main.py
    ```
-   **Dry-Run Mode**: Ensure `dry_run: true` is set in `config/settings.yaml`. The bot will simulate trades in-memory without contacting the broker.

---

## 7. Prop-Firm Compliance

ScalpMaster is built with Prop Firm rules in mind:
-   **Consistency**: Adaptive risk ensures no rigid "gambling" patterns.
-   **Loss Limits**: Hard stops prevent breaching firm daily drawdown rules.
-   **One-Trade Rule**: Prevents stacking/grid-trading which is often banned.
-   **News Avoidance**: Filter can be configured to block trades +/- 30 mins around events.

---

## 8. Development

### Running Tests
All modules are covered by Unit Tests using Mocks.
```bash
python -m unittest discover tests
```

### Mac Development
The system automatically detects macOS and swaps the real `MetaTrader5` library for a `MagicMock` equivalent. This allows full logic testing on non-Windows machines.
