import os
from typing import List, Optional

from dotenv import load_dotenv

from app.cmd.question_commands import QuestionBotCommands
from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.repository.question_repo import QuestionRepository
from app.respondent.google_service import GoogleService
from app.respondent.raw_service import RawService
from app.respondent.remote_service import OpenService
from app.service.company_service import CompanyService
from app.service.doc_service import DocWriterService
from app.service.mail_service import MailService
from app.telegram.telegram_connector import TelegramConnector

logger = LoggerWrapper()

# Map env-token -> service class. Extend here when new remote services are added.
_SERVICE_REGISTRY = {
    "raw": RawService,
    "open": OpenService,
    "google": GoogleService,
}

class ConstructorFacade:

    def __init__(self) -> None:
        self.questions_list = None

        self.database_service = DataBaseService()
        self.repo_question = QuestionRepository(self.database_service)

        self.mail_service = MailService()
        self.doc_service = DocWriterService()

        self.bot_command_question = QuestionBotCommands(self.repo_question)

        # Instantiate lazily only what is selected, but keep references available
        # so other code paths can still import them if needed.
        self.google_service: Optional[GoogleService] = None
        self.remote_service: Optional[OpenService] = None
        self.raw_service: Optional[RawService] = None

        self.remote_services: List = self._resolve_remote_services()

        # Keep typed handles for convenience / backward-compat.
        for svc in self.remote_services:
            if isinstance(svc, RawService):
                self.raw_service = svc
            elif isinstance(svc, OpenService):
                self.remote_service = svc
            elif isinstance(svc, GoogleService):
                self.google_service = svc

        logger(f"[ConstructorFacade_c:remote_services_number_l]: {len(self.remote_services)}")

        self.company_service = CompanyService()

        self.bot_command_question.set_company_service(self.company_service)

        self.telegram_connector = TelegramConnector()
        self.telegram_connector.set_bot_commands(self.bot_command_question)
        self.telegram_connector.install_bot()

    @staticmethod
    def _resolve_remote_services() -> List:
        """
        Decide which remote services to activate.

        Priority:
          1. env var REMOTE_SERVICE (comma-separated, e.g. "raw,open,google")
          2. config.yaml key `active_remote_services` (list)
          3. fallback default: ["raw"]  (preserves original behaviour)

        Unknown tokens are skipped with a warning instead of crashing.
        """
        from app.utils import Utils

        load_dotenv()

        requested: Optional[List[str]] = None

        env_val = os.environ.get("REMOTE_SERVICE", "").strip()
        if env_val:
            logger(f"[ConstructorFacade_c:resolve_remote_services_f:env_val_v]: Download from .env")
            requested = [t.strip().lower() for t in env_val.split(",") if t.strip()]

        if not requested:
            cfg = Utils.get_config_file() or {}
            requested = [str(t).strip().lower() for t in (cfg.get("active_remote_services") or [])]

        if not requested:
            requested = ["raw"]

        # Defensive: tokens themselves may contain commas if someone wrote them as
        # a single list item. Flatten so "open,google" -> ["open", "google"].
        flattened: List[str] = []
        for token in requested:
            flattened.extend([t.strip().lower() for t in token.split(",") if t.strip()])
        requested = flattened

        services: List = []
        for token in requested:
            cls = _SERVICE_REGISTRY.get(token)
            if cls is None:
                logger(f"[ConstructorFacade_c:resolve_remote_services_f:unknown_service_v]: "
                       f"'{token}' is not a known service (raw|open|google). Skipped.")
                continue
            try:
                services.append(cls())
                logger(f"[ConstructorFacade_c:resolve_remote_services_f:activated_v]: {token}")
            except Exception as e:
                logger(f"[ConstructorFacade_c:resolve_remote_services_f:activate_err]: "
                       f"failed to activate '{token}': {e}")
        if not services:
            logger("[ConstructorFacade_c:resolve_remote_services_f:empty_v]: "
                   "no remote services activated, falling back to raw_service.")
            services.append(RawService())
        return services

    async def run(self) -> None:
        try:
            await self.database_service.init_session()
            await self.repo_question.seed_questions()

            self.questions_list = await self.repo_question.find_all_questions_async()

            self.company_service.set_remote_services(self.remote_services)
            self.company_service.set_question_db(self.questions_list)

            self.bot_command_question.set_doc_service(self.doc_service)
            self.bot_command_question.set_mail_service(self.mail_service)

            await self.telegram_connector.run_bot()

            logger(f"[ConstructorFacade_c:run_f]: Bot Started")
        except Exception as e:
            logger(f"[ConstructorFacade_c:run_f:run_err]: {e}")


