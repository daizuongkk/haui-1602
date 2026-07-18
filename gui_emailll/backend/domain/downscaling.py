"""Terrain downscaling — pure physics, no I/O."""
from typing import Optional

from backend.config import settings


def downscale_temperature(
    model_temp: Optional[float], real_elevation: float, model_elevation: float
) -> Optional[float]:
    """
    Correct a coarse-grid model temperature to a location's true elevation using
    the atmospheric lapse rate. Returns None when the input is missing.
    """
    if model_temp is None:
        return None
    elevation_diff = real_elevation - model_elevation
    return round(model_temp - settings.LAPSE_RATE * elevation_diff, 1)
