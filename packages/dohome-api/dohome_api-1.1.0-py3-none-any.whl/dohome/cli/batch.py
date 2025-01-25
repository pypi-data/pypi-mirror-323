"""DoHome batch operations"""
import asyncio
from typing import Iterable, Callable, Coroutine, Any, TypeVar

from dohome.api import discover, APIClient, PingResponse
from dohome.socket import UDPBroadcast, TCPStream

async def discover_devices() -> list[PingResponse]:
    """Discovers DoHome devices on the network"""
    broadcast = UDPBroadcast()
    ping_responses = await discover(broadcast)
    broadcast.close()
    return ping_responses

async def _open_devices(hosts: list[str]) -> Iterable[APIClient]:
    """Connects to the DoHome devices"""
    streams = map(TCPStream, hosts)
    clients = map(APIClient, streams)
    return clients

def _parse_hosts(hosts_str: str) -> Iterable[str]:
    hosts = map(lambda x: x.strip(), hosts_str.split(","))
    hosts = filter(lambda x: x != "", hosts)
    return hosts

async def get_devices(args) -> Iterable[APIClient]:
    """Opens DoHome devices from args"""
    if args.hosts == "all":
        responses = await discover_devices()
        hosts = map(lambda x: x["sta_ip"], responses)
    else:
        hosts = _parse_hosts(args.hosts)
    return await _open_devices(hosts)

T = TypeVar('T')
R = TypeVar('R')

async def parallel_run(
        func: Callable[[T], Coroutine[Any, Any, R]],
        args: Iterable[T]) -> Iterable[R]:
    """Runs multiple functions in parallel"""
    return await asyncio.gather(*map(func, args))
