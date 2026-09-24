import asyncio
from typing import Optional, Dict
import aiohttp

from app.logger.logger_wrapper import LoggerWrapper
from app.respondent.abstract_external_model import AbstractModelExternal
from app.utils import Utils

logger = LoggerWrapper()

class RawService(AbstractModelExternal):

    def __init__(self) -> None:

        self.config: Optional[Dict] = Utils.get_config_file()

        super().__init__()

        self.set_model_ticket(self.config.get('raw_service', {}).get('model', "NONE"))
        self.set_base_url(self.config.get('raw_service', {}).get('url', "NONE"))
        self.set_api_key(self.config.get('raw_service', {}).get('api_key', "NONE"))

        logger(f"[RawService_c:model_v]: {self.get_model_ticker() if not None else ''},\n "
               f"[RawService_c:url_v]: {self.get_base_url()},\n "
               f"[RawService_c:api_key_v]: {True if self.get_api_key() else False} \n")

    async def generate(self, prompt: Optional[str], **kwargs) -> str:
        await asyncio.sleep(8)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'query': prompt
        }

        logger(f"[RawService_c:generate_f:prompt_v]: {prompt}")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, json=data, headers=headers) as response:
                    answer = await response.json()

            logger(f"[RawService_c:generate_f:raw_answer_v]: {answer}")
            logger(f"[RawService_c:generate_f:status_v]: {answer.get('status', "Don't obtain")}")

            return answer.get('data', {}).get('answer', "None")
        except Exception as e:
            logger(f"[RawService_c:generate_f:answer_err]: {e}")

    async def close(self) -> None:
        pass

    def __repr__(self):
        return f"Model's Ticker: {self.get_model_ticker()}"
