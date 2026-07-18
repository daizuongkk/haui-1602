"""Configuration package. Re-exports settings so `from config import THRESHOLDS` works."""
from backend.config.settings import *  # noqa: F401,F403
from backend.config import settings  # noqa: F401
