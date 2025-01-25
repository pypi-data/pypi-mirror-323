"""DoIT API transport"""
from abc import ABC, abstractmethod

class APITransport(ABC):
    """DoIT API transport interface"""

    @abstractmethod
    async def send(self, payload: bytes) -> bytes:
        """Sends data to DoIT API device"""

class BroadcastAPITransport(ABC):
    """DoIT API broadcast transport interface"""

    @abstractmethod
    async def send(self, payload: bytes) -> list[bytes]:
        """Sends data to DoIT API devices"""
