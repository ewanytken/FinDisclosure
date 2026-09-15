import unittest
from unittest import IsolatedAsyncioTestCase
from app.logger.logger_wrapper import LoggerWrapper
from app.models.db_setup import DataBaseService, QuestionRepository

logger = LoggerWrapper()

class Test(IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        pass

    async def test_db(self):
        db = DataBaseService()
        await db.init_session()

        repo = QuestionRepository(db)
        await repo.add_question_async("AAAAAAA")
        all = await repo.find_all_questions_async()
        q = await repo.find_question_async(1)
        print(all)
        print(q)

        await db.close_session()
        self.assertIsNotNone(q)

    if __name__ == '__main__':
        unittest.main()