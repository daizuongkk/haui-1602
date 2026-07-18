"""
Gemini LLM client (implements ports.LlmJsonClient).

A thin adapter: it performs exactly one generation call and returns the raw
text. Retry, parsing and validation policy live in the application layer.
"""
from google import genai

from backend.config import settings


class GeminiClient:
    def __init__(self, api_key: str, model: str = settings.GEMINI_MODEL) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self._model,
            contents=[{"role": "user", "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}],
            config=genai.types.GenerateContentConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                response_mime_type="application/json",
            ),
        )
        return response.text or ""
