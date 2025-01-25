"""DoIT API light types"""
from typing import TypedDict
from .common import DoInt

SetLightStateParams = TypedDict("SetLightStateParams", {
    "on": int,
    "r": DoInt,
    "g": DoInt,
    "b": DoInt,
    "m": DoInt,
    "w": DoInt,
})

LightState = TypedDict("LightState", {
    "r": DoInt,
    "g": DoInt,
    "b": DoInt,
    "w": DoInt,
    "m": DoInt,
})

SetEffectRequest = TypedDict("SetEffectRequest", {
    "cmd": int,
    "index": int, # 1 - 27
})
