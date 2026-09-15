from typing import List, Optional

from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand

from app.cmd.abstract_commands import AbstractCommand
from app.logger.logger_wrapper import LoggerWrapper
from app.models.models import CompanyModel

logger = LoggerWrapper()

class ParserBotCommands(AbstractCommand):

    def __init__(self) -> None:

        super().__init__()

    def get_user_command_list(self) -> List[BotCommand]:
        return [
            BotCommand(command="add",    description="Add Company"),
            BotCommand(command="remove", description="Remove Company"),
            BotCommand(command="list",   description="List of Company"),
            BotCommand(command="find",   description="Find Company"),
        ]

    def register_handlers(self) -> None:

        @self.dispatcher.message(Command("start"))
        async def cmd_start(message: Message):
            await self.authorization.check_authorized_ids(message)

            await message.answer(
                f"<b>👋 Disclosure Monitor</b>\n\n"
                f"Бот мониторит раскрытия эмитентов и новости по вашим компаниям.\n\n"
                f"<b>Команды:</b>\n"
                f"/add TICKER — добавить компанию (например, /add MGKL)\n"
                f"/remove TICKER — удалить\n"
                f"/list — список отслеживаемых\n"
                f"/status — статус системы\n"
                f"/check — запустить проверку вручную\n"
                f"/search TICKER — последние новости из архива\n",
                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("add"))
        async def cmd_add(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer(
                    "Использование: /add TICKER [полное название] [ИНН] [ISIN]\n"
                    "Например: /add MGKL ПАО_МГКЛ 7707600245 RU000A0JVJQ8"
                )

            parts = command.args.split()

            logger(f"Parts of Company: {parts}")

            ticker = parts[0].upper()
            name = parts[1].replace("_", " ") if len(parts) > 1 else ticker
            inn = parts[2] if len(parts) > 2 else "not_exist"
            isin = parts[3] if len(parts) > 3 else "not_exist"

            company = CompanyModel(ticker=ticker, name=name, inn=inn, isin=isin)
            logger(f"Company data: {company}")

            await message.answer(
                f"✅ Company Added: <b>{ticker}</b> — {name}\n"
                f"ИНН: {inn}, ISIN: {isin}",
                parse_mode=ParseMode.HTML
            )

        @self.dispatcher.message(Command("remove"))
        async def cmd_remove(message: Message, command: CommandObject):
            await self.authorization.check_authorized_ids(message)

            if not command.args:
                return await message.answer("Использование: /remove TICKER")

            ticker = command.args.split()[0].upper()

            ok = None
            if ok:
                await message.answer(f"✅ {ticker} удалён из мониторинга")
            else:
                await message.answer(f"⚠️ {ticker} не найден в списке")

        @self.dispatcher.message(Command("list"))
        async def cmd_list(message: Message):
            await self.authorization.check_authorized_ids(message)

            companies = []

            if not companies:
                return await message.answer(
                    "📋 Список пуст. Добавьте через /add TICKER"
                )
            lines = [f"📋 <b>Отслеживаемые компании</b> ({len(companies)}):\n"]

            for company in companies:
                line = f"• <b>{company.ticker}</b> — {company.name}"
                if company.inn or company.isin:
                    extra = []
                    if company.inn:
                        extra.append(f"ИНН: {company.inn}")
                    if company.isin:
                        extra.append(f"ISIN: {company.isin}")

                    line += f"\n  ({', '.join(extra)})"
                lines.append(line)

            await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)

        @self.dispatcher.message(Command("find"))
        async def cmd_check(message: Message):
            await self.authorization.check_authorized_ids(message)

            await message.answer("🔍 Checking sources...")
            try:
                # digests = await self.engine.run_full_cycle()
                digests = []

                if not digests:
                    return await message.answer("ℹ️ News don't find")

                for digest in digests:
                    text = digest.render_markdown()
                    if text:
                        # Делим на части если > 4096 символов (лимит Telegram)
                        for i in range(0, len(text), 4000):
                            await message.answer(text[i:i + 4000])
            except Exception as e:
                logger(f"Check error")
                await message.answer(f"❌ Error: {e}")

