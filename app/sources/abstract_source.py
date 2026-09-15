from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class AbstractSource(ABC):

    config: Optional[Dict] = None

    def set_config(self, config: Dict):
        self.config = config

    @abstractmethod
    def extract_data(self) -> str:
        raise NotImplementedError