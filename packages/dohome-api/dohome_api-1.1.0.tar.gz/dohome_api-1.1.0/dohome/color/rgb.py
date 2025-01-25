"""DoHome RGB helpers"""
from __future__ import annotations
from dohome.api import DoRGB
from .int import (
    UInt8,
    uint8_to_doint,
    doint_to_uint8,
    scale_by_uint8,
    assert_uint8,
)

RGBColor = tuple[UInt8, UInt8, UInt8]

def to_dorgb(color: RGBColor) -> DoRGB:
    """Converts RGB color to DoIT RGB color"""
    dorgb_color = map(uint8_to_doint, color)
    return tuple(dorgb_color)

def from_dorgb(color: DoRGB) -> RGBColor:
    """Converts DoIT RGB color to RGB color"""
    rgb_color = map(doint_to_uint8, color)
    return tuple(rgb_color)

def apply_brightness(values: tuple, brightness: UInt8) -> DoRGB:
    """Applies brightness to RGB color"""
    assert_uint8(brightness)

    if brightness == 0:
        return (0, 0, 0)
    if brightness == 255:
        return values

    adjusted_color = map(lambda x: scale_by_uint8(x, brightness), values)
    return tuple(adjusted_color)
