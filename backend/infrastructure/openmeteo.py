"""Open-Meteo weather provider (implements ports.WeatherProvider)."""
import json
import urllib.request

from backend.config import settings


class OpenMeteoWeatherProvider:
    """Fetches the 7-day hourly forecast for a coordinate from Open-Meteo."""

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    def fetch(self, lat: float, lon: float) -> dict:
        variables = ",".join(settings.WEATHER_VARIABLES)
        url = (
            f"{settings.OPEN_METEO_FORECAST_URL}"
            f"?latitude={lat}&longitude={lon}"
            f"&hourly={variables}"
            f"&timezone={settings.OPEN_METEO_TIMEZONE}"
        )
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=self._timeout) as response:
            return json.loads(response.read().decode("utf-8"))
