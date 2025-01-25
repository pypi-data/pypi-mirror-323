"""DoIT API device types"""
from typing import TypedDict

DeviceInfo = TypedDict("DeviceInfo", {
    "tz": int,
    "ver": str,
    "dev_id": str,
    "conn": int, # 0 - not connected, 1 - connected
    "remote": int, # 0 - remote control disabled, 1 - enabled
    "save_off_stat": int, # 0 - disabled, 1 - enabled
    "repeater": int, # 0 - disabled, 1 - enabled
    "portal": int, # 0 - disabled, 1 - enabled
    "chip": str
})
