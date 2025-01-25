"""DoHome connection exceptions"""

from .base import DoHomeException


class PayloadTooLong(DoHomeException):
    """Payload too long"""
    def __init__(self, got: int):
        super().__init__(f"Payload too long: {got}, max: 256")

class ClientIsNotResponding(DoHomeException):
    """Client is not responding"""
    def __init__(self, host: str):
        super().__init__(f"Client is not responding at {host}")
