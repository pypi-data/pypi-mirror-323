"""DoHome protocol exceptions"""

import json
from .base import DoHomeException


class CommandCodeInvalid(DoHomeException):
    """Invalid command code exception"""

    def __init__(self, got: str, expected: str, expected_title: str):
        super().__init__(
            f"Invalid command code: {got}, expected: {expected} ({expected_title})")

class CommandCodeNotFound(DoHomeException):
    """Command not found exception"""

    def __init__(self, res: dict, code: int, title: str):
        super().__init__(
            f"Command code not found: {title} ({code}) at response: {json.dumps(res)}")

class ResponseCodeInvalid(DoHomeException):
    """Invalid response code exception"""

    def __init__(self, code: int, title: str):
        super().__init__(f"Invalid response code: {code} ({title})")

class ResponseCodeNotFound(DoHomeException):
    """Response code not found exception"""

    def __init__(self, res: dict):
        super().__init__(f"Response code not found at response: {json.dumps(res)}")
