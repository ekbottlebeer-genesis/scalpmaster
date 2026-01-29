import unittest
from unittest.mock import AsyncMock, MagicMock
from modules.ui.telegram import commands

class TestTelegramCommands(unittest.TestCase):
    async def asyncSetUp(self):
        # Setup Mock Update and Context
        self.update = MagicMock()
        self.update.message.reply_text = AsyncMock()
        self.context = MagicMock()

    async def test_cmd_status(self):
        await commands.cmd_status(self.update, self.context)
        self.update.message.reply_text.assert_called_once()
        args = self.update.message.reply_text.call_args[0][0]
        self.assertIn("SYSTEM STATUS", args)

    async def test_cmd_panic(self):
        await commands.cmd_panic(self.update, self.context)
        self.update.message.reply_text.assert_called_once()
        args = self.update.message.reply_text.call_args[0][0]
        self.assertIn("PANIC TRIGGERED", args)

    async def test_cmd_help(self):
        await commands.cmd_help(self.update, self.context)
        self.update.message.reply_text.assert_called_once()
        args = self.update.message.reply_text.call_args[0][0]
        self.assertIn("COMMANDS", args)

if __name__ == '__main__':
    unittest.main()
