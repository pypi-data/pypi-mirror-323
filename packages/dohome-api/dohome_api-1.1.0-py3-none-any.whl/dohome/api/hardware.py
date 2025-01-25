"""DoIT hardware info"""
from typing import TypedDict
from .constants import DeviceType

HardwareInfo = TypedDict("HardwareInfo", {
    "mac": str,
    "sid": str,
    "chip": str,
    "type": DeviceType,
})

def _format_mac(mac: str) -> str:
    return ":".join(mac[i:i+2] for i in range(0, len(mac), 2))

def parse_hardware_info(device_id: str) -> HardwareInfo:
    """Extracts device info from device ID"""
    mac = device_id[0:12]
    rest = device_id[13:]
    [device_type, chip] = rest.split("_")
    return {
        "mac": _format_mac(mac),
        "sid": mac[-4:],
        "type": DeviceType(device_type),
        "chip": chip
    }
