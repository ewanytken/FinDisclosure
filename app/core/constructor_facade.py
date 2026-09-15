from app.cmd.question_commands import QuestionBotCommands
from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.repository.question_repo import QuestionRepository
from app.respondent.remote_service import RemoteService
from app.service.company_service import CompanyService
from app.telegram.telegram_connector import TelegramConnector

logger = LoggerWrapper()

class ConstructorFacade:
    def __init__(self) -> None:
        self.questions_list = None

        self.database_service = DataBaseService()
        self.repo_question = QuestionRepository(self.database_service)
        self.bot_command_question = QuestionBotCommands(self.repo_question)

        self.remote_service = RemoteService()
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
            self.company_service.set_remote_service(self.remote_service)
            self.company_service.set_question_db(self.questions_list)
            await self.telegram_connector.run_bot()
        except Exception as e:
            logger(f"Initialization exception: {e}")


