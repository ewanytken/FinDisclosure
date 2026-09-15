import asyncio
from typing import Optional, Dict, List

from aiogram import Bot

from app.cmd.abstract_commands import AbstractCommand
from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

class TelegramConnector:

    def __init__(self):
        self.bot_commands: Optional[AbstractCommand] = None
        self.config: Optional[Dict] =  Utils.get_config_file()
        self.bot: Optional[Bot] = None

    def set_bot_commands(self, bot_commands: Optional[AbstractCommand]) -> None:
        self.bot_commands = bot_commands
        if self.bot_commands:
            self.bot_commands.register_handlers()
        else:
            logger(f"Bot commands don't SET")

    def set_config(self, config: Dict):
        self.config = config

    def install_bot(self) -> None:
        try:
            self.bot = Bot(token=self.config.get("telegram", {}).get("bot_token", ""))
        except Exception as e:
            logger(f"Install Telegram Bot Exception: {e}")

    async def run_bot(self):
        try:
            if not self.bot:
                while True:
                    await asyncio.sleep(60)

            logger("Starting Telegram bot polling...")

            await self.bot.set_my_commands(self.bot_commands.get_user_command_list())

            disp = self.bot_commands.get_dispatcher()
            await disp.start_polling(self.bot)

        except Exception as e:
            logger(f"Bot Run-function Exception: {e}")
