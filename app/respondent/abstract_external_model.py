from abc import ABC, abstractmethod
from typing import Optional

class AbstractModelExternal(ABC):

    def __init__(self) -> None:
        self.model_ticket: Optional[str] = ""
        self.api_key: Optional[str] = ""
        self.base_url: Optional[str] = ""

    def set_base_url(self, base_url: Optional[str]) -> None:
        self.base_url = base_url

    def set_model_ticket(self, model_ticket: Optional[str]) -> None:
        self.model_ticket = model_ticket

    def set_api_key(self, api_key: Optional[str]) -> None:
        self.api_key = api_key

    def get_base_url(self) -> Optional[str]:
        return self.base_url

    def get_model_ticker(self) -> Optional[str]:
        return self.model_ticket

    def get_api_key(self) -> Optional[str]:
        return self.api_key

    @abstractmethod
    async def generate(self, prompt: Optional[str], **kwargs) -> str:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError
