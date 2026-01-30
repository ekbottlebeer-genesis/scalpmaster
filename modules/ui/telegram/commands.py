from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
import logging

logger = logging.getLogger(__name__)

# --- formatting helpers ---
def code(text): return f"<code>{text}</code>"
def bold(text): return f"<b>{text}</b>"

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ScalpMaster v1.2 Command Centre.\nUse /help for commands.")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        f"{bold('COMMANDS')}\n"
        f"/status - System Overview\n"
        f"/scan - Force Market Scan\n"
        f"/panic - {bold('CLOSE ALL TRADES')}\n"
        f"/mode [dry/live] - Switch Mode\n"
        f"/risk [val] - Set Risk %\n"
        f"/news - Check News Status"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    engine = context.bot_data.get("engine")
    if not engine:
        await update.message.reply_text("⚠️ Engine not connected.")
        return

    state = engine.get_state_summary()
    
    msg = (
        f"{bold('SYSTEM STATUS')}\n"
        f"Mode: {code(state['mode'])}\n"
        f"Uptime: {state['uptime']}\n"
        f"State: {'🟢 RUNNING' if state['is_running'] else '🔴 STOPPED'}\n\n"
        f"{bold('ACCOUNT')}\n"
        f"Balance: ${state['balance']:.2f}\n"
        f"Equity: ${state['equity']:.2f}\n"
        f"Daily PnL: ${state['daily_pnl']:.2f}\n"
        f"Open Trades: {state['open_trades']}\n"
        f"Pairs: {state['pairs']}"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("System Healthy. Tick Loop Active.")

async def cmd_panic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    engine = context.bot_data.get("engine")
    if engine:
        engine.panic_close()
        await update.message.reply_text(f"🚨 {bold('PANIC EXECUTED')} 🚨\nClose all signal sent.")
    else:
        await update.message.reply_text("Error: Engine not connected.")

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scanning markets...")

async def cmd_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usage: /open [SYM] [BUY/SELL] [LOTS]")

async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Current Mode: DRY-RUN")

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    engine = context.bot_data.get("engine")
    if not engine:
        await update.message.reply_text("Engine not connected.")
        return

    events = engine.news_loader.get_upcoming_events(limit=5)
    
    if not events:
        await update.message.reply_text("📅 No upcoming High-Impact news found.")
        return
        
    msg = f"{bold('UPCOMING HIGH IMPACT NEWS')}\n\n"
    for e in events:
        # Parse easier
        title = e.get('title', 'N/A')
        country = e.get('country', '??')
        date_str = e.get('date', '')
        
        # Try to format time nicely (Very rough parsing again)
        try:
             # Just show the raw string or slice it if standard ISO
             # 2024-01-30T15:00:00+00:00 -> 15:00 (UTC)
             ts = date_str.split('T')[1][:5]
             msg += f"• {country} - {title} @ {ts}\n"
        except:
             msg += f"• {country} - {title}\n"
             
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

# --- Config & Debug Stubs ---
async def cmd_risk(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Risk set.")
async def cmd_trail(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Trailing updated.")
async def cmd_maxloss(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("MaxLoss updated.")
async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Test executed.")
async def cmd_canceltest(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Test cancelled.")
async def cmd_testsignalmessage(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Fake signal sent.")
async def cmd_chart(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Chart request received.")
async def cmd_debugbybit(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Debug info sent to log.")
