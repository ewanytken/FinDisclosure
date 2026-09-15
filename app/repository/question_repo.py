from typing import Optional, List

from sqlalchemy import select

from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService
from app.models.models import QuestionModel
from app.repository.abstract_repo import AbstractRepository
from app.utils import Utils

logger = LoggerWrapper()

class QuestionRepository(AbstractRepository):

    def __init__(self, db_service: DataBaseService):
        self.db = db_service

    async def add_question_async(self, question: Optional[str] = None):
        try:
            async with self.db.get_session() as session:
                question_obj = QuestionModel(question=question)
                session.add(question_obj)
                await session.flush()
                await session.refresh(question_obj)
                logger(f"Question added: {question_obj}")
        except Exception as e:
            logger(f"Error added question: {e}")

    async def find_question_async(self, id_question: Optional[int]) -> Optional[QuestionModel]:
        try:
            async with self.db.get_session() as session:
                statement = select(QuestionModel).where(QuestionModel.id == id_question)
                result = await session.execute(statement)
                return result.scalar_one_or_none()
        except Exception as e:
            logger(f"Question find error: {e}")
            return None

    async def find_all_questions_async(self) -> List[QuestionModel]:
        try:
            async with self.db.get_session() as session:
                statement = select(QuestionModel).order_by(QuestionModel.id)
                result = await session.execute(statement)
                return list(result.scalars().all())
        except Exception as e:
            logger(f"Questions list error: {e}")
            return []

    async def remove_question_async(self, id_question: Optional[int]) -> bool:
        try:
            async with self.db.get_session() as session:
                statement = select(QuestionModel).where(QuestionModel.id == id_question)
                result = await session.execute(statement)
                question = result.scalar_one_or_none()
                if question:
                    await session.delete(question)
                    return True
                return False
        except Exception as e:
            logger(f"Question remove error: {e}")
            return False

    async def seed_questions(self) -> None:
        INITIAL_QUESTIONS = Utils.load_questions()
        try:
            async with self.db.get_session() as session:

                result = await session.execute(select(QuestionModel).limit(1))
                if result.scalar_one_or_none() is not None:
                    logger("Questions already seeded, skipping")
                    return

                for question in INITIAL_QUESTIONS.values():
                    session.add(QuestionModel(question=question))

                await session.flush()
                logger(f"Seeded {len(INITIAL_QUESTIONS)} questions")

        except Exception as e:
            logger(f"Question seeding error: {e}")

