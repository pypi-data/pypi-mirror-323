"""Light handlers for the DoHome CLI"""

from arrrgs import arg, command
from dohome.color import (
    to_dowhite,
    to_dorgb,
    apply_brightness,
    RGBColor,
)
from .batch import get_devices, parallel_run

def _hex_to_rgb(hex_color) -> RGBColor:
    """Converts hex color to RGB tuple"""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError("Invalid hex color")

    r, g, b = hex_color[:2], hex_color[2:4], hex_color[4:]
    return (
        int(r, 16),
        int(g, 16),
        int(b, 16)
    )

@command(name="off")
async def turn_off(args):
    """Turn off the device(s)"""
    devices = await get_devices(args)
    await parallel_run(lambda x: x.set_power(False), devices)

@command(name="on")
async def turn_on(args):
    """Turn off the device(s)"""
    devices = await get_devices(args)
    await parallel_run(lambda x: x.set_power(True), devices)

@command(
    arg("color", type=str, help="HEX color value"),
    arg("--brightness", "-b", type=int, default=255, help="0-255 brightness value"),
    name="color",
)
async def set_color(args):
    """Turn off the device(s)"""
    devices = await get_devices(args)
    try:
        rgb_color = _hex_to_rgb(args.color)
        dorgb_color = to_dorgb(rgb_color)
        dorgb_color = apply_brightness(dorgb_color, args.brightness)
    except ValueError:
        print("Invalid hex color")
        return
    await parallel_run(
        lambda x: x.set_color(dorgb_color), devices)

@command(
    arg("kelvin", type=int, help="Kelvin color temperature"),
    arg("--brightness", "-b", type=int, default=255, help="0-255 brightness value"),
    name="white",
)
async def set_white(args):
    """Turn off the device(s)"""
    white = to_dowhite(args.kelvin)
    white = apply_brightness(white, args.brightness)
    devices = await get_devices(args)
    await parallel_run(
        lambda x: x.set_white(white), devices)
