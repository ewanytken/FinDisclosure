from typing import Optional, Set

from aiogram.types import Message, User

from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

class AuthorizationBot:
    def __init__(self):
        self.config: [Optional] = Utils.get_config_file()
        self.authorized_ids: Optional[Set] = None

    def set_config(self, config):
        self.config = config

    def install_authorized_ids(self):
        try:
            self.authorized_ids = set(self.config.get("telegram", {}).get("allowed_user_ids", []))
        except Exception as e:
            logger(f"[AuthorizationBot_c:install_authorized_ids_f:authorized_ids_err]: {e}")

    def _is_authorized(self, user: Optional[User]) -> bool:
        if not user:
            return False
        try:
            if not self.authorized_ids:
                logger("[AuthorizationBot_c:_is_authorized_f:authorized_b]: Use without authorized_ids")
                return True
            return user.id in self.authorized_ids
        except Exception as e:
            logger(f"[AuthorizationBot_c:_is_authorized_f:authorized_err]: {e}")
            return False

    async def check_authorized_ids(self, message: Message):
        if not self._is_authorized(message.from_user):
            return await message.answer("⛔ Access Restricted")