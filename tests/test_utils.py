from typing import Optional, List

import pytest
from pathlib import Path
import yaml
from app.logger.logger_wrapper import LoggerWrapper
from app.utils import Utils

logger = LoggerWrapper()

@pytest.mark.asyncio
class Test:

    def setUp(self):
        pass

    def test_document_processing(self):
        config = Utils.get_config_file()
        print(config)
        js = Utils.load_questions()
        print(js)
        for k in js.values():
            print(k)

    async def chinking(self, text: str, max_length: int) -> List[str]:
        chunks: Optional[List[str]] = []
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i + max_length])
        return chunks

    async def test_chunks(self):
        text = "sdfsdfsdf" * 10
        print(f"Result = {len(await self.chinking(text, 4000))}")
        print(f"Text = {await self.chinking(text, 4000)}")


    async def test_document_processing3(self):
        dict = {'status': 200, 'code': 'OK',
         'data': {'id': 'EWX44B42LzKDpkUEiR24h7', 'message_id': '3275f1dd-b6c9-4975-834f-7c93fb1ce932',
                  'answer': 'По последним доступным новостям, компания'}}

        print(dict.get('status', "None"), dict.get('code', "None"), dict.get('data', {}).get('answer', "None"))

    async def test_document_processing4(self):
        APP_ROOT = Path(__file__).resolve().parent.parent
        print(APP_ROOT)
        config_path = APP_ROOT / "config.yaml"
        print(config_path)
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)

        relative_output_dir = config["doc_writer"]["output_dir"]

        final_output_path = (APP_ROOT / relative_output_dir).resolve()

        final_output_path.mkdir(parents=True, exist_ok=True)

        file_to_save = final_output_path / "report.txt"
        with open(file_to_save, "w") as f:
            f.write("Your document content goes here.")

        print(f"Folder and file successfully saved to: {file_to_save}")