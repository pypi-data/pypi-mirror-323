from enum import IntEnum

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonResponse


class CommonResponse:
    def __init__(self, src: CommonResponse | None):
        if src == None:
            self.__result_code = 0
            self.__detail = bytearray()
        else:
            self.__result_code = src.resultCode
            self.__detail = src.detail
    
    @property
    def result_code(self) -> int:
        return self.__result_code
    
    @property
    def detail(self) -> str:
        return self.__detail


class ORiN3ObjectType(IntEnum):
    PROVIDER_ROOT = 0
    CONTROLLER = 1
    MODULE = 2
    VARIABLE = 3
    FILE = 4
    STREAM = 5
    EVENT = 6
    JOB = 7


class ORiN3MessageFileSeekOrigin(IntEnum):
    BEGIN = 0
    CURRENT = 1
    END = 2


class ORiN3ValueType(IntEnum):
    ORIN3_BOOL = 10
    ORIN3_BOOL_ARRAY = 11
    ORIN3_NULLABLE_BOOL = 12
    ORIN3_NULLABLE_BOOL_ARRAY = 13
    ORIN3_INT8 = 20
    ORIN3_INT8_ARRAY = 21
    ORIN3_NULLABLE_INT8 = 22
    ORIN3_NULLABLE_INT8_ARRAY = 23
    ORIN3_INT16 = 30
    ORIN3_INT16_ARRAY = 31
    ORIN3_NULLABLE_INT16 = 32
    ORIN3_NULLABLE_INT16_ARRAY = 33
    ORIN3_INT32 = 40
    ORIN3_INT32_ARRAY = 41
    ORIN3_NULLABLE_INT32 = 42
    ORIN3_NULLABLE_INT32_ARRAY = 43
    ORIN3_INT64 = 50
    ORIN3_INT64_ARRAY = 51
    ORIN3_NULLABLE_INT64 = 52
    ORIN3_NULLABLE_INT64_ARRAY = 53
    ORIN3_UINT8 = 60
    ORIN3_UINT8_ARRAY = 61
    ORIN3_NULLABLE_UINT8 = 62
    ORIN3_NULLABLE_UINT8_ARRAY = 63
    ORIN3_UINT16 = 70
    ORIN3_UINT16_ARRAY = 71
    ORIN3_NULLABLE_UINT16 = 72
    ORIN3_NULLABLE_UINT16_ARRAY = 73
    ORIN3_UINT32 = 80
    ORIN3_UINT32_ARRAY = 81
    ORIN3_NULLABLE_UINT32 = 82
    ORIN3_NULLABLE_UINT32_ARRAY = 83
    ORIN3_UINT64 = 90
    ORIN3_UINT64_ARRAY = 91
    ORIN3_NULLABLE_UINT64 = 92
    ORIN3_NULLABLE_UINT64_ARRAY = 93
    ORIN3_FLOAT = 100
    ORIN3_FLOAT_ARRAY = 101
    ORIN3_NULLABLE_FLOAT = 102
    ORIN3_NULLABLE_FLOAT_ARRAY = 103
    ORIN3_DOUBLE = 110
    ORIN3_DOUBLE_ARRAY = 111
    ORIN3_NULLABLE_DOUBLE = 112
    ORIN3_NULLABLE_DOUBLE_ARRAY = 113
    ORIN3_STRING = 120
    ORIN3_STRING_ARRAY = 121
    ORIN3_DATE_TIME = 130
    ORIN3_DATE_TIME_ARRAY = 131
    ORIN3_NULLABLE_DATE_TIME = 132
    ORIN3_NULLABLE_DATE_TIME_ARRAY = 133
    ORIN3_OBJECT = 140


class ORiN3Value():
    def __init__(self, value: any, value_type: ORiN3ValueType):
        if value is None:
            assert value_type == ORiN3ValueType.ORIN3_NULLABLE_BOOL or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT8 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT8 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT16 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT16 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT32 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT32 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT64 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT64 or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE or \
                value_type == ORiN3ValueType.ORIN3_STRING or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME or \
                value_type == ORiN3ValueType.ORIN3_OBJECT, 'Invalid value type.'
        if type(value) is list:
            assert value_type == ORiN3ValueType.ORIN3_BOOL_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_BOOL_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_UINT8_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT8_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_INT8_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT8_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_UINT16_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT16_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_INT16_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT16_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_UINT32_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT32_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_INT32_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT32_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_UINT64_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_UINT64_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_INT64_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_INT64_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_FLOAT_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_DOUBLE_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_STRING_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_DATE_TIME_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME_ARRAY or \
                value_type == ORiN3ValueType.ORIN3_OBJECT, 'Invalid value type.'

        self.__value = value
        self.__value_type = value_type
    
    @property
    def value(self) -> any:
        return self.__value
    
    @property
    def value_type(self) -> ORiN3ValueType:
        return self.__value_type

class DataType(IntEnum):
    NULL = 0
    OBJECT_ARRAY = 1
    BOOL = 2
    BOOL_ARRAY = 3
    NULLABLE_BOOL = 4
    NULLABLE_BOOL_ARRAY = 5
    UINT8 = 6
    UINT8_ARRAY = 7
    NULLABLE_UINT8 = 8
    NULLABLE_UINT8_ARRAY = 9
    UINT16 = 10
    UINT16_ARRAY = 11
    NULLABLE_UINT16 = 12
    NULLABLE_UINT16_ARRAY = 13
    UINT32 = 14
    UINT32_ARRAY = 15
    NULLABLE_UINT32 = 16
    NULLABLE_UINT32_ARRAY = 17
    UINT64 = 18
    UINT64_ARRAY = 19
    NULLABLE_UINT64 = 20
    NULLABLE_UINT64_ARRAY = 21
    INT8 = 22
    INT8_ARRAY = 23
    NULLABLE_INT8 = 24
    NULLABLE_INT8_ARRAY = 25
    INT16 = 26
    INT16_ARRAY = 27
    NULLABLE_INT16 = 28
    NULLABLE_INT16_ARRAY = 29
    INT32 = 30
    INT32_ARRAY = 31
    NULLABLE_INT32 = 32
    NULLABLE_INT32_ARRAY = 33
    INT64 = 34
    INT64_ARRAY = 35
    NULLABLE_INT64 = 36
    NULLABLE_INT64_ARRAY = 37
    FLOAT = 38
    FLOAT_ARRAY = 39
    NULLABLE_FLOAT = 40
    NULLABLE_FLOAT_ARRAY = 41
    DOUBLE = 42
    DOUBLE_ARRAY = 43
    NULLABLE_DOUBLE = 44
    NULLABLE_DOUBLE_ARRAY = 45
    STRING = 46
    STRING_ARRAY = 47
    DATE_TIME = 48
    DATE_TIME_ARRAY = 49
    NULLABLE_DATE_TIME = 50
    NULLABLE_DATE_TIME_ARRAY = 51
    DICTIONARY = 52
