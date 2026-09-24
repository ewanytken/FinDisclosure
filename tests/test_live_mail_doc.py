import ssl
from pathlib import Path
from typing import Optional, Dict

import certifi
import pytest

from app.service.doc_service import DocWriterService
from app.service.mail_service import MailService


@pytest.mark.asyncio
class Test:

    async def test_document_processing(self):
        answers: Optional[Dict] = {"Какая ситуация вокруг компании Евротранс по последним новостям?": "По последним новостям, вокруг компании «ЕвроТранс» (ПАО «ЕвроТранс», тикер EUTR на Московской бирже) "}
        self.doc_service = DocWriterService()
        if self.doc_service:
            question_answer = [(key, value) for key, value in answers.items()]
            self.doc_service.set_company_name("euro_test")
            await self.doc_service.save_answers(question_answer, )

    async def test_document_processing_2(self):
        answers: Optional[Dict] = {"Какая ситуация вокруг компании Евротранс по последним новостям?": "По последним новостям, вокруг компании «ЕвроТранс» (ПАО «ЕвроТранс», тикер EUTR на Московской бирже) "}

        self.mail_service = MailService()
        if answers:
            text = "\n".join(f"- {key}: {value}" for key, value in answers.items())
            path = Path(__file__).parent.parent / "reports/euro_test_20260924_122050.docx"
            if self.mail_service:
                self.mail_service.set_attachments([path])
                await self.mail_service.send_message(subject=f"Анализ", body=text)

    async def test_document_processing_3(self):
        answers: Optional[Dict] = {
            "Какая ситуация вокруг компании Евротранс по последним новостям?": "По последним новостям, вокруг компании «ЕвроТранс» (ПАО «ЕвроТранс», тикер EUTR на Московской бирже) "}
        self.doc_service = DocWriterService()
        self.mail_service = MailService()

        path_to_file: Optional[Path] = None
        if self.doc_service:
            question_answer_tuple = [(key, value) for key, value in answers.items()]
            self.doc_service.set_company_name("SOME COMPANY")
            await self.doc_service.save_answers(question_answer_tuple)
            path_to_file = self.doc_service.get_path_to_file()

        if answers:
            text = "\n".join(f"- {key}: {value}" for key, value in answers.items())

            if self.mail_service:
                if path_to_file:
                    self.mail_service.set_attachments([path_to_file])

                await self.mail_service.send_message(subject=f"Financial Analysis", body=text)