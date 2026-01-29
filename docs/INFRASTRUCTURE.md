# ScalpMaster Infrastructure & DevOps Guide

## 1. Development vs. Runtime Model

### Development Environment (macOS)
- **Role**: Code authoring, strategy logic implementation, backtesting (future), and unit testing.
- **Constraints**: 
  - No access to live MT5 terminal.
  - Must use mock objects or conditional imports for `MetaTrader5` library.
  - **NEVER** commit real API keys or secrets.
- **Workflow**: 
  1. Edit code in VS Code / Cursor.
  2. Run local tests (using mocks).
  3. `git commit` and `git push`.

### Runtime Environment (Windows PC)
- **Role**: Production execution, live market data connectivity, trade execution.
- **Constraints**: 
  - Host OS for MT5 Terminal.
  - Must have stable internet connection.
- **Workflow**:
  1. `git pull` latest changes.
  2. Update dependencies (`pip install -r requirements.txt`).
  3. Restart the bot using the crash-recovery script (`run_bot.bat`).

---

## 2. Environment Setup

### prerequisites
- **Python**: Version 3.10+ required.
- **Git**: Installed on both machines.
- **MT5 Terminal**: Installed on Windows machine.

### Setup Steps
1. **Clone the Repository**:
   ```bash
   git clone <repo_url>
   cd ScalpMaster
   ```

2. **Virtual Environment**:
   ```bash
   # Create
   python -m venv venv
   
   # Activate (Mac)
   source venv/bin/activate
   
   # Activate (Windows)
   venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configuration**:
   - Copy `.env.example` to `.env`.
   - **Environment Variables (.env)**: Fill in *secrets* (MT5 credentials, Telegram Token).
   - **Settings (settings.yaml)**: Configure trading parameters (Risk, Pairs, etc.).

---

## 3. Secret Management
- **Tool**: `python-dotenv`
- **Rule**: `.env` is **ignored** by git.
- **Secrets**:
  - `MT5_LOGIN`
  - `MT5_PASSWORD`
  - `MT5_SERVER`
  - `MT5_PATH` (Absolute path to `terminal64.exe`)
  - `TELEGRAM_TOKEN`
  - `TELEGRAM_CHAT_ID`

---

## 4. Deployment Flow (Mac -> Win)

1. **Mac (Dev)**:
   - Make changes.
   - Verify logic.
   - `git add .`
   - `git commit -m "Update strategy"`
   - `git push origin main`

2. **Windows (Runtime)**:
   - Open PowerShell / Terminal.
   - `cd ScalpMaster`
   - `git pull origin main`
   - (Optional) `pip install -r requirements.txt` if dependencies changed.
   - **Restart Bot**: Close the running instance and start `scripts/run_bot.bat`.

---

## 5. Crash Recovery Strategy (Windows)
We use a **batch script loop** to ensure the bot restarts automatically if the Python process crashes or is terminated unexpectedly.

**File**: `scripts/run_bot.bat`
```batch
@echo off
:loop
echo Starting ScalpMaster...
path\to\venv\Scripts\python.exe main.py
echo Bot crashed or stopped. Restarting in 5 seconds...
timeout /t 5
goto loop
```
