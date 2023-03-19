from protodeep.lib import guess_schema
from protodeep.blackboxprotobuf.lib.exceptions import DecoderException
import pytest


def test_bad_utf8_string():
    input_data = bytes.fromhex('72 01 FF')

    # Default encoding
    schema = guess_schema(data=input_data)
    assert schema.schema == {'14': {'type': 'bytes'}}
    assert schema.values == {'14': b'\xff'}

    # Force bytes
    schema = guess_schema(data=input_data, definitions={'14': 'test_str:bytes'})
    assert schema.schema == {'14': {'type': 'bytes', 'name': 'test_str'}}
    assert schema.values == {'14': b'\xff'}

    # Force bytes_hex
    schema = guess_schema(data=input_data, definitions={'14': 'test_str:bytes_hex'})
    assert schema.schema == {'14': {'type': 'bytes_hex', 'name': 'test_str'}}
    assert schema.values == {'14': b'ff'}

    # Force string
    with pytest.raises(DecoderException):
        guess_schema(data=input_data, definitions={'14': 'test_str:string'})

def test_good_utf8_string():
    input_data = bytes.fromhex('72 01 61')

    # Default encoding
    schema = guess_schema(data=input_data)
    assert schema.schema == {'14': {'type': 'string'}}
    assert schema.values == {'14': 'a'}

    # Force bytes
    schema = guess_schema(data=input_data, definitions={'14': 'test_str:bytes'})
    assert schema.schema == {'14': {'type': 'bytes', 'name': 'test_str'}}
    assert schema.values == {'14': b'a'}

    # Force bytes_hex
    schema = guess_schema(data=input_data, definitions={'14': 'test_str:bytes_hex'})
    assert schema.schema == {'14': {'type': 'bytes_hex', 'name': 'test_str'}}
    assert schema.values == {'14': b'61'}

    # Force string
    schema = guess_schema(data=input_data, definitions={'14': 'test_str:string'})
    assert schema.schema == {'14': {'type': 'string', 'name': 'test_str'}}
    assert schema.values == {'14': 'a'}

