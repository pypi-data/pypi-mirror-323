"""DoIT API client"""
from __future__ import annotations
from .transport import APITransport
from .constants import Command, Effect
from .message import format_command, decode_message, assert_response
from .types import (
    DoWhite,
    DoRGB,
    DoTime,
    DeviceInfo,
    LightState,
    BaseResponse,
    SetWiFiCredentialsParams,
    GetWiFiCredentialsResponse,
    SetLightStateParams,
)

class APIClient:
    """DoIT API client"""
    _transport: APITransport

    def __init__(self, transport: APITransport):
        self._transport = transport

    async def reboot(self) -> None:
        """Reboots the device"""
        await self._send_command(Command.REBOOT)

    async def get_device_info(self) -> DeviceInfo:
        """Returns device info"""
        return await self._send_command(Command.GET_DEVICE_INFO)

    async def get_state(self) -> LightState:
        """Reads light state from the device"""
        return await self._send_command(Command.GET_STATE)

    async def set_power(self, is_on: bool) -> None:
        """Turns the device on or off"""
        await self._set_color_state(on=1 if is_on else 0)

    async def set_color(self, color: DoRGB) -> None:
        """Sets RGB color to the device. 0-5000 values"""
        [r, g, b] = color
        await self._set_color_state(r=r, g=g, b=b)

    async def set_white(self, white: DoWhite) -> None:
        """Sets white temperature to the device"""
        [w, m] = white
        await self._set_color_state(w=w, m=m)

    async def set_effect(self, effect: Effect) -> None:
        """Sets effect to the device"""
        await self._send_command(Command.SET_EFFECT, index=effect.value)

    async def get_time(self) -> DoTime:
        """Reads time from the device"""
        return await self._send_command(Command.GET_TIME)

    async def set_time(self, time: DoTime) -> None:
        """Sets time to the device"""
        await self._send_command(Command.SET_TIME, **time)

    async def set_wifi_credentials(self, ssid: str, password: str) -> None:
        """Sets WiFi credentials to the device"""
        req: SetWiFiCredentialsParams = {
            "ssid": ssid,
            "password": password
        }
        await self._send_command(Command.SET_WIFI_CREDENTIALS, **req)

    async def get_wifi_credentials(self) -> GetWiFiCredentialsResponse:
        """Reads WiFi credentials from the device"""
        return await self._send_command(Command.GET_WIFI_CREDENTIALS)

    async def _set_color_state(self, r=0, g=0, b=0, m=0, w=0, on=None) -> None:
        kwargs: SetLightStateParams = {
            "r": r,
            "g": g,
            "b": b,
            "m": m,
            "w": w
        }
        if on is not None:
            kwargs["on"] = on

        await self._send_command(Command.SET_STATE, **kwargs)

    def _encode_request(self, cmd: Command, **kwargs) -> bytes:
        req = format_command(cmd, **kwargs) + "\r\n"
        return req.encode()

    def _handle_response(self, res: BaseResponse, cmd: Command):
        assert_response(res, cmd)
        del res["cmd"]
        del res["res"]

    def _decode_response(self, res: bytes, cmd: Command) -> BaseResponse:
        data: BaseResponse = decode_message(res)
        self._handle_response(data, cmd)
        return data

    async def _send_command(self, cmd: Command, **kwargs):
        req = self._encode_request(cmd, **kwargs)
        res = await self._transport.send(req)
        return self._decode_response(res, cmd)
