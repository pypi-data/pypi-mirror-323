from orin3_grpc.message.orin3.provider.v1 import orin3_common_type_pb2

from orin3_provider_client.v1.binary_converter import BinaryConverter
from orin3_provider_client.v1.common import ORiN3ValueType


def get_value(value: orin3_common_type_pb2.ORiN3Value) -> any:
    type = ORiN3ValueType(value.type)
    if type == ORiN3ValueType.ORIN3_BOOL:
        return value.bool.raw_value
    if type == ORiN3ValueType.ORIN3_BOOL_ARRAY:
        return value.bool_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_BOOL:
        return None if value.nullable_bool.is_null else value.nullable_bool.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_BOOL_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_bool_array.raw_value]
    if type == ORiN3ValueType.ORIN3_INT8:
        return value.int8.raw_value
    if type == ORiN3ValueType.ORIN3_INT8_ARRAY:
        return value.int8_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT8:
        return None if value.nullable_int8.is_null else value.nullable_int8.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT8_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_int8_array.raw_value]
    if type == ORiN3ValueType.ORIN3_INT16:
        return value.int16.raw_value
    if type == ORiN3ValueType.ORIN3_INT16_ARRAY:
        return value.int16_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT16:
        return None if value.nullable_int16.is_null else value.nullable_int16.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT16_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_int16_array.raw_value]
    if type == ORiN3ValueType.ORIN3_INT32:
        return value.int32.raw_value
    if type == ORiN3ValueType.ORIN3_INT32_ARRAY:
        return value.int32_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT32:
        return None if value.nullable_int32.is_null else value.nullable_int32.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT32_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_int32_array.raw_value]
    if type == ORiN3ValueType.ORIN3_INT64:
        return value.int64.raw_value
    if type == ORiN3ValueType.ORIN3_INT64_ARRAY:
        return value.int64_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT64:
        return None if value.nullable_int64.is_null else value.nullable_int64.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT64_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_int64_array.raw_value]
    if type == ORiN3ValueType.ORIN3_UINT8:
        return value.uint8.raw_value
    if type == ORiN3ValueType.ORIN3_UINT8_ARRAY:
        return value.uint8_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT8:
        return None if value.nullable_uint8.is_null else value.nullable_uint8.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT8_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_uint8_array.raw_value]
    if type == ORiN3ValueType.ORIN3_UINT16:
        return value.uint16.raw_value
    if type == ORiN3ValueType.ORIN3_UINT16_ARRAY:
        return value.uint16_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT16:
        return None if value.nullable_uint16.is_null else value.nullable_uint16.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT16_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_uint16_array.raw_value]
    if type == ORiN3ValueType.ORIN3_UINT32:
        return value.uint32.raw_value
    if type == ORiN3ValueType.ORIN3_UINT32_ARRAY:
        return value.uint32_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT32:
        return None if value.nullable_uint32.is_null else value.nullable_uint32.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT32_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_uint32_array.raw_value]
    if type == ORiN3ValueType.ORIN3_UINT64:
        return value.uint64.raw_value
    if type == ORiN3ValueType.ORIN3_UINT64_ARRAY:
        return value.uint64_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT64:
        return None if value.nullable_uint64.is_null else value.nullable_uint64.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT64_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_uint64_array.raw_value]
    if type == ORiN3ValueType.ORIN3_FLOAT:
        return value.float.raw_value
    if type == ORiN3ValueType.ORIN3_FLOAT_ARRAY:
        return value.float_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT:
        return None if value.nullable_float.is_null else value.nullable_float.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_float_array.raw_value]
    if type == ORiN3ValueType.ORIN3_DOUBLE:
        return value.double.raw_value
    if type == ORiN3ValueType.ORIN3_DOUBLE_ARRAY:
        return value.double_array.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE:
        return None if value.nullable_double.is_null else value.nullable_double.raw_value
    if type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.nullable_double_array.raw_value]
    if type == ORiN3ValueType.ORIN3_STRING:
        return None if value.string.is_null else value.string.raw_value
    if type == ORiN3ValueType.ORIN3_STRING_ARRAY:
        return [None if item.is_null else item.raw_value for item in value.string_array.raw_value]
    if type == ORiN3ValueType.ORIN3_DATE_TIME:
        return BinaryConverter.from_int64_to_datetime(value.datetime.raw_value)
    if type == ORiN3ValueType.ORIN3_DATE_TIME_ARRAY:
        return [BinaryConverter.from_int64_to_datetime(it) for it in value.datetime_array.raw_value]
    if type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME:
        return None if value.nullable_datetime.is_null else BinaryConverter.from_int64_to_datetime(value.nullable_datetime.raw_value)
    if type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME_ARRAY:
        return [None if item.is_null else BinaryConverter.from_int64_to_datetime(item.raw_value) for item in value.nullable_datetime_array.raw_value]
