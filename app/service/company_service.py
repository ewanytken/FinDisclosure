from typing import Optional, List, Dict

from app.logger.logger_wrapper import LoggerWrapper
from app.models.models import QuestionModel
from app.respondent.google_service import GoogleService
from app.respondent.remote_service import RemoteService

logger = LoggerWrapper()

class CompanyService:
    def __init__(self) -> None:
        self.remote_service: Optional[RemoteService] = None
        self.google_service: Optional[GoogleService] = None
        self.question_from_db: Optional[List[QuestionModel]] = None

    def set_remote_service(self, remote_service: Optional[RemoteService]) -> None:
        self.remote_service = remote_service

    def set_google_service(self, google_service: Optional[GoogleService]) -> None:
        self.google_service = google_service

    def set_question_db(self, question_db: Optional[List]) -> None:
        self.question_from_db = question_db

    async def request_to_service(self, company_name: Optional[str]) -> Optional[Dict]:
        answers: Optional[Dict] = {}

        if not self.question_from_db:
            logger(f"Empty database: {len(self.question_from_db)}")
            return {}

        try:

            logger(f"Receive next company: {company_name}")
            # Zero question with 5 astras
            new_question = self.question_from_db[0].get_question().replace("*****", company_name)
            self.question_from_db[0].set_question(new_question)

            logger(f"Edited question with company's name: {self.question_from_db[1].get_question()}")
            logger(f"Install next remote service: {self.remote_service}, {self.google_service}")

            for question in self.question_from_db:
                question = question.get_question()

                answer: [Optional[str]] = None

                if self.remote_service:
                    answer = await self.remote_service.generate(question)
                    if not answer:
                        raise Exception()

                if self.google_service:
                    answer = await self.google_service.generate(question)
                    if not answer:
                        raise Exception()

                answers[question] = answer

            await self.remote_service.close()
            return answers

        except Exception as e:
            logger(f"Error question: {e}. Return Empty dictionary or don't obtain answer")
            return {}


