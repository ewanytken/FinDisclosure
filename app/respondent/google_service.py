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

        self.set_model_ticket(self.config.get('google_service', {}).get('model', "NONE"))
        self.set_base_url(self.config.get('google_service', {}).get('url', "NONE"))
        self.set_api_key(self.config.get('google_service', {}).get('api_key', "NONE"))

        logger(f"[GoogleService_c:model_v]: {self.get_model_ticker() if not None else ''},\n "
               f"[GoogleService_c:url_v]: {self.get_base_url()},\n "
               f"[GoogleService_c:api_key_v]: {True if self.get_api_key() else False} \n")

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
        logger("[GoogleService_c:init_chat_f:initialization_b]: True")

    async def generate(self, prompt: Optional[str], **kwargs) -> str:
        logger(f"[GoogleService_c:generate_f:prompt_v]: {prompt}")
        await asyncio.sleep(10)
        try:
            if self.chat is None:
                self.init_chat()

            response = await self.chat.send_message(prompt)
            logger(f"[GoogleService_c:generate_f:response_v]: {response}")
            return response.text if response else None
        except Exception as e:
            logger(f"[GoogleService_c:generate_f:response_err]: {e}")

    async def close(self) -> None:
        await self.client.aclose()

    def __repr__(self):
        return f"Load Google model with ticket: {self.get_model_ticker()}"
