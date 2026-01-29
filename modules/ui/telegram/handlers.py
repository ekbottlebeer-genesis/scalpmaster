from telegram.ext import Application, CommandHandler, filters
from modules.ui.telegram import commands

def register_handlers(app: Application, security_filter: filters.BaseFilter):
    """
    Registers all command handlers with the application, applied with security filter.
    """
    
    # helper to wrap
    def add(command, func):
        app.add_handler(CommandHandler(command, func, filters=security_filter))

    # Monitor
    add("start", commands.cmd_start)
    add("help", commands.cmd_help)
    add("status", commands.cmd_status)
    add("health", commands.cmd_health)
    add("news", commands.cmd_news)
    
    # Control
    add("scan", commands.cmd_scan)
    add("open", commands.cmd_open)
    add("panic", commands.cmd_panic)
    add("mode", commands.cmd_mode)
    add("canceltest", commands.cmd_canceltest)
    
    # Config
    add("risk", commands.cmd_risk)
    add("trail", commands.cmd_trail)
    add("maxloss", commands.cmd_maxloss)
    
    # Debug
    add("test", commands.cmd_test)
    add("testsignalmessage", commands.cmd_testsignalmessage)
    add("chart", commands.cmd_chart)
    add("debugbybit", commands.cmd_debugbybit)
