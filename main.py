import asyncio

from app.cmd.question_commands import QuestionBotCommands
from app.core.constructor_facade import ConstructorFacade
from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.repository.question_repo import QuestionRepository
from app.respondent.remote_service import RemoteService
from app.service.company_service import CompanyService
from app.telegram.telegram_connector import TelegramConnector
from app.utils import Utils

logger = LoggerWrapper()

async def main():

    logger("=== Disclosure Company starting ===")
    #
    # database_service = DataBaseService()
    # await database_service.init_session()
    #
    # repo_question = QuestionRepository(database_service)
    # await repo_question.seed_questions()
    # questions_list = await repo_question.find_all_questions_async()
    #
    # bot_command_question = QuestionBotCommands(repo_question)
    #
    # remote_service = RemoteService()
    # company_service = CompanyService()
    # company_service.set_remote_service(remote_service)
    # company_service.set_question_db(questions_list)
    #
    # bot_command_question.set_company_service(company_service)
    #
    # telegram_connector = TelegramConnector()
    # telegram_connector.set_bot_commands(bot_command_question)
    # telegram_connector.install_bot()
    #
    # try:
    #     await telegram_connector.run_bot()
    # except KeyboardInterrupt:
    #     logger("Interrupted by user")
    # finally:
    #     logger("=== Disclosure Monitor stopped ===")

    try:
        await ConstructorFacade().run()
    except KeyboardInterrupt:
        logger("Interrupted by user")
    finally:
        logger("=== Disclosure Monitor stopped ===")


if __name__ == "__main__":
    asyncio.run(main())