"""Math utilities."""
import numpy as np


def normalize(vec):
    """Normalize vector.

    Args:
        vec: Vector to normalize

    Returns:
        Normalized vector
    """
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec / norm
    return vec


def clamp(value, min_val, max_val):
    """Clamp value between min and max.

    Args:
        value: Value to clamp
        min_val: Minimum value
        max_val: Maximum value

    Returns:
        Clamped value
    """
    return max(min_val, min(max_val, value))


def lerp(a, b, t):
    """Linear interpolation.

    Args:
        a: Start value
        b: End value
        t: Interpolation factor (0-1)

    Returns:
        Interpolated value
    """
    return a + (b - a) * t
