import re
from typing import Tuple

from .base import BaseModelClient


class GroqClient(BaseModelClient):
    def __init__(self, api_key: str, api_url: str = None):
        super().__init__("groq", api_key, api_url or "https://api.groq.com/openai/v1/chat/completions")

    def query(self, prompt: str) -> Tuple[str, float]:
        if not self.api_key:
            raise RuntimeError("GROQ_API_KEY is not set. Cannot run experiment with mock data.")

        import requests

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        resp = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        confidence = self._extract_confidence_from_text(text)
        return text, confidence

    def _extract_confidence_from_text(self, text: str) -> float:
        nums = re.findall(r'(\d+\.?\d*)%', text)
        if nums:
            return min(float(nums[-1]) / 100.0, 1.0)
        return 0.5

    def extract_answer(self, response: str, options: list) -> str:
        match = re.search(r'([A-D])(?:\s|\.|$)', response.strip())
        if match:
            idx = ord(match.group(1)) - 65
            if 0 <= idx < len(options):
                return options[idx]
        return ""

    def extract_confidence(self, response: str) -> float:
        return self._extract_confidence_from_text(response)
