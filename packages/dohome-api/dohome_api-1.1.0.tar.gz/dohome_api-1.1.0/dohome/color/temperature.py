"""DoHome Temperature helpers"""

import math
from dohome.api import DO_INT_MAX, DoWhite
from .int import assert_doint

KELVIN_MIN = 3000
KELVIN_MAX = 6400
_KELVIN_DELTA = KELVIN_MAX - KELVIN_MIN

def assert_kelvin(value: int):
    """Asserts kelvin value. Raises ValueError if assertion fails"""
    if not isinstance(value, int):
        raise ValueError(f"Invalid kelvin value: {value}")
    if value < KELVIN_MIN or value > KELVIN_MAX:
        raise ValueError(f"Invalid kelvin value. Out of range: {value}")

def from_dowhite(value: DoWhite, brightness: int) -> int:
    """Converts DoIT value to kelvin"""
    (yellow, blue) = value
    assert_doint(yellow)
    assert_doint(blue)
    assert_doint(yellow + blue)

    print(yellow, blue)

    yellow = (yellow / brightness) * 255
    percent = yellow / DO_INT_MAX
    return math.ceil(percent * _KELVIN_DELTA) + KELVIN_MIN

def to_dowhite(kelvin: int) -> DoWhite:
    """Converts kelvin to DoIT value"""
    assert_kelvin(kelvin)

    percent = (kelvin - KELVIN_MIN) / _KELVIN_DELTA
    yellow = int(percent * DO_INT_MAX)
    blue = DO_INT_MAX - yellow

    print(yellow, blue)
    return (yellow, blue)
