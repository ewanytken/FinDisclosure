from typing import Optional, List, Callable

import asyncio
from google import genai
from google.genai.client import AsyncClient
from google.genai import types
from app.logger.logger_wrapper import LoggerWrapper
from app.respondent.abstract_external_model import AbstractModelExternal
from app.utils import Utils

logger = LoggerWrapper()

class GoogleService(AbstractModelExternal):

    def __init__(self) -> None:

        self.config = Utils.get_config_file()

        super().__init__()

        self.set_model_ticket(self.config['google_service']['model'])
        self.set_api_key(self.config['google_service']['api_key'])

        logger(f"Model: {self.get_model_ticker()}, "
               f"APIKey: {True if self.get_api_key() else False}")

        base_client = genai.Client(api_key=self.get_api_key())
        self.client: Optional[AsyncClient] = base_client.aio
        self.chat = None

    def init_chat(self, tools: Optional[List[Callable]] = None, temperature: float = 0.5):

        config = types.GenerateContentConfig(
            tools=tools,
            temperature=temperature
        )

        self.chat = self.client.chats.create(
            model=self.get_model_ticker(),
            config=config
        )
        logger("Google AsyncChat session initialized with tools.")

    async def generate(self, prompt: Optional[str], **kwargs) -> str:
        await asyncio.sleep(10)
        try:
            if self.chat is None:
                self.init_chat()

            response = await self.chat.send_message(prompt)
            return response.text if response else None
        except Exception as e:
            logger(f"Bad connection to Model Service: {e}")

    async def close(self) -> None:
        await self.client.aclose()

    def __repr__(self):
        return f"Load Google model with ticket: {self.get_model_ticker()}"
