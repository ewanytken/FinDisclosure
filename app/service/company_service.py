from typing import Optional, List, Dict

from app.logger.logger_wrapper import LoggerWrapper
from app.models.models import QuestionModel
from app.respondent.abstract_external_model import AbstractModelExternal

logger = LoggerWrapper()

class CompanyService:
    def __init__(self) -> None:
        self.remote_services: Optional[List[AbstractModelExternal]] = None
        self.question_from_db: Optional[List[QuestionModel]] = None

    def set_remote_services(self, remote_services: Optional[List[AbstractModelExternal]]) -> None:
        self.remote_services = remote_services

    def set_question_db(self, question_db: Optional[List]) -> None:
        self.question_from_db = question_db

    async def request_to_service_ask(self, issue: Optional[str]) -> Optional[str]:
        try:
            logger(f"[CompanyService_c:request_to_service_ask_f:issue_v]: {issue}")
            logger(f"[CompanyService_c:request_to_service_ask_f:rem_service_v]: \n {[remote_service for remote_service in self.remote_services]}")

            answer = await self.request_api(issue)

            logger(f"[CompanyService_c:request_to_service_ask_f:answer_from_rs_v]: {answer}")
            return answer
        except Exception as e:
            logger(f"[CompanyService_c:request_to_service_ask_f:answer_v_err]: {e}")
            return None

    async def request_to_service(self, company_name: Optional[str]) -> Optional[Dict]:
        answers: Optional[Dict] = {}

        if not self.question_from_db:
            logger(f"[CompanyService_c:request_to_service_f:db_empty_b]: {len(self.question_from_db)}")
            return {}

        try:
            logger(f"[CompanyService_c:request_to_service_f:company_name_v]: {company_name}")
            # Zero question with 5 astras
            new_question = self.question_from_db[0].get_question().replace("*****", company_name)
            self.question_from_db[0].set_question(new_question)

            logger(f"[CompanyService_c:request_to_service_f:new_question_v]: {self.question_from_db[0].get_question()}")
            logger(f"[CompanyService_c:request_to_service_f:rem_service_v]: {[remote_service for remote_service in self.remote_services]}")

            for question in self.question_from_db:
                question = question.get_question()
                answer = await self.request_api(question)
                answers[question] = answer

            return answers

        except Exception as e:
            logger(f"[CompanyService_c:request_to_service_f:answer_err]: {e}")
            return {}

    async def request_api(self, prompt: Optional[str]) -> Optional[str]:
        answer: Optional[str] = None
        try:
            logger(f"[CompanyService_c:request_api_f:num_r_service_v]: {len(self.remote_services)}")
            for remote_service in self.remote_services:
                answer = await remote_service.generate(prompt)
        except Exception as e:
            logger(f"[CompanyService_c:request_api_f:answer_err]: {e}")

        return answer


