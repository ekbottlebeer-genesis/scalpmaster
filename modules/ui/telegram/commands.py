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
    # TODO: Connect to global Bot State
    msg = (
        f"{bold('SYSTEM STATUS')}\n"
        f"Mode: {code('DRY-RUN')}\n"
        f"Uptime: 00:00:00\n"
        f"Regime: {code('UNDEFINED')}\n\n"
        f"{bold('ACCOUNT')}\n"
        f"Balance: $0.00\n"
        f"Daily PnL: $0.00\n"
        f"Open Trades: 0"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.HTML)

async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("System Healthy. Tick Loop Active.")

async def cmd_panic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # IMPORTANT: Logic to trigger close_all()
    await update.message.reply_text(f"🚨 {bold('PANIC TRIGGERED')} 🚨\nAttempting to close ALL positions...")
    # TODO: Call OrderManager.close_all()

async def cmd_scan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔍 Scanning markets...")

async def cmd_open(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usage: /open [SYM] [BUY/SELL] [LOTS]")

async def cmd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Current Mode: DRY-RUN")

async def cmd_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("No upcoming high-impact news detected.")

# --- Config & Debug Stubs ---
async def cmd_risk(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Risk set.")
async def cmd_trail(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Trailing updated.")
async def cmd_maxloss(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("MaxLoss updated.")
async def cmd_test(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Test executed.")
async def cmd_canceltest(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Test cancelled.")
async def cmd_testsignalmessage(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Fake signal sent.")
async def cmd_chart(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Chart request received.")
async def cmd_debugbybit(update: Update, context: ContextTypes.DEFAULT_TYPE): await update.message.reply_text("Debug info sent to log.")
