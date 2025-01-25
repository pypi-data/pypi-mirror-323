"""DoHome light state"""
from typing import TypedDict
from enum import Enum

from dohome.api import LightState

from .rgb import RGBColor, from_dorgb
from .int import UInt8, doint_to_uint8
from .temperature import from_dowhite

class LightMode(Enum):
    """Light mode"""
    RGB = "rgb"
    WHITE = "white"

ParsedState = TypedDict("ParsedState", {
    "is_on": bool,
    "brightness": UInt8,
    "mode": LightMode,
    "color": RGBColor,
    "temperature": int
})

def parse_state(res: LightState) -> ParsedState:
    """Reads high-level state from the device"""

    is_on = False
    mode = LightMode.WHITE
    brightness = 255
    temperature = 0

    rgb_color = from_dorgb((res["r"], res["g"], res["b"]))
    white_total = sum([res["w"], res["m"]])

    if sum(rgb_color) > 0:
        mode = LightMode.RGB
        is_on = True
    elif white_total > 0:
        mode = LightMode.WHITE
        is_on = True
        brightness = doint_to_uint8(white_total)
        temperature = from_dowhite((res["w"], res["m"]), brightness)

    return {
        "is_on": is_on,
        "brightness": brightness,
        "mode": mode,
        "color": rgb_color,
        "temperature": temperature
    }
