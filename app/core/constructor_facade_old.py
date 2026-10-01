from typing import Optional

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

class ConstructorFacade:

    def __init__(self) -> None:
        self.questions_list = None

        self.database_service = DataBaseService()
        self.repo_question = QuestionRepository(self.database_service)

        self.mail_service = MailService()
        self.doc_service = DocWriterService()

        self.bot_command_question = QuestionBotCommands(self.repo_question)

        self.google_service = GoogleService() # not use
        self.remote_service = OpenService() # not use

        self.raw_service: Optional[RawService] = RawService()

        self.remote_services = [self.raw_service]

        self.company_service = CompanyService()

        self.bot_command_question.set_company_service(self.company_service)

        self.telegram_connector = TelegramConnector()
        self.telegram_connector.set_bot_commands(self.bot_command_question)
        self.telegram_connector.install_bot()

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


