import json
from pathlib import Path
from typing import Any, Dict, Optional
import hashlib

import yaml
from app.logger.logger_wrapper import LoggerWrapper

logger = LoggerWrapper()

class Utils:

    @staticmethod
    def get_config_file(config_path: str = "config.yaml") -> Any:
        path = Path(__file__).parent.parent.parent / config_path
        try:
            with open(path, "r", encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError as e:
            logger(f"Config file not found: by path {path}. Stack trace: {e}")
        except Exception as e:
            logger(f"An error occurred: {e}")
        finally:
            file.close()

    @staticmethod
    def load_questions(path: str = "questions.json") -> Dict[str, str]:

        json_path = Path(__file__).parent.parent.parent/ "dictionary" / path
        logger(f"Loading dictionary from {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                questions_dictionary = json.load(file)
                return questions_dictionary

        except FileNotFoundError as e:
            logger(f"Dictionary file not found: by path {json_path}. Stack trace: {e}")
        except Exception as e:
            logger(f"An error occurred: {e}")
        finally:
            file.close()

    @staticmethod
    def _make_item_id(link: str) -> str:
        return hashlib.sha256(link.encode("utf-8")).hexdigest()[:16]
