"""DoIT protocol operation formatter"""
from __future__ import annotations
import json
from enum import Enum
from dohome.exc import (
    ResponseCodeNotFound,
    ResponseCodeInvalid,
    CommandCodeInvalid,
    CommandCodeNotFound,
)
from .constants import Command, DatagramCommand, ResponseCode

def _dump_minified_json(data: dict | list) -> str:
    """Formats minified JSON string"""
    return json.dumps(data, separators=(',', ':'))

def format_command(cmd: Command, **kwargs) -> str:
    """Formats DoIT command request"""
    req = {
        "cmd": cmd.value,
    }
    for key, value in kwargs.items():
        req[key] = value
    return _dump_minified_json(req)

def decode_message(res: bytes) -> dict:
    """Formats DoIT response"""
    data = res.decode("utf-8")
    return json.loads(data)

def assert_response(res: dict, cmd: Command):
    """Asserts DoIT response. Raises ValueError if assertion fails"""
    if "cmd" not in res:
        raise CommandCodeNotFound(res, cmd.value, cmd.name)
    res_cmd = Command(res["cmd"])
    if res_cmd != cmd:
        raise CommandCodeInvalid(res_cmd.value, cmd.value, cmd.name)
    if "res" not in res:
        raise ResponseCodeNotFound(res)
    res_code = ResponseCode(res["res"])
    if res_code != ResponseCode.OK:
        raise ResponseCodeInvalid(res_code.value, res_code.name)

def format_datagram(req: dict) -> str:
    """Formats DoIT datagram request"""
    params = []
    for key, value in req.items():
        if isinstance(value, list | dict):
            value = _dump_minified_json(value)
        elif isinstance(value, Enum):
            value = value.value
        params.append(f"{key}={value}")
    datagram = "&".join(params)
    return datagram

def format_datagram_command(cmd: DatagramCommand, **kwargs) -> str:
    """Formats DoIT datagram command request"""
    req = {
        "cmd": cmd.value,
    }
    for key, value in kwargs.items():
        req[key] = value
    return format_datagram(req)

def decode_datagram(res: bytes) -> dict:
    """Formats DoIT datagram response"""
    data = res.decode("utf-8").strip()
    entries = map(lambda x: x.split("="), data.split("&"))
    data = dict(entries)
    for key, value in data.items():
        if value.startswith("{") or value.startswith("["):
            data[key] = json.loads(value)
        elif value.isdigit():
            data[key] = int(value)
    return data
