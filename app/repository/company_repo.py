from typing import Optional, List

from sqlalchemy import select

from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.models.models import CompanyModel
from app.repository.abstract_repo import AbstractRepository

logger = LoggerWrapper()


class CompanyRepository(AbstractRepository):

    def __init__(self, db_service: Optional[DataBaseService]):
        self.db = db_service

    async def add_company_async(self,
                                ticker: Optional[str] = None,
                                name: Optional[str] = None,
                                inn: Optional[str] = None,
                                isin: Optional[str] = None) -> None:

        try:
            async with self.db.get_session() as session:
                company_obj = CompanyModel(ticker=ticker, name=name, inn=inn, isin=isin)
                session.add(company_obj)
                await session.flush()
                await session.refresh(company_obj)
                logger(f"Added company: {company_obj}")
        except Exception as e:
            logger(f"Company add error: {e}")

    async def find_company_by_ticker_async(self, ticker: str) -> Optional[CompanyModel]:
        try:
            async with self.db.get_session() as session:
                statement = select(CompanyModel).where(CompanyModel.ticker == ticker)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
        except Exception as e:
            logger(f"Company find by ticker error: {e}")
            return CompanyModel(999, "None")

    async def find_companies_by_name_async(self, name: str) -> List[CompanyModel]:
        try:
            async with self.db.get_session() as session:

                statement = select(CompanyModel).where(CompanyModel.name.ilike(f"%{name}%"))
                result = await session.execute(statement)
                return list(result.scalars().all())
        except Exception as e:
            logger(f"Company find by name error: {e}")
            return []

    async def remove_company_by_ticker_async(self, ticker: str) -> bool:
        try:
            async with self.db.get_session() as session:
                statement = select(CompanyModel).where(CompanyModel.name.ilike(f"%{ticker}%"))
                result = await session.execute(statement)
                question = result.scalar_one_or_none()
                if question:
                    await session.delete(question)
                    return True
                return False

        except Exception as e:
            logger(f"Company remove error: {e}")
            return False


