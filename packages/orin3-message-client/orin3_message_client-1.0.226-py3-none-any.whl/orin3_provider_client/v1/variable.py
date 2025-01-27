import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_variable_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_variable_pb2_grpc

from orin3_provider_client.v1 import set_value_request_creator
from orin3_provider_client.v1.client_base import ChildClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.common import ORiN3ObjectType
from orin3_provider_client.v1.common import ORiN3ValueType
from orin3_provider_client.v1.get_value_branch import get_value
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class VariableClient(ChildClient):
    __value_type: ORiN3ValueType

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: any, value_type: ORiN3ValueType,timeout_interval_milliseconds: int):
        super().__init__(channel, parent, name, ORiN3ObjectType.VARIABLE, id, option, created_date_time, timeout_interval_milliseconds)
        self.__value_type = value_type

    async def __get_value_async(self, value_type: int) -> orin3_variable_pb2.GetValueResponse:
        common = CommonRequest(reserved=0)
        request = orin3_variable_pb2.GetValueRequest(common=common, id=self._id, value_type=value_type)
        stub = orin3_variable_pb2_grpc.VariableServiceStub(self.channel)
        return await stub.GetValue(request)

    async def get_value_async(self) -> any:
        try:
            get_value_result = await self.__get_value_async(self.__value_type.value)
            validate_response(get_value_result)
            return get_value(get_value_result.value)
        except Exception as err:
            raise ProviderClientError() from err

    async def __set_value_async(self, value: any, type: ORiN3ValueType):
        common = CommonRequest(reserved=0)
        request = orin3_variable_pb2.SetValueRequest(common=common, id=self._id, value=set_value_request_creator.create_orin3value(value, type))
        stub = orin3_variable_pb2_grpc.VariableServiceStub(self.channel)
        return await stub.SetValue(request)

    async def set_value_async(self, value: any) -> None:
        try:
            set_value_result = await self.__set_value_async(value, self.__value_type)
            validate_response(set_value_result)
        except Exception as err:
            raise ProviderClientError() from err

    def get_value_type(self) -> ORiN3ValueType:
        return self.__value_type
