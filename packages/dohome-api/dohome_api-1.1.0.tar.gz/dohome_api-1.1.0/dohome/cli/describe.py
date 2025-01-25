"""Describe handlers for the DoHome CLI"""
from __future__ import annotations
from arrrgs import command

from dohome.api import APIClient, parse_hardware_info, HardwareInfo
from dohome.color import parse_state, ParsedState, LightMode

from .batch import get_devices, parallel_run

_Description = tuple[HardwareInfo, ParsedState]

async def _describe_client(device: APIClient) -> tuple[_Description]:
    info = await device.get_device_info()
    raw_state = await device.get_state()
    return parse_hardware_info(info["dev_id"]), parse_state(raw_state)

@command()
async def describe(args):
    """Describe the device(s)"""
    print("Connecting")
    devices = await get_devices(args)
    print("Reading information")
    descriptions = await parallel_run(_describe_client, devices)
    for info, state in descriptions:
        info: HardwareInfo
        state: ParsedState
        print(f"SID: {info['sid']}")
        print(f" - Mac: {info['mac']}")
        print(f" - Type: {info['type'].name}")
        print(f" - Enabled: {state['is_on']}")
        if not state['is_on']:
            continue
        print(f" - Mode: {state['mode'].name}")
        print(f" - Brightness: {state['brightness']}")
        if state['mode'] == LightMode.RGB:
            print(f" - Color: {state['color']}")
        elif state['mode'] == LightMode.WHITE:
            print(f" - White temperature: {state['temperature']}")
        else:
            print(f" - Unknown mode: {state['mode']}")
        print()
