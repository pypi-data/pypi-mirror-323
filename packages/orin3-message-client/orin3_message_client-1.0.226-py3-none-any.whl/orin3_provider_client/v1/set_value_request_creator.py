from orin3_grpc.message.orin3.provider.v1 import orin3_common_type_pb2

from orin3_provider_client.v1.binary_converter import BinaryConverter
from orin3_provider_client.v1.common import ORiN3ValueType


def create_orin3value(value: any, type: ORiN3ValueType) -> orin3_common_type_pb2.ORiN3Value:
    is_null_value = value is None
    if type == ORiN3ValueType.ORIN3_BOOL:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, bool=orin3_common_type_pb2.ORiN3Bool(raw_value=value))
    if type == ORiN3ValueType.ORIN3_BOOL_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, bool_array=orin3_common_type_pb2.ORiN3BoolArray(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_BOOL:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_bool=orin3_common_type_pb2.ORiN3NullableBool(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_BOOL_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_bool_array=orin3_common_type_pb2.ORiN3NullableBoolArray(raw_value=[orin3_common_type_pb2.ORiN3NullableBool(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_INT8:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int8=orin3_common_type_pb2.ORiN3Int8(raw_value=value))
    if type == ORiN3ValueType.ORIN3_INT8_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int8_array=orin3_common_type_pb2.ORiN3Int8Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT8:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int8=orin3_common_type_pb2.ORiN3NullableInt8(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT8_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int8_array=orin3_common_type_pb2.ORiN3NullableInt8Array(raw_value=[orin3_common_type_pb2.ORiN3NullableInt8(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_INT16:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int16=orin3_common_type_pb2.ORiN3Int16(raw_value=value))
    if type == ORiN3ValueType.ORIN3_INT16_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int16_array=orin3_common_type_pb2.ORiN3Int16Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT16:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int16=orin3_common_type_pb2.ORiN3NullableInt16(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT16_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int16_array=orin3_common_type_pb2.ORiN3NullableInt16Array(raw_value=[orin3_common_type_pb2.ORiN3NullableInt16(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_INT32:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int32=orin3_common_type_pb2.ORiN3Int32(raw_value=value))
    if type == ORiN3ValueType.ORIN3_INT32_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int32_array=orin3_common_type_pb2.ORiN3Int32Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT32:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int32=orin3_common_type_pb2.ORiN3NullableInt32(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT32_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int32_array=orin3_common_type_pb2.ORiN3NullableInt32Array(raw_value=[orin3_common_type_pb2.ORiN3NullableInt32(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_INT64:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int64=orin3_common_type_pb2.ORiN3Int64(raw_value=value))
    if type == ORiN3ValueType.ORIN3_INT64_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, int64_array=orin3_common_type_pb2.ORiN3Int64Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT64:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int64=orin3_common_type_pb2.ORiN3NullableInt64(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_INT64_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_int64_array=orin3_common_type_pb2.ORiN3NullableInt64Array(raw_value=[orin3_common_type_pb2.ORiN3NullableInt64(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_UINT8:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint8=orin3_common_type_pb2.ORiN3UInt8(raw_value=value))
    if type == ORiN3ValueType.ORIN3_UINT8_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint8_array=orin3_common_type_pb2.ORiN3UInt8Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT8:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint8=orin3_common_type_pb2.ORiN3NullableUInt8(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT8_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint8_array=orin3_common_type_pb2.ORiN3NullableUInt8Array(raw_value=[orin3_common_type_pb2.ORiN3NullableUInt8(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_UINT16:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint16=orin3_common_type_pb2.ORiN3UInt16(raw_value=value))
    if type == ORiN3ValueType.ORIN3_UINT16_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint16_array=orin3_common_type_pb2.ORiN3UInt16Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT16:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint16=orin3_common_type_pb2.ORiN3NullableUInt16(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT16_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint16_array=orin3_common_type_pb2.ORiN3NullableUInt16Array(raw_value=[orin3_common_type_pb2.ORiN3NullableUInt16(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_UINT32:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint32=orin3_common_type_pb2.ORiN3UInt32(raw_value=value))
    if type == ORiN3ValueType.ORIN3_UINT32_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint32_array=orin3_common_type_pb2.ORiN3UInt32Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT32:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint32=orin3_common_type_pb2.ORiN3NullableUInt32(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT32_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint32_array=orin3_common_type_pb2.ORiN3NullableUInt32Array(raw_value=[orin3_common_type_pb2.ORiN3NullableUInt32(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_UINT64:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint64=orin3_common_type_pb2.ORiN3UInt64(raw_value=value))
    if type == ORiN3ValueType.ORIN3_UINT64_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, uint64_array=orin3_common_type_pb2.ORiN3UInt64Array(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT64:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint64=orin3_common_type_pb2.ORiN3NullableUInt64(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_UINT64_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_uint64_array=orin3_common_type_pb2.ORiN3NullableUInt64Array(raw_value=[orin3_common_type_pb2.ORiN3NullableUInt64(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_FLOAT:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, float=orin3_common_type_pb2.ORiN3Float(raw_value=value))
    if type == ORiN3ValueType.ORIN3_FLOAT_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, float_array=orin3_common_type_pb2.ORiN3FloatArray(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_float=orin3_common_type_pb2.ORiN3NullableFloat(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_FLOAT_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_float_array=orin3_common_type_pb2.ORiN3NullableFloatArray(raw_value=[orin3_common_type_pb2.ORiN3NullableFloat(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_DOUBLE:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, double=orin3_common_type_pb2.ORiN3Double(raw_value=value))
    if type == ORiN3ValueType.ORIN3_DOUBLE_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, double_array=orin3_common_type_pb2.ORiN3DoubleArray(raw_value=value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_double=orin3_common_type_pb2.ORiN3NullableDouble(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_DOUBLE_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_double_array=orin3_common_type_pb2.ORiN3NullableDoubleArray(raw_value=[orin3_common_type_pb2.ORiN3NullableDouble(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_STRING:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, string=orin3_common_type_pb2.ORiN3String(raw_value=value, is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_STRING_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, string_array=orin3_common_type_pb2.ORiN3StringArray(raw_value=[orin3_common_type_pb2.ORiN3String(raw_value=item, is_null=item is None) for item in value]))
    if type == ORiN3ValueType.ORIN3_DATE_TIME:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, datetime=orin3_common_type_pb2.ORiN3DateTime(raw_value=BinaryConverter.from_datetime_to_int64(value)))
    if type == ORiN3ValueType.ORIN3_DATE_TIME_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, datetime_array=orin3_common_type_pb2.ORiN3DateTimeArray(raw_value=[BinaryConverter.from_datetime_to_int64(it) for it in value]))
    if type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_datetime=orin3_common_type_pb2.ORiN3NullableDateTime(raw_value=0 if is_null_value else BinaryConverter.from_datetime_to_int64(value), is_null=is_null_value))
    if type == ORiN3ValueType.ORIN3_NULLABLE_DATE_TIME_ARRAY:
        return orin3_common_type_pb2.ORiN3Value(type=type.value, nullable_datetime_array=orin3_common_type_pb2.ORiN3NullableDateTimeArray(raw_value=[orin3_common_type_pb2.ORiN3NullableDateTime(raw_value=0 if item is None else BinaryConverter.from_datetime_to_int64(item), is_null=item is None) for item in value]))
