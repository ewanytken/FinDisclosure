import pytest
import requests
from app.respondent.google_service import GoogleService
from app.respondent.raw_service import RawService


@pytest.mark.asyncio
class Test:

    async def test_document_processing(self):
        self.model = GoogleService()
        response = await self.model.generate("Чем занимается российская компания Свои Финансы и какая ее доля участия на рынке")
        print(response)

    async def test_document_processing2(self):
        self.model = RawService()
        response = await self.model.generate("Какая ситуация вокруг компании Евротранс по последним новостям?")
        print(response)

    async def test_document_processing3(self):
        dict = {'status': 200, 'code': 'OK',
         'data': {'id': 'EWX44B42LzKDpkUEiR24h7', 'message_id': '3275f1dd-b6c9-4975-834f-7c93fb1ce932',
                  'answer': 'По последним доступным новостям, компания'}}

        print(dict.get('status', "None"), dict.get('code', "None"), dict.get('data', {}).get('answer', "None"))