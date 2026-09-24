import asyncio
from typing import Optional

from openai import AsyncOpenAI

from app.logger.logger_wrapper import LoggerWrapper
from app.respondent.abstract_external_model import AbstractModelExternal
from app.utils import Utils

logger = LoggerWrapper()

class OpenService(AbstractModelExternal):

    def __init__(self) -> None:

        self.config = Utils.get_config_file()

        super().__init__()

        self.set_model_ticket(self.config.get('open_service', {}).get('model', "NONE"))
        self.set_base_url(self.config.get('open_service', {}).get('url', "NONE"))
        self.set_api_key(self.config.get('open_service', {}).get('api_key', "NONE"))

        logger(f"[OpenService_c:model_v]: {self.get_model_ticker() if not None else 'No model'},\n "
               f"[OpenService_c:url_v]: {self.get_base_url()},\n "
               f"[OpenService_c:api_key_v]: {True if self.get_api_key() else False} \n")

        self.client = AsyncOpenAI(base_url=self.get_base_url(),
                                  api_key=self.get_api_key())

    async def __aenter__(self) -> "OpenService":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.close()

    async def generate(self, prompt: Optional[str], **kwargs) -> str:
        await asyncio.sleep(3)
        try:
            response = await self.client.chat.completions.create(
                model=self.get_model_ticker(),
                messages = [{"role": "user", "content": prompt}],
            )
            answer = response.choices[0].message.content.strip()
            return answer.strip() if answer else None
        except Exception as e:
            logger(f"[OpenService_c:generate_f:answer_err]: {e}")

    async def close(self) -> None:
        await self.client.close()

    def __repr__(self):
        return f"Load Remote model with ticket: {self.get_model_ticker()}"

    # USAGE
    # async with RemoteService() as service:
    #     answer = await service.generate("What is Python?")
    #     print(answer)

