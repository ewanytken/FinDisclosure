from abc import ABC, abstractmethod
from typing import Optional, List

from aiogram import Dispatcher, Router
from app.telegram.authorization import AuthorizationBot

class AbstractCommand(ABC):

    def __init__(self) -> None:
        self.authorization: Optional[AuthorizationBot] = AuthorizationBot()
        self.authorization.install_authorized_ids()

        self.dispatcher = Dispatcher()
        self.router = Router()
        self.dispatcher.include_router(self.router)

    def get_dispatcher(self) -> Optional[Dispatcher]:
        return self.dispatcher

    @abstractmethod
    def register_handlers(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_user_command_list(self) -> List:
        raise NotImplementedError

