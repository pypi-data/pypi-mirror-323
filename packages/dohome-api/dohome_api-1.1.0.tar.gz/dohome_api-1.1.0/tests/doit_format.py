"""DoIT protocol formatter tests"""
from dohome.doit import (
    Command,
    DatagramCommand,

    format_command,
    format_datagram,
    format_datagram_command,
)


def test_format_command():
    """Test format_command function"""
    assert format_command(Command.GET_DEV_INFO) == '{"cmd":4}'
    assert format_command(
        Command.SET_STATE, r=1, g=2, b=3, m=4, w=5) == '{"cmd":6,"r":1,"g":2,"b":3,"m":4,"w":5}' # noqa: E501

def test_format_datagram():
    """Test format_datagram function"""
    assert format_datagram({"a": 1, "b": 2}) == 'a=1&b=2'
    assert format_datagram({"a": [1, 2, 3]}) == 'a=[1,2,3]'
    assert format_datagram({"a": {"b": 1, "c": 2}}) == 'a={"b":1,"c":2}'

def test_format_datagram_command():
    """Test format_datagram_command function"""
    assert format_datagram_command(DatagramCommand.PING) == 'cmd=ping'
    assert format_datagram_command(
        DatagramCommand.DOIT_COMMAND, op={
            "cmd": Command.SET_STATE,
            "r": 1,
            "g": 2,
            "b": 3,
            "m": 4,
            "w": 5
        }) == 'cmd=ctrl&op={"cmd":6,"r":1,"g":2,"b":3,"m":4,"w":5}'
