"""DoIT protocol response assertion tests"""
import pytest
from dohome.doit import (
    Command,
    ResponseCode,
    assert_response,
)
from dohome.exc import (
    ResponseCodeNotFound,
    ResponseCodeInvalid,
    CommandCodeInvalid,
    CommandCodeNotFound
)


def test_assert_response():
    """Test assert_response function"""
    with pytest.raises(CommandCodeNotFound):
        assert_response({"a": 1, "b": 2}, Command.GET_TIME)
    with pytest.raises(CommandCodeInvalid):
        assert_response({"cmd": Command.GET_STATE.value, "b": 2}, Command.GET_TIME)
    with pytest.raises(ResponseCodeNotFound):
        assert_response({"cmd": Command.GET_TIME.value}, Command.GET_TIME)
    with pytest.raises(ResponseCodeInvalid):
        assert_response({"cmd": Command.GET_TIME.value, "res": 1}, Command.GET_TIME)

    assert_response(
        {"cmd": Command.GET_TIME.value, "res": ResponseCode.OK.value}, Command.GET_TIME)
