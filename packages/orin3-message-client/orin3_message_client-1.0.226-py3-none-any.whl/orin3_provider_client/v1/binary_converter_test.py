from orin3_provider_client.v1.binary_converter import BinaryConverter


def test_bool_convert1():
    excepted = bytes([2, 1])
    actual = BinaryConverter.from_bool_to_bytes(True)
    assert actual == excepted

def test_bool_convert2():
    excepted = bytes([2, 0])
    actual = BinaryConverter.from_bool_to_bytes(False)
    assert actual == excepted

def test_dict_convert1():
    expected = bytes([0, 0, 0, 0])
    actual = BinaryConverter.from_dict_to_bytes({})
    assert actual == expected