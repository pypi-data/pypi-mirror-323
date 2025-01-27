import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_child_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_child_pb2_grpc

from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.common import ORiN3ObjectType
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class ModuleClient(ParentClient):
    __parent: ParentClient

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: any, timeout_interval_milliseconds: int):
        super().__init__(channel, name, ORiN3ObjectType.MODULE, id, option, created_date_time, timeout_interval_milliseconds)
        self.__parent = parent
    
    @property
    def parent(self) -> ParentClient:
        return self.__parent
    
    async def __delete_async(self) -> orin3_child_pb2.DeleteResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_pb2.DeleteRequest(common=common, id=self.id)
        stub = orin3_child_pb2_grpc.ChildServiceStub(self.channel)
        return await stub.Delete(request)

    async def delete_async(self) -> None:
        try:
            delete_result = await self.__delete_async()
            validate_response(delete_result)
        except Exception as err:
            raise ProviderClientError() from err
