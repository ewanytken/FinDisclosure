import unittest

from app.respondent.google_service import GoogleService


class Test(unittest.TestCase):

    def setUp(self):
        self.model = GoogleService()

    def test_document_processing(self):
        response = self.model.generate("Чем занимается российская компания Свои Финансы и какая ее доля участия на рынке")
        print(response)

if __name__ == '__main__':
    unittest.main()