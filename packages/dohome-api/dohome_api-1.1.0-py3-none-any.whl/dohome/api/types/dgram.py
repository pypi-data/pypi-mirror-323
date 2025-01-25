"""DoIT API datagram types"""
from typing import TypedDict

PingResponse = TypedDict('PingResponse', {
    'cmd': str,
    'host_ip': str,
    'sta_ip': str,
    'device_id': str,
    'device_key': str,
    'device_name': str,
    'device_type': str,
    'compandy_id': str,
    'chip': str,
})
