def _clamp(value, low=0.0, high=1.0):
    return max(low, min(high, value))


def remap_active_region(x: float, y: float, margin: float = 0.15) -> tuple:
    lo, hi = margin, 1.0 - margin
    span = hi - lo
    if span <= 0:
        return _clamp(x), _clamp(y)
    return _clamp((x - lo) / span), _clamp((y - lo) / span)


def apply_sensitivity(x: float, y: float, gain: float = 1.0, center: float = 0.5) -> tuple:
    return _clamp(center + (x - center) * gain), _clamp(center + (y - center) * gain)


def map_fingertip(x: float, y: float, margin: float = 0.15, gain: float = 1.0) -> tuple:
    x, y = remap_active_region(x, y, margin)
    return apply_sensitivity(x, y, gain)
