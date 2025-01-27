from datetime import datetime
from typing import List
import math
import struct

from orin3_provider_client.v1.common import DataType
from orin3_provider_client.v1.common import ORiN3Value
from orin3_provider_client.v1.common import ORiN3ValueType


class FromBytesToObjectResult:
    def __init__(self, data_type: int, data: any):
        self.__data_type = data_type
        self.__data = data
    
    @property
    def data_type(self) -> int:
        return self.__data_type
    
    @property
    def data(self) -> any:
        return self.__data


class _ToObjectResult:
    __rest_bytes: bytes
    __result: any

    def __init__(self, rest_bytes: bytes, result: any):
        self.__rest_bytes = rest_bytes
        self.__result = result

    def get_bytes(self) -> bytes:
        return self.__rest_bytes
    
    def get_result(self) -> any:
        return self.__result

class BinaryConverter:
    @staticmethod
    def convert_back_4bytes_for_little_endian(target: bytes) -> int:
        return int.from_bytes(target, 'little')

    @staticmethod
    def convert_float_to_bytes(target: float) -> bytes:
        return bytes(struct.pack("f", target))

    @staticmethod
    def convert_double_to_bytes(target: float) -> bytes:
        return bytes(struct.pack("d", target))

    @staticmethod
    def convert_bytes_to_float(target: bytes) -> bytes:
        return struct.unpack("f", target[:4])[0]

    @staticmethod
    def convert_bytes_to_double(target: bytes) -> float:
        return struct.unpack("d", target[:8])[0]

    @staticmethod
    def from_none_to_bytes() -> bytes:
        return bytes([DataType.NULL.value])

    @staticmethod
    def __from_bool_to_bytes(target: bool) -> bytes:
        return bytes([1 if target else 0])

    @classmethod
    def from_bool_to_bytes(self, target: bool) -> bytes:
        return bytes([DataType.BOOL.value]) + self.__from_bool_to_bytes(target)

    @staticmethod
    def __from_bytes_to_bool(target: bytes) -> bool:
        return True if target[0] == 1 else False

    @classmethod
    def from_bytes_to_bool(self, target: bytes) -> bool:
        return self.__from_bytes_to_bool(target[1:])

    @staticmethod
    def __from_nullable_bool_to_bytes(target: bool) -> bytes:
        return bytes([2 if target is None else 1 if target else 0])

    @classmethod
    def from_nullable_bool_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_BOOL.value]) + self.__from_nullable_bool_to_bytes(target)

    @staticmethod
    def __from_bytes_to_nullable_bool(target: bytes) -> any:
        return None if target[0] == 2 else True if target == 1 else False

    @classmethod
    def from_bytes_to_nullable_bool(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_bool(target[1:])

    @classmethod
    def __from_bool_array_to_bytes(self, target: List[bool]) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_bool_to_bytes(data)
        return buffer

    @classmethod
    def from_bool_array_to_bytes(self, target: List[bool]) -> bytes:
        return bytes([DataType.BOOL_ARRAY.value]) + self.__from_bool_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_bool_array(self, target: bytes) -> List[bool]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index
            buffer.append(self.__from_bytes_to_bool(target[c:c + 1]))
        return buffer

    @classmethod
    def from_bytes_to_bool_array(self, target: bytes) -> List[bool]:
        return self.__from_bytes_to_bool_array(target[1:])

    @classmethod
    def __from_nullable_bool_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_bool_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_bool_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_BOOL_ARRAY.value]) + self.__from_nullable_bool_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_bool_array(self, target: bytes) -> List[bool]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index
            buffer.append(self.__from_bytes_to_nullable_bool(target[c:c + 1]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_bool_array(self, target: bytes) -> List[bool]:
        return self.__from_bytes_to_nullable_bool_array(target[1:])


    #uint8
    @staticmethod
    def __from_uint8_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 1, 'little', signed=False)

    @classmethod
    def from_uint8_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.UINT8.value]) + self.__from_uint8_to_bytes(target)

    @staticmethod
    def __from_bytes_to_uint8(target: bytes) -> int:
        return int.from_bytes(target[:1], 'little', signed=False)

    @classmethod
    def from_bytes_to_uint8(self, target:bytes) -> int:
        return self.__from_bytes_to_uint8(target[1:])

    @staticmethod
    def __from_nullable_uint8_to_bytes(target: any) -> bytes:
        return bytes([0, 0] if target is None else [1, target])

    @classmethod
    def from_nullable_uint8_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_UINT8.value]) + self.__from_nullable_uint8_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint8(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_uint8(target[1:])

    @classmethod
    def from_bytes_to_nullable_uint8(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_uint8(target[1:])

    @classmethod
    def __from_uint8_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_uint8_to_bytes(data)
        return buffer

    @classmethod
    def from_uint8_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.UINT8_ARRAY.value]) + self.__from_uint8_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_uint8_array(self, target: bytes) -> List[bool]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index
            buffer.append(self.__from_bytes_to_uint8(target[c:c + 1]))
        return buffer

    @classmethod
    def from_bytes_to_uint8_array(self, target: bytes) -> List[bool]:
        return self.__from_bytes_to_uint8_array(target[1:])

    @classmethod
    def __from_nullable_uint8_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_uint8_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_uint8_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_UINT8_ARRAY.value]) + self.__from_nullable_uint8_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint8_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 2
            buffer.append(self.__from_bytes_to_nullable_uint8(target[c:c + 2]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_uint8_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_uint8_array(target[1:])



    #int8
    @staticmethod
    def __from_int8_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 1, 'little', signed=True)

    @classmethod
    def from_int8_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.INT8.value]) + self.__from_int8_to_bytes(target)

    @staticmethod
    def __from_bytes_to_int8(target: bytes) -> int:
        return int.from_bytes(target[:1], 'little', signed=True)

    @classmethod
    def from_bytes_to_int8(self, target:bytes) -> int:
        return self.__from_bytes_to_int8(target[1:])

    @classmethod
    def __from_nullable_int8_to_bytes(self, target: any) -> bytes:
        return bytes([0, 0]) if target is None else bytes([1]) + self.__from_int8_to_bytes(target)

    @classmethod
    def from_nullable_int8_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_INT8.value]) + self.__from_nullable_int8_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int8(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_int8(target[1:])

    @classmethod
    def from_bytes_to_nullable_int8(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_int8(target[1:])

    @classmethod
    def __from_int8_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_int8_to_bytes(data)
        return buffer

    @classmethod
    def from_int8_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.INT8_ARRAY.value]) + self.__from_int8_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_int8_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index
            buffer.append(self.__from_bytes_to_int8(target[c:c + 1]))
        return buffer

    @classmethod
    def from_bytes_to_int8_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_int8_array(target[1:])

    @classmethod
    def __from_nullable_int8_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_int8_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_int8_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_INT8_ARRAY.value]) + self.__from_nullable_int8_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int8_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 2
            buffer.append(self.__from_bytes_to_nullable_int8(target[c:c + 2]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_int8_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_int8_array(target[1:])


    #uint16
    @staticmethod
    def __from_uint16_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 2, 'little', signed=False)

    @classmethod
    def from_uint16_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.UINT16.value]) + self.__from_uint16_to_bytes(target)

    @staticmethod
    def __from_bytes_to_uint16(target: bytes) -> int:
        return int.from_bytes(target[:2], 'little', signed=False)

    @classmethod
    def from_bytes_to_uint16(self, target: bytes) -> int:
        return self.__from_bytes_to_uint16(target[1:])

    @staticmethod
    def __from_nullable_uint16_to_bytes(target: any) -> bytes:
        return bytes([0, 0, 0]) if target is None else bytes([1]) + int.to_bytes(target, 2, 'little', signed=False)

    @classmethod
    def from_nullable_uint16_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_UINT16.value]) + self.__from_nullable_uint16_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint16(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_uint16(target[1:])

    @classmethod
    def from_bytes_to_nullable_uint16(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_uint16(target[1:])

    @classmethod
    def __from_uint16_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_uint16_to_bytes(data)
        return buffer

    @classmethod
    def from_uint16_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.UINT16_ARRAY.value]) + self.__from_uint16_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_uint16_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 2
            buffer.append(self.__from_bytes_to_uint16(target[c:c + 2]))
        return buffer

    @classmethod
    def from_bytes_to_uint16_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_uint16_array(target[1:])

    @classmethod
    def __from_nullable_uint16_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_uint16_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_uint16_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_UINT16_ARRAY.value]) + self.__from_nullable_uint16_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint16_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 3
            buffer.append(self.__from_bytes_to_nullable_uint16(target[c:c + 3]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_uint16_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_uint16_array(target[1:])


    #int16
    @staticmethod
    def __from_int16_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 2, 'little', signed=True)

    @classmethod
    def from_int16_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.INT16.value]) + self.__from_int16_to_bytes(target)

    @staticmethod
    def __from_bytes_to_int16(target: bytes) -> int:
        return int.from_bytes(target[:2], 'little', signed=True)

    @classmethod
    def from_bytes_to_int16(self, target: bytes) -> int:
        return self.__from_bytes_to_int16(target[1:])

    @staticmethod
    def __from_nullable_int16_to_bytes(target: any) -> bytes:
        return bytes([0]) + int.to_bytes(0, 2, 'little', signed=True) if target is None else bytes([1]) + int.to_bytes(target, 2, 'little', signed=True)

    @classmethod
    def from_nullable_int16_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_INT16.value]) + self.__from_nullable_int16_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int16(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_int16(target[1:])

    @classmethod
    def from_bytes_to_nullable_int16(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_int16(target[1:])

    @classmethod
    def __from_int16_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_int16_to_bytes(data)
        return buffer

    @classmethod
    def from_int16_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.INT16_ARRAY.value]) + self.__from_int16_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_int16_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 2
            buffer.append(self.__from_bytes_to_int16(target[c:c + 2]))
        return buffer

    @classmethod
    def from_bytes_to_int16_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_int16_array(target[1:])

    @classmethod
    def __from_nullable_int16_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_int16_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_int16_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_INT16_ARRAY.value]) + self.__from_nullable_int16_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int16_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 3
            buffer.append(self.__from_bytes_to_nullable_int16(target[c:c + 3]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_int16_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_int16_array(target[1:])


    #uint32
    @staticmethod
    def __from_uint32_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 4, 'little', signed=False)

    @classmethod
    def from_uint32_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.UINT32.value]) + self.__from_uint32_to_bytes(target)

    @staticmethod
    def __from_bytes_to_uint32(target: bytes) -> int:
        return int.from_bytes(target[:4], 'little', signed=False)

    @classmethod
    def from_bytes_to_uint32(self, target: bytes) -> int:
        return self.__from_bytes_to_uint32(target[1:])

    @staticmethod
    def __from_nullable_uint32_to_bytes(target: any) -> bytes:
        return bytes([0]) + int.to_bytes(0, 4, 'little', signed=False) if target is None else bytes([1]) + int.to_bytes(target, 4, 'little', signed=False)

    @classmethod
    def from_nullable_uint32_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_UINT32.value]) + self.__from_nullable_uint32_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint32(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_uint32(target[1:])

    @classmethod
    def from_bytes_to_nullable_uint32(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_uint32(target[1:])

    @classmethod
    def __from_uint32_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_uint32_to_bytes(data)
        return buffer

    @classmethod
    def from_uint32_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.UINT32_ARRAY.value]) + self.__from_uint32_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_uint32_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 4
            buffer.append(self.__from_bytes_to_uint32(target[c:c + 4]))
        return buffer

    @classmethod
    def from_bytes_to_uint32_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_uint32_array(target[1:])

    @classmethod
    def __from_nullable_uint32_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_uint32_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_uint32_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_UINT32_ARRAY.value]) + self.__from_nullable_uint32_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint32_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 5
            buffer.append(self.__from_bytes_to_nullable_uint32(target[c:c + 5]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_uint32_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_uint32_array(target[1:])


    #int32
    @staticmethod
    def __from_int32_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 4, 'little', signed=True)

    @classmethod
    def from_int32_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.INT32.value]) + self.__from_int32_to_bytes(target)

    @staticmethod
    def __from_bytes_to_int32(target: bytes) -> int:
        return int.from_bytes(target[:4], 'little', signed=True)

    @classmethod
    def from_bytes_to_int32(self, target: bytes) -> int:
        return self.__from_bytes_to_int32(target[1:])

    @staticmethod
    def __from_nullable_int32_to_bytes(target: any) -> bytes:
        return bytes([0]) + int.to_bytes(0, 4, 'little', signed=True) if target is None else bytes([1]) + int.to_bytes(target, 4, 'little', signed=True)

    @classmethod
    def from_nullable_int32_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_INT32.value]) + self.__from_nullable_int32_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int32(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_int32(target[1:])

    @classmethod
    def from_bytes_to_nullable_int32(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_int32(target[1:])

    @classmethod
    def __from_int32_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_int32_to_bytes(data)
        return buffer

    @classmethod
    def from_int32_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.INT32_ARRAY.value]) + self.__from_int32_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_int32_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 4
            buffer.append(self.__from_bytes_to_int32(target[c:c + 4]))
        return buffer

    @classmethod
    def from_bytes_to_int32_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_int32_array(target[1:])

    @classmethod
    def __from_nullable_int32_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_int32_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_int32_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_INT32_ARRAY.value]) + self.__from_nullable_int32_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int32_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 5
            buffer.append(self.__from_bytes_to_nullable_int32(target[c:c + 5]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_int32_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_int32_array(target[1:])


    #uint64
    @staticmethod
    def __from_uint64_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 8, 'little', signed=False)

    @classmethod
    def from_uint64_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.UINT64.value]) + self.__from_uint64_to_bytes(target)

    @staticmethod
    def __from_bytes_to_uint64(target: bytes) -> int:
        return int.from_bytes(target[:8], 'little', signed=False)

    @classmethod
    def from_bytes_to_uint64(self, target: bytes) -> int:
        return self.__from_bytes_to_uint64(target[1:])

    @staticmethod
    def __from_nullable_uint64_to_bytes(target: any) -> bytes:
        return bytes([0]) + int.to_bytes(0, 8, 'little', signed=False) if target is None else bytes([1]) + int.to_bytes(target, 8, 'little', signed=False)

    @classmethod
    def from_nullable_uint64_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_UINT64.value]) + self.__from_nullable_uint64_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint64(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_uint64(target[1:])

    @classmethod
    def from_bytes_to_nullable_uint64(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_uint64(target[1:])

    @classmethod
    def __from_uint64_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_uint64_to_bytes(data)
        return buffer

    @classmethod
    def from_uint64_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.UINT64_ARRAY.value]) + self.__from_uint64_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_uint64_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 8
            buffer.append(self.__from_bytes_to_uint64(target[c:c + 8]))
        return buffer

    @classmethod
    def from_bytes_to_uint64_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_uint64_array(target[1:])

    @classmethod
    def __from_nullable_uint64_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_uint64_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_uint64_array_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_UINT64_ARRAY.value]) + self.__from_nullable_uint64_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_uint64_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 9
            buffer.append(self.__from_bytes_to_nullable_uint64(target[c:c + 9]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_uint64_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_uint64_array(target[1:])


    #int64
    @staticmethod
    def __from_int64_to_bytes(target: int) -> bytes:
        return int.to_bytes(target, 8, 'little', signed=True)

    @classmethod
    def from_int64_to_bytes(self, target: int) -> bytes:
        return bytes([DataType.INT64.value]) + self.__from_int64_to_bytes(target)

    @staticmethod
    def __from_bytes_to_int64(target: bytes) -> int:
        return int.from_bytes(target[:8], 'little', signed=True)

    @classmethod
    def from_bytes_to_int64(self, target: bytes) -> int:
        return self.__from_bytes_to_int64(target[1:])

    @staticmethod
    def __from_nullable_int64_to_bytes(target: any) -> bytes:
        return bytes([0]) + int.to_bytes(0, 8, 'little', signed=True) if target is None else bytes([1]) + int.to_bytes(target, 8, 'little', signed=True)

    @classmethod
    def from_nullable_int64_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_INT64.value]) + self.__from_nullable_int64_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int64(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_int64(target[1:])

    @classmethod
    def from_bytes_to_nullable_int64(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_int64(target[1:])

    @classmethod
    def __from_int64_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_int64_to_bytes(data)
        return buffer

    @classmethod
    def from_int64_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.INT64_ARRAY.value]) + self.__from_int64_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_int64_array(self, target: bytes) -> List[int]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 8
            buffer.append(self.__from_bytes_to_int64(target[c:c + 8]))
        return buffer

    @classmethod
    def from_bytes_to_int64_array(self, target: bytes) -> List[int]:
        return self.__from_bytes_to_int64_array(target[1:])

    @classmethod
    def __from_nullable_int64_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_int64_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_int64_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_INT64_ARRAY.value]) + self.__from_nullable_int64_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_int64_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 9
            buffer.append(self.__from_bytes_to_nullable_int64(target[c:c + 9]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_int64_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_int64_array(target[1:])


    #float
    @classmethod
    def __from_float_to_bytes(self, target: float) -> bytes:
        return self.convert_float_to_bytes(target)

    @classmethod
    def from_float_to_bytes(self, target: float) -> bytes:
        return bytes([DataType.FLOAT.value]) + self.__from_float_to_bytes(target)

    @classmethod
    def __from_bytes_to_float(self, target: bytes) -> float:
        return self.convert_bytes_to_float(target)

    @classmethod
    def from_bytes_to_float(self, target: bytes) -> float:
        return self.__from_bytes_to_float(target[1:])

    @classmethod
    def __from_nullable_float_to_bytes(self, target: any) -> bytes:
        return bytes([0]) + self.convert_float_to_bytes(0) if target is None else bytes([1]) + self.convert_float_to_bytes(target)

    @classmethod
    def from_nullable_float_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_FLOAT.value]) + self.__from_nullable_float_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_float(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_float(target[1:])

    @classmethod
    def from_bytes_to_nullable_float(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_float(target[1:])

    @classmethod
    def __from_float_array_to_bytes(self, target: List[float]) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_float_to_bytes(data)
        return buffer

    @classmethod
    def from_float_array_to_bytes(self, target: List[float]) -> bytes:
        return bytes([DataType.FLOAT_ARRAY.value]) + self.__from_float_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_float_array(self, target: bytes) -> List[float]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 4
            buffer.append(self.__from_bytes_to_float(target[c:c + 4]))
        return buffer

    @classmethod
    def from_bytes_to_float_array(self, target: bytes) -> List[float]:
        return self.__from_bytes_to_float_array(target[1:])

    @classmethod
    def __from_nullable_float_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_float_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_float_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_FLOAT_ARRAY.value]) + self.__from_nullable_float_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_float_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 5
            buffer.append(self.__from_bytes_to_nullable_float(target[c:c + 5]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_float_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_float_array(target[1:])


    #double
    @classmethod
    def __from_double_to_bytes(self, target: float) -> bytes:
        return self.convert_double_to_bytes(target)

    @classmethod
    def from_double_to_bytes(self, target: float) -> bytes:
        return bytes([DataType.DOUBLE.value]) + self.__from_double_to_bytes(target)

    @classmethod
    def __from_bytes_to_double(self, target: bytes) -> float:
        return self.convert_bytes_to_double(target)

    @classmethod
    def from_bytes_to_double(self, target: bytes) -> float:
        return self.__from_bytes_to_double(target[1:])

    @classmethod
    def __from_nullable_double_to_bytes(self, target: any) -> bytes:
        return bytes([0]) + self.convert_double_to_bytes(0) if target is None else bytes([1]) + self.convert_double_to_bytes(target)

    @classmethod
    def from_nullable_double_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_DOUBLE.value]) + self.__from_nullable_double_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_double(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_double(target[1:])

    @classmethod
    def from_bytes_to_nullable_double(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_double(target[1:])

    @classmethod
    def __from_double_array_to_bytes(self, target: List[float]) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_double_to_bytes(data)
        return buffer

    @classmethod
    def from_double_array_to_bytes(self, target: List[float]) -> bytes:
        return bytes([DataType.DOUBLE_ARRAY.value]) + self.__from_double_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_double_array(self, target: bytes) -> List[float]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 8
            buffer.append(self.__from_bytes_to_double(target[c:c + 8]))
        return buffer

    @classmethod
    def from_bytes_to_double_array(self, target: bytes) -> List[float]:
        return self.__from_bytes_to_double_array(target[1:])

    @classmethod
    def __from_nullable_double_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_double_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_double_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_DOUBLE_ARRAY.value]) + self.__from_nullable_double_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_double_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 9
            buffer.append(self.__from_bytes_to_nullable_double(target[c:c + 9]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_double_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_double_array(target[1:])


    #string
    @staticmethod
    def __from_string_to_bytes(target: str) -> bytes:
        ba = target.encode("utf-8")
        buffer = int.to_bytes(len(ba), 4, 'little', signed=False) + ba
        return buffer

    @classmethod
    def from_string_to_bytes(self, target: str) -> bytes:
        return bytes([DataType.STRING.value]) + self.__from_string_to_bytes(target)

    @staticmethod
    def __from_bytes_to_string(target: bytes) -> str:
        length = int.from_bytes(target[:4], 'little', signed=False)
        return target[4:4 + length].decode("utf-8")

    @classmethod
    def from_bytes_to_string(self, target: bytes) -> str:
        return self.__from_bytes_to_string(target[1:])

    @classmethod
    def __from_string_array_to_bytes(self, target: List[str]) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            if data is None:
                buffer += bytes([0]) + int.to_bytes(0, 4, 'little', signed=False)
            else:
                buffer += bytes([1]) + self.__from_string_to_bytes(data)
        return buffer

    @classmethod
    def from_string_array_to_bytes(self, target: List[str]) -> bytes:
        return bytes([DataType.STRING_ARRAY.value]) + self.__from_string_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_string_array(self, target: bytes) -> List[str]:
        total_count = int.from_bytes(target[:4], 'little', signed=False)
        ret = []
        cursor = 4
        for _ in range(0, total_count):
            if target[cursor] == 0:
                ret.append(None)
                cursor += 5
            else:
                cursor += 1
                length = int.from_bytes(target[cursor:cursor + 4], 'little', signed=False)
                ret.append(self.__from_bytes_to_string(target[cursor:]))
                cursor += 4 + length
        return ret

    @classmethod
    def from_bytes_to_string_array(self, target: bytes) -> List[str]:
        return self.__from_bytes_to_string_array(target[1:])


    #datetime
    @staticmethod
    def from_datetime_to_int64(target: datetime) -> int:
        ordinal = target.toordinal()
        datetime_num = (ordinal - 1) * 10 * 1000 * 1000 * 60 * 60 * 24 + target.hour * 10 * 1000 * 1000 * 60 * 60 + target.minute * 10 * 1000 * 1000 * 60 + target.second * 10 * 1000 * 1000 + target.microsecond * 10
        return datetime_num | (1 << 62)

    @staticmethod
    def from_int64_to_datetime(target: int) -> datetime:
        datetime_num = target & 0x3FFFFFFFFFFFFFFF;
        time = datetime_num % (10 * 1000 * 1000 * 60 * 60 * 24)
        days = math.floor((datetime_num - time) / (10 * 1000 * 1000 * 60 * 60 * 24))
        hour = math.floor(time / (10 * 1000 * 1000 * 60 * 60))
        minute = math.floor((time - (hour * 10 * 1000 * 1000 * 60 * 60)) / (10 * 1000 * 1000 * 60))
        second = math.floor((time - (hour * 10 * 1000 * 1000 * 60 * 60) - (minute * 10 * 1000 * 1000 * 60)) / (10 * 1000 * 1000))
        microsecond = math.floor((time - (hour * 10 * 1000 * 1000 * 60 * 60) - (minute * 10 * 1000 * 1000 * 60) - (second * 10 * 1000 * 1000)) / 10)
        base_dt = datetime.fromordinal(days + 1)
        return datetime(base_dt.year, base_dt.month, base_dt.day, hour, minute, second, microsecond)

    @classmethod
    def __from_datetime_to_bytes(self, target: datetime) -> bytes:
        return self.__from_int64_to_bytes(self.from_datetime_to_int64(target))

    @classmethod
    def from_datetime_to_bytes(self, target: datetime) -> bytes:
        return bytes([DataType.DATE_TIME.value]) + self.__from_datetime_to_bytes(target)

    @classmethod
    def __from_bytes_to_datetime(self, target: bytes) -> datetime:
        return self.from_int64_to_datetime(self.__from_bytes_to_int64(target))

    @classmethod
    def from_bytes_to_datetime(self, target: bytes) -> datetime:
        return self.__from_bytes_to_datetime(target[1:])

    @classmethod
    def __from_nullable_datetime_to_bytes(self, target: any) -> bytes:
        return bytes([0]) + self.__from_int64_to_bytes(0) if target is None else bytes([1]) + self.__from_datetime_to_bytes(target)

    @classmethod
    def from_nullable_datetime_to_bytes(self, target: any) -> bytes:
        return bytes([DataType.NULLABLE_DATE_TIME.value]) + self.__from_nullable_datetime_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_datetime(self, target: bytes) -> any:
        return None if target[0] == 0 else self.__from_bytes_to_datetime(target[1:])

    @classmethod
    def from_bytes_to_nullable_datetime(self, target: bytes) -> any:
        return self.__from_bytes_to_nullable_datetime(target[1:])

    @classmethod
    def __from_datetime_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_datetime_to_bytes(data)
        return buffer

    @classmethod
    def from_datetime_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.DATE_TIME_ARRAY.value]) + self.__from_datetime_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_datetime_array(self, target: bytes) -> List[datetime]:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 8
            buffer.append(self.__from_bytes_to_datetime(target[c:c + 8]))
        return buffer

    @classmethod
    def from_bytes_to_datetime_array(self, target: bytes) -> List[datetime]:
        return self.__from_bytes_to_datetime_array(target[1:])

    @classmethod
    def __from_nullable_datetime_array_to_bytes(self, target: list) -> bytes:
        buffer = int.to_bytes(len(target), 4, 'little', signed=False)
        for data in target:
            buffer += self.__from_nullable_datetime_to_bytes(data)
        return buffer

    @classmethod
    def from_nullable_datetime_array_to_bytes(self, target: list) -> bytes:
        return bytes([DataType.NULLABLE_DATE_TIME_ARRAY.value]) + self.__from_nullable_datetime_array_to_bytes(target)

    @classmethod
    def __from_bytes_to_nullable_datetime_array(self, target: bytes) -> list:
        length = int.from_bytes(target[:4], 'little', signed=False)
        buffer = []
        for index in range(length):
            c = 4 + index * 9
            buffer.append(self.__from_bytes_to_nullable_datetime(target[c:c + 9]))
        return buffer

    @classmethod
    def from_bytes_to_nullable_datetime_array(self, target: bytes) -> list:
        return self.__from_bytes_to_nullable_datetime_array(target[1:])


    #object
    @classmethod
    def from_object_to_bytes(self, target: any) -> bytes:
        if type(target) is list:
            buffer = bytes([DataType.OBJECT_ARRAY.value]) + int.to_bytes(len(target), 4, 'little', signed=False)
            for data in target:
                if type(data) is list:
                    buffer += self.from_object_to_bytes(data)
                else:
                    buffer += self.from_orin3_value_to_bytes(data)
            return buffer
        elif type(target) is dict:
            return self.from_dict_to_bytes(target)
        elif type(target) is ORiN3Value:
            return self.from_orin3_value_to_bytes(target)
        else:
            return self.from_string_to_bytes(str(target))

    @classmethod
    def __from_dict_to_bytes(self, target: dict) -> bytes:
        buffer = bytes([DataType.DICTIONARY.value])
        temp_buffer = self.from_dict_to_bytes(target)
        buffer += int.to_bytes(len(temp_buffer), 4, 'little', signed=False)
        buffer += temp_buffer
        return buffer

    @classmethod
    def from_dict_to_bytes(self, target: dict) -> bytes:
        key_count = len(target)
        temp_buffer = int.to_bytes(key_count, 4, 'little', signed=False)
        for key in target.keys():
            value = target[key]
            key_bytes = self.from_string_to_bytes(key)
            if type(value) is list:
                value_bytes = self.from_object_to_bytes(value)
            else:
                assert type(value) is ORiN3Value
                value_bytes = self.from_orin3_value_to_bytes(value)
            temp_buffer += key_bytes + value_bytes
        return temp_buffer

    @classmethod
    def from_orin3_value_to_bytes(self, target: ORiN3Value) -> bytes:
        value = target.value
        value_type = target.value_type
        if value is None:
            return self.from_none_to_bytes()
        elif type(value) is dict:
            return self.__from_dict_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_BOOL:
            return self.from_bool_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_BOOL_ARRAY:
            return self.from_bool_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_BOOL:
            return self.from_bool_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_BOOL_ARRAY:
            return self.from_nullable_bool_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT8:
            return self.from_uint8_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT8_ARRAY:
            return self.from_uint8_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT8:
            return self.from_uint8_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT8_ARRAY:
            return self.from_nullable_uint8_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT8:
            return self.from_int8_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT8_ARRAY:
            return self.from_int8_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT8:
            return self.from_int8_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT8_ARRAY:
            return self.from_nullable_int8_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT16:
            return self.from_uint16_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT16_ARRAY:
            return self.from_uint16_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT16:
            return self.from_uint16_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT16_ARRAY:
            return self.from_nullable_uint16_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT16:
            return self.from_int16_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT16_ARRAY:
            return self.from_int16_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT16:
            return self.from_int16_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT16_ARRAY:
            return self.from_nullable_int16_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT32:
            return self.from_uint32_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT32_ARRAY:
            return self.from_uint32_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT32:
            return self.from_uint32_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT32_ARRAY:
            return self.from_nullable_uint32_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT32:
            return self.from_int32_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT32_ARRAY:
            return self.from_int32_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT32:
            return self.from_int32_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT32_ARRAY:
            return self.from_nullable_int32_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT64:
            return self.from_uint64_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_UINT64_ARRAY:
            return self.from_uint64_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT64:
            return self.from_uint64_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT64_ARRAY:
            return self.from_nullable_uint64_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT64:
            return self.from_int64_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_INT64_ARRAY:
            return self.from_int64_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT64:
            return self.from_int64_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_INT64_ARRAY:
            return self.from_nullable_int64_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_FLOAT:
            return self.from_float_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_FLOAT_ARRAY:
            return self.from_float_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT:
            return self.from_float_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT_ARRAY:
            return self.from_nullable_float_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_DOUBLE:
            return self.from_double_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_DOUBLE_ARRAY:
            return self.from_double_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE:
            return self.from_double_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE_ARRAY:
            return self.from_nullable_double_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_STRING:
            return self.from_string_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_STRING_ARRAY:
            return self.from_string_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_DATE_TIME:
            return self.from_datetime_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_DATE_TIME_ARRAY:
            return self.from_datetime_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME:
            return self.from_datetime_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME_ARRAY:
            return self.from_nullable_datetime_array_to_bytes(value)
        elif value_type == ORiN3ValueType.ORIN3_OBJECT:
            return self.from_object_to_bytes(value)
        else:
            raise TypeError(f"not supported type: {value_type}")

    @classmethod
    def from_bytes_to_dict(self, target: bytes) -> dict:
        count = int.from_bytes(target[0:4], 'little', signed=False)
        target = target[4:]
        result = {}
        for i in range(count):
            to_object_result = self.__to_object(target)
            key = to_object_result.get_result()
            target = to_object_result.get_bytes()
            to_object_result = self.__to_object(target)
            value = to_object_result.get_result()
            target = to_object_result.get_bytes()
            if key is None:
                raise TypeError()
            elif type(key) is not str:
                raise TypeError()
            result[key] = value
        return result

    @classmethod
    def from_bytes_to_object_array(self, target: bytes) -> list:
        length = int.from_bytes(target[1:5], 'little', signed=False)
        ret = []
        rest = target[5:]
        for _ in range(length):
            result = self.__to_object(rest)
            rest = result.get_bytes()
            ret.append(result.get_result())
        return ret

    @classmethod
    def __to_object(self, target: bytes) -> _ToObjectResult:
        data_type = target[0]
        if data_type == DataType.NULL.value:
            return _ToObjectResult(target[1:], None)
        elif data_type == DataType.OBJECT_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            temp = []
            rest = target[5:]
            for _ in range(length):
                result = self.__to_object(rest)
                rest = result.get_bytes()
                temp.append(result.get_result())
            return _ToObjectResult(rest, temp)
        elif data_type == DataType.BOOL.value:
            return _ToObjectResult(target[2:], self.from_bytes_to_bool(target))
        elif data_type == DataType.BOOL_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length + 5:], self.from_bytes_to_bool_array(target))
        elif data_type == DataType.NULLABLE_BOOL_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length + 5:], self.from_bytes_to_nullable_bool_array(target))
        elif data_type == DataType.UINT8.value:
            return _ToObjectResult(target[2:], self.from_bytes_to_uint8(target))
        elif data_type == DataType.UINT8_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length + 5:], self.from_bytes_to_uint8_array(target))
        elif data_type == DataType.NULLABLE_UINT8_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 2 + 5:], self.from_bytes_to_nullable_uint8_array(target))
        elif data_type == DataType.INT8.value:
            return _ToObjectResult(target[2:], self.from_bytes_to_int8(target))
        elif data_type == DataType.INT8_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length + 5:], self.from_bytes_to_int8_array(target))
        elif data_type == DataType.NULLABLE_INT8_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 2 + 5:], self.from_bytes_to_nullable_int8_array(target))
        elif data_type == DataType.UINT16.value:
            return _ToObjectResult(target[3:], self.from_bytes_to_uint16(target))
        elif data_type == DataType.UINT16_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 2 + 5:], self.from_bytes_to_uint16_array(target))
        elif data_type == DataType.NULLABLE_UINT16_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 3 + 5:], self.from_bytes_to_nullable_uint16_array(target))
        elif data_type == DataType.INT16.value:
            return _ToObjectResult(target[3:], self.from_bytes_to_int16(target))
        elif data_type == DataType.INT16_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 2 + 5:], self.from_bytes_to_int16_array(target))
        elif data_type == DataType.NULLABLE_INT16_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 3 + 5:], self.from_bytes_to_nullable_int16_array(target))
        elif data_type == DataType.UINT32.value:
            return _ToObjectResult(target[5:], self.from_bytes_to_uint32(target))
        elif data_type == DataType.UINT32_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 4 + 5:], self.from_bytes_to_uint32_array(target))
        elif data_type == DataType.NULLABLE_UINT32_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 5 + 5:], self.from_bytes_to_nullable_uint32_array(target))
        elif data_type == DataType.INT32.value:
            return _ToObjectResult(target[5:], self.from_bytes_to_int32(target))
        elif data_type == DataType.INT32_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 4 + 5:], self.from_bytes_to_int32_array(target))
        elif data_type == DataType.NULLABLE_INT32_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 5 + 5:], self.from_bytes_to_nullable_int32_array(target))
        elif data_type == DataType.UINT64.value:
            return _ToObjectResult(target[9:], self.from_bytes_to_uint64(target))
        elif data_type == DataType.UINT64_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 8 + 5:], self.from_bytes_to_uint64_array(target))
        elif data_type == DataType.NULLABLE_UINT64_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 9 + 5:], self.from_bytes_to_nullable_uint64_array(target))
        elif data_type == DataType.INT64.value:
            return _ToObjectResult(target[9:], self.from_bytes_to_int64(target))
        elif data_type == DataType.INT64_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 8 + 5:], self.from_bytes_to_int64_array(target))
        elif data_type == DataType.NULLABLE_INT64_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 9 + 5:], self.from_bytes_to_nullable_int64_array(target))
        elif data_type == DataType.FLOAT.value:
            return _ToObjectResult(target[5:], self.from_bytes_to_float(target))
        elif data_type == DataType.FLOAT_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 4 + 5:], self.from_bytes_to_float_array(target))
        elif data_type == DataType.NULLABLE_FLOAT_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 5 + 5:], self.from_bytes_to_nullable_float_array(target))
        elif data_type == DataType.DOUBLE.value:
            return _ToObjectResult(target[9:], self.from_bytes_to_double(target))
        elif data_type == DataType.DOUBLE_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 8 + 5:], self.from_bytes_to_double_array(target))
        elif data_type == DataType.NULLABLE_DOUBLE_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 9 + 5:], self.from_bytes_to_nullable_double_array(target))
        elif data_type == DataType.STRING.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[5 + length:], self.from_bytes_to_string(target))
        elif data_type == DataType.STRING_ARRAY.value:
            count = int.from_bytes(target[1:5], 'little', signed=False)
            target = target[5:]
            temp = []
            for i in range(count):
                if target[0] == 1:
                    length = int.from_bytes(target[1:5], 'little', signed=False)
                    result = bytes.decode(target[5:5 + length], 'utf-8')
                    temp.append(result)
                    target = target[5 + length:]
                else:
                    temp.append(None)
                    target = target[5:]
            return _ToObjectResult(target, temp)
        elif data_type == DataType.DATE_TIME.value:
            return _ToObjectResult(target[9:], self.from_bytes_to_datetime(target))
        elif data_type == DataType.DATE_TIME_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 8 + 5:], self.from_bytes_to_datetime_array(target))
        elif data_type == DataType.NULLABLE_DATE_TIME_ARRAY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            return _ToObjectResult(target[length * 9 + 5:], self.from_bytes_to_nullable_datetime_array(target))
        elif data_type == DataType.DICTIONARY.value:
            length = int.from_bytes(target[1:5], 'little', signed=False)
            result = self.from_bytes_to_dict(target[5:])
            return _ToObjectResult(target[5 + length:], result)
        else:
            raise TypeError(f"not supported type: {data_type}")

    @classmethod
    def from_bytes_to_object(self, target: bytes):
        data_type = target[0]
        if (data_type == DataType.NULL.value):
            return FromBytesToObjectResult(data_type, None)
        elif (data_type == DataType.BOOL.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_bool(target))
        elif (data_type == DataType.NULLABLE_BOOL.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_bool(target))
        elif (data_type == DataType.BOOL_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_bool_array(target))
        elif (data_type == DataType.NULLABLE_BOOL_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_bool_array(target))
        elif (data_type == DataType.UINT8.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint8(target))
        elif (data_type == DataType.NULLABLE_UINT8.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint8(target))
        elif (data_type == DataType.UINT8_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint8_array(target))
        elif (data_type == DataType.NULLABLE_UINT8_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint8_array(target))
        elif (data_type == DataType.INT8.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int8(target))
        elif (data_type == DataType.NULLABLE_INT8.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int8(target))
        elif (data_type == DataType.INT8_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int8_array(target))
        elif (data_type == DataType.NULLABLE_INT8_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int8_array(target))
        elif (data_type == DataType.UINT16.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint16(target))
        elif (data_type == DataType.NULLABLE_UINT16.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint16(target))
        elif (data_type == DataType.UINT16_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint16_array(target))
        elif (data_type == DataType.NULLABLE_UINT16_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint16_array(target))
        elif (data_type == DataType.INT16.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int16(target))
        elif (data_type == DataType.NULLABLE_INT16.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int16(target))
        elif (data_type == DataType.INT16_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int16_array(target))
        elif (data_type == DataType.NULLABLE_INT16_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int16_array(target))
        elif (data_type == DataType.UINT32.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint32(target))
        elif (data_type == DataType.NULLABLE_UINT32.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint32(target))
        elif (data_type == DataType.UINT32_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint32_array(target))
        elif (data_type == DataType.NULLABLE_UINT32_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint32_array(target))
        elif (data_type == DataType.INT32.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int32(target))
        elif (data_type == DataType.NULLABLE_INT32.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int32(target))
        elif (data_type == DataType.INT32_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int32_array(target))
        elif (data_type == DataType.NULLABLE_INT32_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int32_array(target))
        elif (data_type == DataType.UINT64.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint64(target))
        elif (data_type == DataType.NULLABLE_UINT64.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint64(target))
        elif (data_type == DataType.UINT64_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_uint64_array(target))
        elif (data_type == DataType.NULLABLE_UINT64_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_uint64_array(target))
        elif (data_type == DataType.INT64.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int64(target))
        elif (data_type == DataType.NULLABLE_INT64.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int64(target))
        elif (data_type == DataType.INT64_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_int64_array(target))
        elif (data_type == DataType.NULLABLE_INT64_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_int64_array(target))
        elif (data_type == DataType.FLOAT.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_float(target))
        elif (data_type == DataType.NULLABLE_FLOAT.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_float(target))
        elif (data_type == DataType.FLOAT_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_float_array(target))
        elif (data_type == DataType.NULLABLE_FLOAT_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_float_array(target))
        elif (data_type == DataType.DOUBLE.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_double(target))
        elif (data_type == DataType.NULLABLE_DOUBLE.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_double(target))
        elif (data_type == DataType.DOUBLE_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_double_array(target))
        elif (data_type == DataType.NULLABLE_DOUBLE_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_double_array(target))
        elif (data_type == DataType.STRING.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_string(target))
        elif (data_type == DataType.STRING_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_string_array(target))
        elif (data_type == DataType.DATE_TIME.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_datetime(target))
        elif (data_type == DataType.NULLABLE_DATE_TIME.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_datetime(target))
        elif (data_type == DataType.DATE_TIME_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_datetime_array(target))
        elif (data_type == DataType.NULLABLE_DATE_TIME_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_nullable_datetime_array(target))
        elif (data_type == DataType.DICTIONARY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_dict(target[5:]))
        elif (data_type == DataType.OBJECT_ARRAY.value):
            return FromBytesToObjectResult(data_type, self.from_bytes_to_object_array(target))
        else:
            raise TypeError(f"not supported type: {data_type}")
