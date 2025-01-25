"""DoIT API broadcast client"""
from logging import getLogger
from .transport import BroadcastAPITransport
from .client import APIClient
from .constants import Command, DatagramCommand
from .message import (
    decode_datagram,
    format_datagram,
    format_command,
)
from .types import (
    BaseResponse,
    GetWiFiCredentialsResponse,
    PingResponse,
)

_LOGGER = getLogger(__name__)

async def discover(transport: BroadcastAPITransport) -> list[PingResponse]:
    """Discovers DoIT API devices on the network"""
    req = format_datagram({
            "cmd": DatagramCommand.PING
        }) + "\n"
    res = await transport.send(req.encode())
    dgrams = map(decode_datagram, res)
    return list(dgrams)

class DatagramClient(APIClient):
    """DoIT API broadcast client"""

    _transport: BroadcastAPITransport
    _sids: list[str]

    def __init__(self, sids: list[str], transport: BroadcastAPITransport):
        self._transport = transport
        self._sids = sids
        super().__init__(transport)

    async def get_wifi_credentials(self) -> list[GetWiFiCredentialsResponse]:
        """Reads WiFi credentials from the device"""
        return await self._send_command(Command.GET_WIFI_CREDENTIALS)

    def _decode_response(self, res: bytes, cmd: Command) -> dict:
        datagram = decode_datagram(res)
        if "op" not in datagram:
            raise ValueError(datagram)
        self._handle_response(datagram["op"], cmd)
        return datagram

    async def _send_command(self, cmd: Command, **kwargs) -> list[BaseResponse]:
        req = format_datagram({
            "cmd": DatagramCommand.CTRL,
            "devices": self._sids,
            "op": format_command(cmd, **kwargs)
        }) + "\r\n"
        res = await self._transport.send(req.encode())
        if len(res) != len(self._sids):
            _LOGGER.warning(
                "Not all responses received: expected %d, got %d",
                len(self._sids),
                len(res))
        res = map(lambda x: self._decode_response(x, cmd), res)
        return list(res)
