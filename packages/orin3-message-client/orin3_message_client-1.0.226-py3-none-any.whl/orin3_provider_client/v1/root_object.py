import asyncio
from datetime import datetime
from typing import List
import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest, CommonResponse
from orin3_grpc.message.orin3.provider.v1 import orin3_root_object_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_root_object_pb2

from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.common import ORiN3ObjectType
from orin3_provider_client.v1.common import ORiN3Value
from orin3_provider_client.v1.event import EventClient, EventInfo
from orin3_provider_client.v1.get_value_branch import get_value
from orin3_provider_client.v1.set_value_request_creator import create_orin3value
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class GetRootObjectIdAsyncResult:
    def __init__(self, src: orin3_root_object_pb2.GetRootObjectIdResponse):
        self.__user_defined_id = src.user_defined_id
        self.__root_object_id = src.root_object_id
    
    @property
    def user_defined_id(self) -> bytes:
        return self.__user_defined_id

    @property
    def root_object_id(self) -> bytes:
        return self.__root_object_id


class RootObjectInformation:
    def __init__(self, src: orin3_root_object_pb2.GetRootObjectIdResponse):
        self.__orin3_provider_config = src.orin3_provider_config
        self.__connection_count = src.connection_count
    
    @property
    def orin3_provider_config(self) -> str:
        return self.__orin3_provider_config
    
    @property
    def connection_count(self) -> int:
        return self.__connection_count


class SetValuesResult:
    def __init__(self, src: orin3_root_object_pb2.SetValuesResponse):
        self.__succeeded = src.common.result_code == 0
        self.__detail = src.common.detail
    
    @property
    def succeeded(self) -> bool:
        return self.__succeeded
    
    @property
    def detail(self) -> str:
        return self.__detail


class _EventListener:
    __eventStreamCall: grpc.aio._call.StreamStreamCall
    __dict: dict
    __lock: asyncio.Lock
    __task: asyncio.Task

    def __init__(self, eventStreamCall: grpc.aio._call.StreamStreamCall):
        self.__eventStreamCall = eventStreamCall
        self.__dict = {}
        self.__lock = asyncio.Lock()
        self.__task = None

    def start(self) -> None:
        if self.__task == None:
            self.__task = asyncio.create_task(self.__listen())
    
    async def stop_async(self) -> None:
        if self.__task is not None:
            request = orin3_root_object_pb2.OpenEventStreamRequest(end=True)
            await self.__eventStreamCall.write(request)
            await self.__eventStreamCall.done_writing()
            await self.__task
            self.__task = None

    async def __listen(self) -> None:
        while True:
            src = await self.__eventStreamCall.read()
            event_info = EventInfo(src)
            if sum(event_info.id) == 0 and event_info.end:
                break
            async with self.__lock:
                if event_info.id in self.__dict:
                    try:
                        await self.__dict[src.id].publish_async(event_info)
                    except:
                        print("Failed to publish event.")
    
    async def subscribe_async(self, event: EventClient) -> None:
        async with self.__lock:
            self.__dict[event.id] = event

    async def unsubscribe_async(self, event: EventClient | bytes) -> None:
        async with self.__lock:
            if type(event) == "bytes":
                self.__dict.pop(event)
            else:
                self.__dict.pop(event.id)


class RootObjectClient(ParentClient):
    _id: bytes = None
    __event_listner: _EventListener = None

    # pythonではコンストラクタは公開されてしまうので、root_object_idの部分は少し工夫がいる
    # Noneをセットしてからの、get_root_object_idで正規の値を入れる
    def __init__(self, ip: str, port: int, timeout_interval_milliseconds: int = 60000, option: str = "", is_https: bool=False, root_certificates: bytes = None, private_key: bytes = None, certificate_chain: bytes = None) -> None:
        channel = grpc.aio.secure_channel(ip + ':' + str(port), grpc.ssl_channel_credentials(root_certificates, private_key, certificate_chain)) if is_https else grpc.aio.insecure_channel(ip + ':' + str(port))
        created_date_time = datetime.now()
        super().__init__(channel, "Root", ORiN3ObjectType.PROVIDER_ROOT, None, option, created_date_time, timeout_interval_milliseconds)

    async def __aenter__(self):
        await self.init_async()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_async()
    
    async def init_async(self):
        if self._id is None:
            get_id_result = await self.get_root_object_id_async()
            self._id = get_id_result.root_object_id
    
    async def exit_async(self):
        await self.channel.close()

    async def __get_root_object_id_async(self) -> orin3_root_object_pb2.GetRootObjectIdResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.GetRootObjectIdRequest(common=common)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.GetRootObjectId(request)

    async def get_root_object_id_async(self) -> GetRootObjectIdAsyncResult:
        try:
            response = await self.__get_root_object_id_async()
            validate_response(response)
            return GetRootObjectIdAsyncResult(response)
        except Exception as err:
            raise ProviderClientError() from err

    async def __shutdown_async(self) -> orin3_root_object_pb2.ShutdownResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.ShutdownRequest(common=common)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.Shutdown(request)

    async def shutdown_async(self) -> None:
        try:
            result = await self.__shutdown_async()
            validate_response(result)
        except Exception as err:
            raise ProviderClientError() from err

    async def __get_information_async(self) -> orin3_root_object_pb2.GetInformationResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.GetInformationRequest(common=common)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.GetInformation(request)

    async def get_information_async(self) -> RootObjectInformation:
        try:
            result = await self.__get_information_async()
            validate_response(result)
            return RootObjectInformation(result)
        except Exception as err:
            raise ProviderClientError() from err

    async def __register_variables_async(self, variable_ids: List[bytes]) -> orin3_root_object_pb2.RegisterVariablesResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.RegisterVariablesRequest(common=common, variable_ids=variable_ids)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.RegisterVariables(request)

    async def register_variables_async(self, variable_ids: List[bytes]) -> int:
        try:
            result = await self.__register_variables_async(variable_ids)
            validate_response(result)
            return result.registration_id
        except Exception as err:
            raise ProviderClientError() from err

    async def __unregister_variables_async(self, registration_id: int) -> orin3_root_object_pb2.UnregisterVariablesResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.UnregisterVariablesRequest(common=common, registration_id=registration_id)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.RegisterVariables(request)

    async def unregister_variables_async(self, registration_id: int) -> None:
        try:
            result = await self.__unregister_variables_async(registration_id)
            validate_response(result)
        except Exception as err:
            raise ProviderClientError() from err

    async def get_values_async(self, registration_id: int) -> list:
        try:
            common = CommonRequest(reserved=0)
            request = orin3_root_object_pb2.GetValuesRequest(common=common, registration_id=registration_id)
            stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
            stream_call = stub.GetValues(request)
            results = []
            while (True):
                response = await stream_call.read()
                if (response == grpc.aio.EOF):
                    break
                results.append(get_value(response.value))
            return results
        except Exception as err:
            raise ProviderClientError() from err

    async def set_values_async(self, registration_id: int, values: List[ORiN3Value]) -> List[SetValuesResult]:
        try:
            requests = []
            prepend_data = orin3_root_object_pb2.SetValuesRequest(common=CommonRequest(reserved=0), registration_id=registration_id)
            requests.append(prepend_data)
            for value in values:
                requests.append(orin3_root_object_pb2.SetValuesRequest(common=CommonRequest(reserved=0), value=create_orin3value(value.value, value.value_type)))
            stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
            stream_call = stub.SetValues(iter(requests))
            responses = []
            while(True):
                response = await stream_call.read()
                if (response == grpc.aio.EOF):
                    break
                responses.append(SetValuesResult(response))
            return responses
        except Exception as err:
            raise ProviderClientError() from err

    def open_event_stream(self) -> None:
        try:
            if self.__event_listner is not None:
                return
            stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
            call = stub.OpenEventStream()
            event_listener = _EventListener(call)
            event_listener.start()
            self.__event_listner = event_listener
        except Exception as err:
            raise ProviderClientError() from err
    
    async def close_event_stream_async(self) -> None:
        try:
            if self.__event_listner is None:
                return
            await self.__event_listner.stop_async()
            self.__event_listner = None
        except Exception as err:
            raise ProviderClientError() from err

    async def subscribe_event_async(self, event: EventClient) -> None:
        await self.__event_listner.subscribe_async(event)

    async def unsubscribe_event_async(self, event: EventClient | bytes) -> None:
        await self.__event_listner.unsubscribe_async(event)
    
    async def __get_statuses_async(self, ids: List[bytes]) -> orin3_root_object_pb2.GetStatusesResponse:
        common = CommonRequest(reserved=0)
        request = orin3_root_object_pb2.GetStatusesRequest(common=common, ids=ids)
        stub = orin3_root_object_pb2_grpc.RootObjectServiceStub(self.channel)
        return await stub.GetStatuses(request)

    async def get_statuses_async(self, ids: List[bytes]) -> List[int]:
        try:
            result = await self.__get_statuses_async(ids)
            validate_response(result)
            return result.statuses
        except Exception as err:
            raise ProviderClientError() from err
