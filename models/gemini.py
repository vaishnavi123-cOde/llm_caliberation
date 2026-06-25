import re
from typing import Tuple

from .base import BaseModelClient


class GeminiClient(BaseModelClient):
    def __init__(self, api_key: str, api_url: str = None):
        super().__init__("gemini", api_key, api_url or "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")

    def query(self, prompt: str) -> Tuple[str, float]:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not set. Cannot run experiment with mock data.")

        import requests

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        headers = {"Content-Type": "application/json"}
        url = f"{self.api_url}?key={self.api_key}"
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
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
