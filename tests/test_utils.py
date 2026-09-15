import unittest

from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_document_processing(self):
        config = Utils.get_config_file()
        print(config)
        js = Utils.load_questions()
        print(js)
        for k in js.values():
            print(k)

    if __name__ == '__main__':
        unittest.main()