"""
Alert-level vocabulary shared by every layer.

Single source of truth for the four-level severity scale so the pipeline, the
translation agent and the API can never drift apart on ordering or labels.
"""
from typing import Iterable

GREEN, YELLOW, ORANGE, RED = "Green", "Yellow", "Orange", "Red"

PRIORITY = {GREEN: 0, YELLOW: 1, ORANGE: 2, RED: 3}
ORDER = [RED, ORANGE, YELLOW, GREEN]

LABELS = {
    RED: "Cực kỳ nguy hiểm",
    ORANGE: "Nguy hiểm",
    YELLOW: "Chú ý",
    GREEN: "Bình thường",
}
EMOJI = {RED: "🔴", ORANGE: "🟠", YELLOW: "🟡", GREEN: "🟢"}

# A hazard "fires" (warrants broadcasting) at Orange or above.
WARNING_LEVELS = frozenset({ORANGE, RED})


def most_severe(levels: Iterable[str]) -> str:
    """Return the highest-priority level in `levels`, or Green if none."""
    best = GREEN
    for level in levels:
        if PRIORITY.get(level, 0) > PRIORITY.get(best, 0):
            best = level
    return best
