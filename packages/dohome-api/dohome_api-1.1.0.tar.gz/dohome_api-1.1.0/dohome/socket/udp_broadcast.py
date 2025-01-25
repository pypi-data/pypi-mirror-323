"""UDP Broadcast Transport"""
import asyncio
import socket
from collections import deque
from dohome.api import PORT_UDP, BroadcastAPITransport

from .utils import get_discovery_host

_Address = tuple[str, int]

class UDPBroadcast(BroadcastAPITransport):
    """UDP Broadcast Transport"""
    _address: _Address
    _read_timeout: float

    def __init__(self, host: str = None, read_timeout=2.0, listen_port=0):
        if host is None:
            host = get_discovery_host()
        self._address = (host, PORT_UDP)
        self._read_timeout = read_timeout

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.bind(('', listen_port))
        self.sock.setblocking(False)

        self.receive_queue = deque()
        self.lock = asyncio.Lock()

        self.loop = asyncio.get_event_loop()
        self.listener_task = self.loop.create_task(self._listener())

    async def _listener(self):
        """Listen for incoming UDP broadcasts"""
        while True:
            try:
                data, _ = await self.loop.sock_recvfrom(self.sock, 256)
                async with self.lock:
                    self.receive_queue.append(data)
            except asyncio.CancelledError:
                break
            except Exception as e:
                raise e

    async def send(self, payload: bytes) -> list[bytes]:
        """Send a UDP broadcast payload and return the received messages"""
        await self.loop.sock_sendto(
            self.sock,
            payload,
            self._address,
        )
        return await self.read(self._read_timeout)

    async def read(self, read_timeout=None) -> list[bytes]:
        """Read messages from the UDP broadcast socket"""
        if read_timeout is not None:
            await asyncio.sleep(read_timeout)
        async with self.lock:
            messages = list(self.receive_queue)
            self.receive_queue.clear()
        return messages

    def close(self):
        """Close the UDP broadcast socket"""
        self.listener_task.cancel()
        self.sock.close()
