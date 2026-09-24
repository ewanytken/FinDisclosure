import asyncio
from pathlib import Path
from typing import List, Optional, Dict
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand
from aiogram.utils.formatting import Text

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
                BotCommand(command="ask",     description="Ask One Question"),
                BotCommand(command="check",   description="Find Information by Company Name"),
        ]

    def register_handlers(self) -> None:

        @self.dispatcher.message(Command("start"))
        async def cmd_start(message: Message):
            await self.authorization.check_authorized_ids(message)

            await message.answer(
                f"<b>👋Company Disclosure</b>\n\n"
                f"<b>Commands:</b>\n"
                f"/add Question — add new Question\n"
                f"/remove by ID — delete by ID\n"
                f"/find — find question by ID\n"
                f"/check — AI check starting\n"
                f"/ask — Ask one question\n"
                f"/list — show all question\n",

                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("add"))
        async def cmd_add(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer("Usage: /add Question\n")

            logger(f"[QuestionBotCommands_c:cmd_add_f:question_v]: {command.args}")
            try:
                await self.repository.add_question_async(command.args)
            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_add_f]: {e}")

            await message.answer(
                f"✅ Question Added: <b>{command.args}</b>",
                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("find"))
        async def cmd_find(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer("Usage: /find 1\n")

            logger(f"[QuestionBotCommands_c:cmd_find_f:id_v]: {command.args}")
            id_number = int(command.args)

            question: Optional[str] = None

            try:
                question = await self.repository.find_question_async(id_number)
            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_find_f:question_err]: {e}")

            if question:
                await message.answer(f"✅ Found Question: {question}")

        @self.dispatcher.message(Command("remove"))
        async def cmd_remove(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer("Usage: /remove 1\n")

            logger(f"[QuestionBotCommands_c:cmd_remove_f:id_v]: {command.args}")
            id_number = int(command.args)

            is_question: Optional[bool] = None

            try:
                is_question = await self.repository.remove_question_async(id_number)
            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_remove_f:is_question_err]: {e}")

            if is_question:
                await message.answer(
                    f"✅ Question Remove: {is_question} <b>{id_number}</b>",
                    parse_mode=ParseMode.HTML
                )

        @self.dispatcher.message(Command("list"))
        async def cmd_list(message: Message):
            await self.authorization.check_authorized_ids(message)

            question_list: Optional[List] = None

            try:
                question_list = await self.repository.find_all_questions_async()
            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_list_f:question_list_err]: {e}")

            if question_list:
                text = "\n".join(f"- {i+1}: {question}"
                          for i, question in enumerate(question_list))
                await message.answer(f"✅ Obtain next answers:\n {text}")

        @self.dispatcher.message(Command("ask"))
        async def cmd_ask(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer("How to use: /ask Your question\n")

            answer: Optional[str] = None
            try:
                issue = command.args
                answer = await self.company_service.request_to_service_ask(issue)

                if not answer:
                    logger(f"[QuestionBotCommands_c:cmd_ask_f:answer_b]: {answer}")
                    raise Exception()

            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_ask_f:answer_err]: {e}")

            if answer:
                await message.answer(f"✅ Obtain next answers: {answer}")
            else:
                logger(f"[QuestionBotCommands_c:cmd_ask_f:answer_b]: {False}")

        @self.dispatcher.message(Command("check"))
        async def cmd_check(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            answers:Optional[Dict] = None

            if not command.args:
                return await message.answer("How to use: /check CompanyName\n")

            try:
                company_name = command.args
                answers = await self.company_service.request_to_service(company_name)
                if not answers:
                    logger(f"[QuestionBotCommands_c:cmd_check_f:answer_v]: {answers}")
                    raise Exception()

            except Exception as e:
                logger(f"[QuestionBotCommands_c:cmd_check_f:answer_err]: {e}")

            path_to_file: Optional[Path] = None
            if self.doc_service:
                question_answer_tuple = [(key, value) for key, value in answers.items()]
                self.doc_service.set_company_name(command.args)
                await self.doc_service.save_answers(question_answer_tuple)
                path_to_file = self.doc_service.get_path_to_file()
                logger(f"[QuestionBotCommands_c:cmd_check_f:path_to_file_v]: {path_to_file}")

            final_text = "\n".join(f"⭐ {key}:\n 💎{value}" for key, value in answers.items())

            if self.mail_service:
                if path_to_file:
                    self.mail_service.set_attachments([path_to_file])
                await self.mail_service.send_message(subject=f"{command.args} Financial Analysis", body=final_text)

            if answers:
                for key, value in answers.items():
                    if len(value) >= 4096:
                        chunks = await self.chinking(value, max_length=4000)
                        for index, chunk in enumerate(chunks):
                            await message.answer("✅ ".join(f"⭐ {key}. Part #{index+1}:\n 💎{chunk}\n"))
                            await asyncio.sleep(1)
                    else:
                        await message.answer("✅ ".join(f"⭐ {key}: 💎{value}\n"))
                        await asyncio.sleep(1)


    async def chinking(self, text: str, max_length: int) -> List[str]:
        chunks: Optional[List[str]] = []
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i + max_length])
        return chunks
