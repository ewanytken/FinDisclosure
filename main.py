import asyncio

from app.cmd.question_commands import QuestionBotCommands
from app.core.constructor_facade import ConstructorFacade
from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.repository.question_repo import QuestionRepository
from app.respondent.remote_service import OpenService
from app.service.company_service import CompanyService
from app.telegram.telegram_connector import TelegramConnector
from app.utils import Utils

logger = LoggerWrapper()

async def main():

    logger("[main_f]: Disclosure Company starting")
    try:
        await ConstructorFacade().run()
    except KeyboardInterrupt:
        logger("[main_f:interrupted_err]: Interrupted by user")
    finally:
        logger("[main_f]: Disclosure Monitor stopped")


if __name__ == "__main__":
    asyncio.run(main())