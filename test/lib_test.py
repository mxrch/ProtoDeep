from protodeep.lib import guess_schema
from protodeep.errors import ProtoDeepCannotDecode
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
    with pytest.raises(ProtoDeepCannotDecode):
        guess_schema(data=input_data, definitions={'14': 'test_str:string'})

    # Force bad bruteforce index
    # Ref : https://github.com/mxrch/ProtoDeep/issues/4
    with pytest.raises(ProtoDeepCannotDecode):
        guess_schema(data=b'\x83\x01\x88\x01h\x84\x01\x92\x01\x02\x08i', bruteforce_index=0)

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

