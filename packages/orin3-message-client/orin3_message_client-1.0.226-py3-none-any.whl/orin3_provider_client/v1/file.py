import datetime
from typing import Dict, List
import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_file_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_file_pb2_grpc

from orin3_provider_client.v1.client_base import ChildClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.client_base import ResourceOpenerClient
from orin3_provider_client.v1.common import ORiN3MessageFileSeekOrigin, ORiN3Value
from orin3_provider_client.v1.common import ORiN3ObjectType
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class FileClient(ChildClient):
    __resource_opener: ResourceOpenerClient

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: datetime, timeout_interval_milliseconds: int):
        super().__init__(channel, parent, name, ORiN3ObjectType.FILE, id, option, created_date_time, timeout_interval_milliseconds)
        self.__resource_opener = ResourceOpenerClient(channel)
    
    async def __can_read_async(self) -> orin3_file_pb2.CanReadFileResponse:
        common = CommonRequest(reserved=0)
        request = orin3_file_pb2.CanReadFileRequest(common=common, id=self.id)
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.CanRead(request)
    
    async def can_read_async(self) -> bool:
        try:
            can_read_result = await self.__can_read_async()
            validate_response(can_read_result)
            return can_read_result.can_read
        except Exception as err:
            raise ProviderClientError() from err

    async def __can_write_async(self) -> orin3_file_pb2.CanWriteFileResponse:
        common = CommonRequest(reserved=0)
        request = orin3_file_pb2.CanWriteFileRequest(common=common, id=self.id)
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.CanWrite(request)

    async def can_write_async(self) -> bool:
        try:
            can_write_result = await self.__can_write_async()
            validate_response(can_write_result)
            return can_write_result.can_write
        except Exception as err:
            raise ProviderClientError() from err

    async def read_async(self, buffer_size: int) -> bytes:
        try:
            common = CommonRequest(reserved=0)
            request = orin3_file_pb2.ReadFileRequest(common=common, id=self.id, buffer_size=buffer_size)
            stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
            stream_call = stub.Read(request)
            results = bytearray()
            while (True):
                response = await stream_call.read()
                if (response == grpc.aio.EOF):
                    break
                results += response.buffer
            return bytes(results)
        except Exception as err:
            raise ProviderClientError() from err

    async def __seek_async(self, offset: int, origin: ORiN3MessageFileSeekOrigin) -> orin3_file_pb2.SeekFileResponse:
        common = CommonRequest(reserved=0)
        request = orin3_file_pb2.SeekFileRequest(common=common, id=self.id, offset=offset, origin=origin.value)
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.Seek(request)

    async def seek_async(self, offset: int, origin: ORiN3MessageFileSeekOrigin) -> int:
        try:
            seek_result = await self.__seek_async(offset, origin)
            validate_response(seek_result)
            return seek_result.position
        except Exception as err:
            raise ProviderClientError() from err
    
    async def __write_async(self, buffer: bytes) -> orin3_file_pb2.WriteFileResponse:
        send_size = 1024 * 1024
        common = CommonRequest(reserved=0)
        cursor = 0
        total_length = len(buffer)
        request_list = []
        while (cursor < len(buffer)):
            request = orin3_file_pb2.WriteFileRequest(
                common=common,
                id=self.id,
                buffer=buffer[cursor:cursor + send_size],
                total_length=total_length
            )
            request_list.append(request)
            cursor += send_size
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.Write(iter(request_list))

    async def write_async(self, buffer: bytes) -> None:
        try:
            write_result = await self.__write_async(buffer)
            validate_response(write_result)
        except Exception as err:
            raise ProviderClientError() from err

    async def __get_length_async(self) -> orin3_file_pb2.GetFileLengthResponse:
        common = CommonRequest(reserved=0)
        request = orin3_file_pb2.GetFileLengthRequest(common=common, id=self.id)
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.GetLength(request)

    async def get_length_async(self) -> int:
        try:
            get_length_result = await self.__get_length_async()
            validate_response(get_length_result)
            return get_length_result.length
        except Exception as err:
            raise ProviderClientError() from err

    async def __set_length_async(self, length: int) -> orin3_file_pb2.SetFileLengthResponse:
        common = CommonRequest(reserved=0)
        request = orin3_file_pb2.SetFileLengthRequest(common=common, id=self.id, length=length)
        stub = orin3_file_pb2_grpc.FileServiceStub(self.channel)
        return await stub.SetLength(request)

    async def set_length(self, length: int) -> None:
        try:
            set_length_result = await self.__set_length_async(length)
            validate_response(set_length_result)
        except Exception as err:
            raise ProviderClientError() from err

    async def open_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.open_async(self.id, argument)

    async def close_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.close_async(self.id, argument)