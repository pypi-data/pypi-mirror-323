from typing import Dict, List
import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_stream_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_stream_pb2_grpc

from orin3_provider_client.v1.client_base import ChildClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.client_base import ResourceOpenerClient
from orin3_provider_client.v1.common import ORiN3ObjectType, ORiN3Value
from orin3_provider_client.v1.error import ProviderClientError


class StreamReader:
    def __init__(self, call: grpc.aio._call.UnaryStreamCall):
        self.__call = call
    
    async def read_async(self) -> bytes:
        try:
            response = await self.__call.read()
            if (response == grpc.aio.EOF):
                return bytearray()
            return response.value
        except Exception as err:
            raise ProviderClientError() from err
    
    def cancel(self) -> None:
        self.__call.cancel()


class StreamClient(ChildClient):
    __resource_opener: ResourceOpenerClient

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: any, timeout_interval_milliseconds: int):
        super().__init__(channel, parent, name, ORiN3ObjectType.STREAM, id, option, created_date_time, timeout_interval_milliseconds)
        self.__resource_opener = ResourceOpenerClient(channel)

    def __read_async(self) -> grpc.aio._call.UnaryStreamCall:
        common = CommonRequest(reserved=0)
        request = orin3_stream_pb2.ReadRequest(common=common, id=self.id)
        stub = orin3_stream_pb2_grpc.StreamServiceStub(self.channel)
        return stub.Read(request)

    def get_reader(self) -> StreamReader:
        try:
            call = self.__read_async()
            return StreamReader(call)
        except Exception as err:
            raise ProviderClientError() from err

    async def open_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.open_async(self.id, argument)

    async def close_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.close_async(self.id, argument)
