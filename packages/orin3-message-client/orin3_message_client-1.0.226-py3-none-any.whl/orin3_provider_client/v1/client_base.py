from datetime import datetime
from typing import Dict, List
import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_base_object_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_base_object_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_child_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_child_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_executable_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_executable_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_parent_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_parent_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_resource_opener_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_resource_opener_pb2_grpc

from orin3_provider_client.v1.binary_converter import BinaryConverter
from orin3_provider_client.v1.common import ORiN3ObjectType, ORiN3Value
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class GetObjectInfoAsyncResult:
    def __init__(self, src: orin3_base_object_pb2.GetObjectInfoResponse):
        self.__name = src.name
        self.__type_name = src.type_name
        self.__option = src.option
        self.__created_date_time = BinaryConverter.from_int64_to_datetime(src.created_datetime)
        self.__object_type = src.object_type
        self.__extra = src.extra
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def type_name(self) -> str:
        return self.__type_name

    @property
    def option(self) -> str:
        return self.__option
    
    @property
    def created_date_time(self) -> datetime:
        return self.__created_date_time
    
    @property
    def object_type(self) -> int:
        return self.__object_type
    
    @property
    def extra(self) -> int:
        return self.__extra


class ORiN3ExecutableClient:
    __channel: grpc.Channel

    def __init__(self, channel: grpc.Channel) -> None:
        self.__channel = channel

    async def __execute_async(self, id: bytes, command_name: str, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list]) -> orin3_executable_pb2.ExecuteResponse:
        common = CommonRequest(reserved=0)
        request = orin3_executable_pb2.ExecuteRequest(common=common, id=id, command_name=command_name, argument=BinaryConverter.from_dict_to_bytes(argument))
        stub = orin3_executable_pb2_grpc.ExecutableServiceStub(self.__channel)
        return await stub.Execute(request)

    async def execute_async(self, id: bytes, command_name: str, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> dict:
        try:
            execute_result = await self.__execute_async(id, command_name, argument)
            validate_response(execute_result)
            return BinaryConverter.from_bytes_to_dict(execute_result.result)
        except Exception as err:
            raise ProviderClientError() from err


class BaseObjectClient:
    __channel: grpc.Channel
    _id: bytes
    __orin3object_type: any
    __created_date_time: datetime
    __option: str
    __name: str
    __timeout_interval_milliseconds: int
    __executable: ORiN3ExecutableClient

    def __init__(self, channel: grpc.Channel, name: str, type: any, id: bytes, option: str, created_date_time: datetime, timeout_interval_milliseconds: int) -> None:
        self.__channel = channel
        self.__name = name
        self.__orin3object_type = type
        self.__created_date_time = created_date_time
        self._id = id
        self.__option = option
        self.__timeout_interval_milliseconds = timeout_interval_milliseconds
        self.__executable = ORiN3ExecutableClient(channel)

    @property
    def channel(self) -> grpc.Channel:
        return self.__channel
    
    @property
    def id(self) -> bytes:
        return self._id
    
    @property
    def orin3object_type(self) -> any:
        return self.__orin3object_type
    
    @property
    def created_date_time(self) -> datetime:
        return self.__created_date_time
    
    @property
    def option(self) -> str:
        return self.__option
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def timeout_interval_milliseconds(self) -> int:
        return self.__timeout_interval_milliseconds

    async def __get_object_info_async(self) -> orin3_base_object_pb2.GetObjectInfoResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.GetObjectInfoRequest(common=common, id=self.id)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.GetObjectInfo(request)

    async def get_object_info_async(self) -> GetObjectInfoAsyncResult:
        try:
            get_object_info_result = await self.__get_object_info_async()
            validate_response(get_object_info_result)
            return GetObjectInfoAsyncResult(get_object_info_result)
        except Exception as err:
            raise ProviderClientError() from err
    
    async def __get_status_async(self) -> orin3_base_object_pb2.GetStatusResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.GetStatusRequest(common=common, id=self.id)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.GetStatus(request)

    async def get_status_async(self) -> int:
        try:
            get_status_result = await self.__get_status_async()
            validate_response(get_status_result)
            return get_status_result.status
        except Exception as err:
            raise ProviderClientError() from err

    async def __get_tag_async(self, key: str) -> orin3_base_object_pb2.GetTagResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.GetTagRequest(common=common, id=self.id, key=key)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.GetTag(request)

    async def get_tag_async(self, key: str) -> any:
        try:
            get_tag_result = await self.__get_tag_async(key)
            validate_response(get_tag_result)
            return BinaryConverter.from_bytes_to_object(get_tag_result.tag).data
        except Exception as err:
            raise ProviderClientError() from err

    async def __set_tag_async(self, key: str, tag: ORiN3Value | List[ORiN3Value] | list) -> orin3_base_object_pb2.SetTagResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.SetTagRequest(common=common, id=self.id, key=key, tag=BinaryConverter.from_object_to_bytes(tag))
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.SetTag(request)

    async def set_tag_async(self, key: str, tag: ORiN3Value | List[ORiN3Value] | list) -> None:
        try:
            set_tag_result = await self.__set_tag_async(key, tag)
            validate_response(set_tag_result)
        except Exception as err:
            raise ProviderClientError() from err
    
    async def __get_tag_keys_async(self) -> orin3_base_object_pb2.GetTagKeysResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.GetTagKeysRequest(common=common, id=self.id)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.GetTagKeys(request)

    async def get_tag_keys_async(self) -> List[str]:
        try:
            get_tag_keys_result = await self.__get_tag_keys_async()
            validate_response(get_tag_keys_result)
            return get_tag_keys_result.keys
        except Exception as err:
            raise ProviderClientError() from err

    async def __remove_tag_async(self, key: str) -> orin3_base_object_pb2.RemoveTagResponse:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.RemoveTagRequest(common=common, id=self.id, key=key)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(self.channel)
        return await stub.RemoveTag(request)

    async def remove_tag_async(self, key: str) -> None:
        try:
            remove_tag_result = await self.__remove_tag_async(key)
            validate_response(remove_tag_result)
        except Exception as err:
            raise ProviderClientError() from err

    async def execute_async(self, command_name: str, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> dict:
        return await self.__executable.execute_async(self.id, command_name, argument)


class ChildInformation:
    def __init__(self, src: orin3_parent_pb2.ChildInformation):
        self.__id = src.id
        self.__name = src.name
        self.__orin3_object_type = src.orin3_object_type
    
    @property
    def id(self) -> bytes:
        return self.__id
    
    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def orin3_object_type(self) -> ORiN3ObjectType:
        return self.__orin3_object_type


class ParentClient(BaseObjectClient):
    def __init__(self, channel: grpc.Channel, name: str, type: any, id: bytes, option: str, created_date_time: datetime, timeout_interval_miilliseconds: int) -> None:
        super().__init__(channel, name, type, id, option, created_date_time, timeout_interval_miilliseconds)

    async def __get_child_ids_async(self) -> orin3_parent_pb2.GetChildIdsResponse:
        common = CommonRequest(reserved=0)
        request = orin3_parent_pb2.GetChildIdsRequest(common=common, id=self.id)
        stub = orin3_parent_pb2_grpc.ParentServiceStub(self.channel)
        return await stub.GetChildIds(request)

    async def get_child_ids_async(self) -> List[bytes]:
        try:
            get_child_ids_result = await self.__get_child_ids_async()
            validate_response(get_child_ids_result)
            return get_child_ids_result.child_ids
        except Exception as err:
            raise ProviderClientError() from err
    
    async def __get_child_informations_async(self) -> orin3_parent_pb2.GetChildInformationsResponse:
        common = CommonRequest(reserved=0)
        request = orin3_parent_pb2.GetChildInformationsRequest(common=common, id=self.id)
        stub = orin3_parent_pb2_grpc.ParentServiceStub(self.channel)
        return await stub.GetChildInformations(request)
    
    async def get_child_informations_async(self) -> List[ChildInformation]:
        try:
            get_child_informations_result = await self.__get_child_informations_async()
            validate_response(get_child_informations_result)
            return [ChildInformation(it) for it in get_child_informations_result.child_informations]
        except Exception as err:
            raise ProviderClientError() from err


class ChildClient(BaseObjectClient):
    __parent: ParentClient

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, type: any, id: bytes, option: str, created_date_time: any, timeout_interval_miilliseconds: int) -> None:
        super().__init__(channel, name, type, id, option, created_date_time, timeout_interval_miilliseconds)
        self.__parent = parent
    
    @property
    def parent(self) -> ParentClient:
        return self.__parent;
    
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


class ResourceOpenerClient:
    __channel: grpc.Channel

    def __init__(self, channel: grpc.Channel) -> None:
        self.__channel = channel

    async def __open_async(self, id: bytes, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list]) -> orin3_resource_opener_pb2.OpenResponse:
        common = CommonRequest(reserved=0)
        request = orin3_resource_opener_pb2.OpenRequest(common=common, id=id, argument=BinaryConverter.from_dict_to_bytes(argument))
        stub = orin3_resource_opener_pb2_grpc.ResourceOpenerServiceStub(self.__channel)
        return await stub.Open(request)

    async def open_async(self, id: bytes, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        try:
            open_result = await self.__open_async(id, argument)
            validate_response(open_result)
        except Exception as err:
            raise ProviderClientError() from err

    async def __close_async(self, id:bytes, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list]) -> orin3_resource_opener_pb2.CloseResponse:
        common = CommonRequest(reserved=0)
        request = orin3_resource_opener_pb2.CloseRequest(common=common, id=id, argument=BinaryConverter.from_dict_to_bytes(argument))
        stub = orin3_resource_opener_pb2_grpc.ResourceOpenerServiceStub(self.__channel)
        return await stub.Close(request)

    async def close_async(self, id:bytes, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        try:
            close_result = await self.__close_async(id, argument)
            validate_response(close_result)
        except Exception as err:
            raise ProviderClientError() from err
