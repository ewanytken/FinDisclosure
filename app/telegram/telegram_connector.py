import asyncio
from typing import Optional, Dict, List

from aiogram import Bot
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

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
        try:
            self.bot_commands = bot_commands
            self.bot_commands.register_handlers()
            logger(f"[TelegramConnector_c:set_bot_commands_f:bot_commands_v]: Bot commands Initialized")
        except Exception as e:
            logger(f"[TelegramConnector_c:set_bot_commands_f:bot_commands_err]: {e}")

    def set_config(self, config: Dict):
        self.config = config

    def install_bot(self) -> None:
        try:
            self.bot = Bot(token=self.config.get("telegram", {}).get("bot_token", ""))
        except Exception as e:
            logger(f"[TelegramConnector_c:install_bot_f:bot_err]: {e}")

    async def run_bot(self):
        webhook_config = self.config.get("webhook", {})

        if webhook_config:
            try:
                if not self.bot or not self.bot_commands:
                    logger(f"[TelegramConnector_c:run_bot_f:bot&bot_commands_init]: Bot commands not initialized")
                    return

                # config: { "webhook": { "host": "123.45.67.89", "port": 8443, "path": "/webhook" } }
                webhook_host = webhook_config.get("host", "0.0.0.0")
                webhook_port = webhook_config.get("port", 443)  # Telegram ports: 443, 80, 88, 8443
                webhook_path = webhook_config.get("path", "/webhook")

                webhook_url = f"https://{webhook_host}{webhook_path}"

                logger(f"[TelegramConnector_c:run_bot_f:webhook_url_v]: {webhook_url}")

                await self.bot.set_my_commands(self.bot_commands.get_user_command_list())

                await self.bot.set_webhook(url=webhook_url)

                app = web.Application()
                disp = self.bot_commands.get_dispatcher()

                webhook_requests_handler = SimpleRequestHandler(dispatcher=disp, bot=self.bot)

                webhook_requests_handler.register(app, path=webhook_path)
                setup_application(app, disp, bot=self.bot)

                runner = web.AppRunner(app)
                await runner.setup()
                site = web.TCPSite(runner, host="0.0.0.0", port=webhook_port)  # Listen all interface on specify port

                logger(f"[TelegramConnector_c:run_bot_f:webhook_port_v]: Starting Telegram Webhook: {webhook_port}...")
                await site.start()
                await asyncio.Event().wait()

            except Exception as e:
                logger(f"[TelegramConnector_c:run_bot_f:webhook_err]: {e}")
        else:
            try:
                if not self.bot:
                    while True:
                        await asyncio.sleep(60)

                logger(f"[TelegramConnector_c:run_bot_f:bot_init]: Starting Telegram bot polling...")

                await self.bot.set_my_commands(self.bot_commands.get_user_command_list())

                disp = self.bot_commands.get_dispatcher()
                await disp.start_polling(self.bot)

            except Exception as e:
                logger(f"[TelegramConnector_c:run_bot_f:long_polling_err]: {e}")