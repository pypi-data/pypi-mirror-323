"""Discovery handlers for the DoHome CLI"""

from arrrgs import command
from dohome.api import parse_hardware_info

from .batch import discover_devices

@command()
async def discover():
    """Manifest creation"""
    devices = await discover_devices()
    if not devices:
        print("No devices found")
        return
    print(f"Found {len(devices)} devices")
    for device in devices:
        info = parse_hardware_info(device["device_id"])
        print(f"{device["sta_ip"]} {info['mac']} {info['type'].name}")
