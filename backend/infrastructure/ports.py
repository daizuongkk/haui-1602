"""
Ports — abstract boundaries the application depends on (Dependency Inversion).

The application layer talks to these Protocols, not to concrete SDKs, so the
weather source, LLM and TTS engine can be swapped or faked in tests.
"""
from pathlib import Path
from typing import NamedTuple, Protocol


class WeatherProvider(Protocol):
    def fetch(self, lat: float, lon: float) -> dict:
        """Return the raw hourly forecast payload for a coordinate."""
        ...


class LlmJsonClient(Protocol):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Return the model's raw text response, or raise on API failure."""
        ...


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str, lang: str, destination: Path) -> None:
        """Render `text` to an audio file at `destination`."""
        ...


class DispatchResult(NamedTuple):
    status: str          # "sent_sim" | "failed"
    error: str | None = None


class MessageChannel(Protocol):
    """Kênh phân phối (SMS/Zalo/loa). Adapter mô phỏng hôm nay, gateway thật sau."""

    name: str

    def send(self, payload: dict) -> DispatchResult:
        """'Gửi' payload đã dựng sẵn; trả trạng thái. Adapter mô phỏng không gửi thật."""
        ...
