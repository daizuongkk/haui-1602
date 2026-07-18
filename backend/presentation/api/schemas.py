"""Request DTOs for the HTTP API."""
from typing import List

from pydantic import BaseModel

from backend.application.broadcasting import DEFAULT_CHANNELS


class BroadcastRequest(BaseModel):
    location_id: str
    date: str
    channels: List[str] = list(DEFAULT_CHANNELS)
