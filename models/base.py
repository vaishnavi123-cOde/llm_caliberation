from abc import ABC, abstractmethod
from typing import Tuple


class BaseModelClient(ABC):
    def __init__(self, model_name: str, api_key: str, api_url: str):
        self.model_name = model_name
        self.api_key = api_key
        self.api_url = api_url

    @abstractmethod
    def query(self, prompt: str) -> Tuple[str, float]:
        pass

    @abstractmethod
    def extract_answer(self, response: str, options: list) -> str:
        pass

    @abstractmethod
    def extract_confidence(self, response: str) -> float:
        pass
