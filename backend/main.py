"""Compatibility ASGI entry point (`uvicorn backend.main:app`). See presentation/api/app.py."""
from backend.presentation.api.app import app

__all__ = ["app"]
