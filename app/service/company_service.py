from typing import Optional, List, Dict

from app.logger.logger_wrapper import LoggerWrapper
from app.respondent.remote_service import RemoteService

logger = LoggerWrapper()

class CompanyService:
    def __init__(self) -> None:
        self.remote_service: Optional[RemoteService] = None
        self.question_from_db: Optional[List] = None

    def set_remote_service(self, remote_service: Optional[RemoteService]) -> None:
        self.remote_service = remote_service

    def set_question_db(self, question_db: Optional[List]) -> None:
        self.question_from_db = question_db

    async def request_to_service(self, company_name: Optional[str]) -> Optional[Dict]:
        answers: Optional[Dict] = {}

        if not self.remote_service or not self.question_from_db:
            return {}

        try:
           self.question_from_db[1] = self.question_from_db[1].replace("*****", company_name)
           logger(f"Edited question with company's name: {self.question_from_db[1]}")

           for question in self.question_from_db:
               answer = await self.remote_service.generate(question)
               answers[question] = answer

           await self.remote_service.close()
           return answers

        except Exception as e:
            logger(f"Error question: {e}")
            return None