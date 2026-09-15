from typing import List, Optional, Dict

from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand

from app.cmd.abstract_commands import AbstractCommand
from app.logger.logger_wrapper import LoggerWrapper
from app.repository.abstract_repo import AbstractRepository
from app.service.company_service import CompanyService
from app.service.doc_service import DocWriterService
from app.service.mail_service import MailService

logger = LoggerWrapper()

class QuestionBotCommands(AbstractCommand):

    def __init__(self, repository: AbstractRepository) -> None:
        self.repository: Optional[AbstractRepository] = repository
        self.company_service: Optional[CompanyService] = None
        self.mail_service: Optional[MailService] = None
        self.doc_service: Optional[DocWriterService] = None

        super().__init__()

    def set_doc_service(self, doc_service: DocWriterService) -> None:
        self.doc_service = doc_service

    def set_mail_service(self, mail_service: MailService) -> None:
        self.mail_service = mail_service

    def set_company_service(self, company_service: CompanyService) -> None:
        self.company_service = company_service

    def get_user_command_list(self) -> List[BotCommand]:
        return [
                BotCommand(command="add",     description="Add Question"),
                BotCommand(command="remove",  description="Remove Question by ID"),
                BotCommand(command="list",    description="List of Question"),
                BotCommand(command="find",    description="Find Question by ID"),
                BotCommand(command="check",   description="Find Information by Company Name"),
        ]

    def register_handlers(self) -> None:

        @self.dispatcher.message(Command("start"))
        async def cmd_start(message: Message):
            await self.authorization.check_authorized_ids(message)

            await message.answer(
                f"<b>👋Company Disclosure</b>\n\n"
                f"<b>Commands:</b>\n"
                f"/add Question        — add new Question\n"
                f"/remove by ID          — delete by ID\n"
                f"/find                  — find question by ID\n"
                f"/check                 — AI check starting\n"
                f"/list                  — show all question\n",

                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("add"))
        async def cmd_add(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer(
                    "Usage: /add Question\n"
                )

            logger(f"Current Question: {command.args}")
            try:
                await self.repository.add_question_async(command.args)
            except Exception as e:
                logger(f"Adding question failed: {e}")

            await message.answer(
                f"✅ Question Added: <b>{command.args}</b>",
                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("find"))
        async def cmd_add(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer(
                    "Usage: /find 1\n"
                )

            logger(f"Current ID number: {command.args}")
            id_number = int(command.args)

            question: Optional[str] = None

            try:
                question = await self.repository.find_question_async(id_number)
            except Exception as e:
                logger(f"Adding question failed: {e}")

            if question:
                await message.answer(
                    f"✅ Found Question: {question}",
                )

        @self.dispatcher.message(Command("remove"))
        async def cmd_add(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer(
                    "Usage: /remove 1\n"
                )

            logger(f"Current ID number: {command.args}")
            id_number = int(command.args)

            is_question: Optional[bool] = None

            try:
                is_question = await self.repository.remove_question_async(id_number)
            except Exception as e:
                logger(f"Removing question failed: {e}")

            if is_question:
                await message.answer(
                    f"✅ Question Remove: {is_question} <b>{id_number}</b>",
                    parse_mode=ParseMode.HTML
                )

        @self.dispatcher.message(Command("list"))
        async def cmd_add(message: Message):
            await self.authorization.check_authorized_ids(message)

            question_list: Optional[List] = None

            try:
                question_list = await self.repository.find_all_questions_async()
            except Exception as e:
                logger(f"Found all questions failed: {e}")

            if question_list:

                text = "\n".join(f"- {i+1}: {question}"
                          for i, question in enumerate(question_list))

                await message.answer(
                    f"✅ Obtain next answers:\n {text}"
                )

        @self.dispatcher.message(Command("check"))
        async def cmd_check(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            answers:Optional[Dict] = None

            if not command.args:
                return await message.answer(
                    "How to use: /check CompanyName\n"
                )
            try:
                company_name = command.args
                answers = await self.company_service.request_to_service(company_name)
            except Exception as e:
                logger(f"Checking company failed: {e}")

            if self.doc_service:
                question_answer = [(key, value) for key, value in answers.items()]
                await self.doc_service.save_answers(question_answer)

            if answers:
                text = "\n".join(f"- {key}: {value}" for key, value in answers.items())

                if self.mail_service:
                    await self.mail_service.send_message(subject="Company Digest", body=text)

                await message.answer(
                    f"✅ Obtain next answers: {text}"
                )


