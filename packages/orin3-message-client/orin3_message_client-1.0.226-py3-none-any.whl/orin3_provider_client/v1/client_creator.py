import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_base_object_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_base_object_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_child_creator_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_child_creator_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_controller_creator_pb2
from orin3_grpc.message.orin3.provider.v1 import orin3_controller_creator_pb2_grpc
from orin3_grpc.message.orin3.provider.v1.orin3_child_creator_pb2 import CreateVariableRequest

from orin3_provider_client.v1.client_base import GetObjectInfoAsyncResult
from orin3_provider_client.v1.client_base import BaseObjectClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.common import ORiN3ObjectType
from orin3_provider_client.v1.common import ORiN3ValueType
from orin3_provider_client.v1.root_object import RootObjectClient
from orin3_provider_client.v1.controller import ControllerClient
from orin3_provider_client.v1.event import EventClient
from orin3_provider_client.v1.file import FileClient
from orin3_provider_client.v1.job import JobClient
from orin3_provider_client.v1.module import ModuleClient
from orin3_provider_client.v1.stream import StreamClient
from orin3_provider_client.v1.variable import VariableClient
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response

class ClientCreator:
    @classmethod
    async def attach_root_object_async(self, ip: str, port: int, timeout_interval_milliseconds: int = 60000, option: str = "", is_https: bool=False, root_certificates: bytes = None, private_key: bytes = None, certificate_chain: bytes = None) -> RootObjectClient:
        try:
            root_object = RootObjectClient(ip, port, timeout_interval_milliseconds, option, is_https, root_certificates, private_key, certificate_chain)
            await root_object.init_async()
            return root_object
        except Exception as err:
            raise ProviderClientError() from err
        
    @classmethod
    async def __create_controller_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str) -> orin3_controller_creator_pb2.CreateControllerResponse:
        common = CommonRequest(reserved=0)
        request = orin3_controller_creator_pb2.CreateControllerRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option)
        stub = orin3_controller_creator_pb2_grpc.ControllerCreatorServiceStub(channel)
        create_controller_result = await stub.CreateController(request)
        return create_controller_result
    
    @classmethod
    async def create_controller_async(self, parent: ParentClient, name: str, type_name: str, option: str) -> ControllerClient:
        try:
            create_controller_result = await self.__create_controller_async(parent.channel, parent.id, name, type_name, option)
            validate_response(create_controller_result)
            controller = ControllerClient(
                parent.channel, parent, name, create_controller_result.id, option,
                create_controller_result.created_datetime, parent.timeout_interval_milliseconds)
            return controller
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __create_module_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str) -> orin3_child_creator_pb2.CreateModuleResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_creator_pb2.CreateModuleRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        create_module_result = await stub.CreateModule(request)
        return create_module_result
    
    @classmethod
    async def create_module_async(self, parent: ParentClient, name: str, type_name: str, option: str) -> ModuleClient:
        try:
            create_module_result = await self.__create_module_async(parent.channel, parent.id, name, type_name, option)
            validate_response(create_module_result)
            module = ModuleClient(
                parent.channel, parent, name, create_module_result.module_id, option,
                create_module_result.created_datetime, parent.timeout_interval_milliseconds)
            return module
        except Exception as err:
            raise ProviderClientError() from err

    @staticmethod
    def __create_variable_request(parent_id: bytes, name: str, type_name: str, option: str, value_type: ORiN3ValueType) -> CreateVariableRequest:
        common = CommonRequest(reserved=0)
        return CreateVariableRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option, value_type = value_type.value)

    @classmethod
    async def __create_variable_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str, variable_type: ORiN3ValueType) -> orin3_child_creator_pb2.CreateVariableResponse:
        request = self.__create_variable_request(parent_id, name, type_name, option, variable_type)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        create_variable_result = await stub.CreateVariable(request)
        return create_variable_result

    @classmethod
    async def create_variable_async(self, parent: ParentClient, name: str, type_name: str, option: str, value_type: ORiN3ValueType) -> VariableClient:
        try:
            create_variable_result = await self.__create_variable_async(parent.channel, parent.id, name, type_name, option, value_type)
            validate_response(create_variable_result)
            variable = VariableClient(
                parent.channel, parent, name, create_variable_result.variable_id, option,
                create_variable_result.created_datetime, value_type, parent.timeout_interval_milliseconds)
            return variable
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __create_job_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str) -> orin3_child_creator_pb2.CreateJobResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_creator_pb2.CreateJobRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        create_job_result = await stub.CreateJob(request)
        return create_job_result
    
    @classmethod
    async def create_job_async(self, parent: ParentClient, name: str, type_name: str, option: str) ->JobClient:
        try:
            create_job_result = await self.__create_job_async(parent.channel, parent.id, name, type_name, option)
            validate_response(create_job_result)
            job = JobClient(
                parent.channel, parent, name, create_job_result.job_id, option,
                create_job_result.created_datetime, parent.timeout_interval_milliseconds)
            return job
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __create_stream_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str, value_type: ORiN3ValueType) -> orin3_child_creator_pb2.CreateStreamResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_creator_pb2.CreateStreamRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option, value_type=value_type.value)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        return await stub.CreateStream(request)
    
    @classmethod
    async def create_stream_async(self, parent: ParentClient, name: str, type_name: str, option: str) -> StreamClient:
        try:
            create_stream_result = await self.__create_stream_async(parent.channel, parent.id, name, type_name, option, ORiN3ValueType.ORIN3_UINT8_ARRAY)
            validate_response(create_stream_result)
            stream = StreamClient(
                parent.channel, parent, name, create_stream_result.stream_id, option, 
                create_stream_result.created_datetime, parent.timeout_interval_milliseconds)
            return stream
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __create_event_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str) -> orin3_child_creator_pb2.CreateEventResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_creator_pb2.CreateEventRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        create_event_result =  await stub.CreateEvent(request)
        return create_event_result
    
    @classmethod
    async def create_event_async(self, parent: ParentClient, name: str, type_name: str, option: str) -> EventClient:
        try:
            create_event_result = await self.__create_event_async(parent.channel, parent.id, name, type_name, option)
            validate_response(create_event_result)
            event = EventClient(
                parent.channel, parent, name, create_event_result.event_id, option, 
                create_event_result.created_datetime, parent.timeout_interval_milliseconds)
            return event
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __create_file_async(self, channel: grpc.Channel, parent_id: bytes, name: str, type_name: str, option: str) -> orin3_child_creator_pb2.CreateFileResponse:
        common = CommonRequest(reserved=0)
        request = orin3_child_creator_pb2.CreateFileRequest(common=common, parent_id=parent_id, name=name, type_name=type_name, option=option)
        stub = orin3_child_creator_pb2_grpc.ChildCreatorServiceStub(channel)
        create_file_result = await stub.CreateFile(request)
        return create_file_result

    @classmethod
    async def create_file_async(self, parent: ParentClient, name: str, type_name: str, option: str) -> FileClient:
        try:
            create_file_result = await self.__create_file_async(parent.channel, parent.id, name, type_name, option)
            validate_response(create_file_result)
            file = FileClient(
                parent.channel, parent, name, create_file_result.file_id, option, 
                create_file_result.created_datetime, parent.timeout_interval_milliseconds)
            return file
        except Exception as err:
            raise ProviderClientError() from err

    @classmethod
    async def __get_child_obejct_info_async(self, parent: ParentClient, id: bytes) -> GetObjectInfoAsyncResult:
        common = CommonRequest(reserved=0)
        request = orin3_base_object_pb2.GetObjectInfoRequest(common=common, id=id)
        stub = orin3_base_object_pb2_grpc.BaseObjectServiceStub(parent.channel)
        return GetObjectInfoAsyncResult(await stub.GetObjectInfo(request))

    @classmethod
    async def attach_child_async(self, parent: ParentClient, id: bytes) -> BaseObjectClient:
        info = await self.__get_child_obejct_info_async(parent, id)
        if info.object_type == ORiN3ObjectType.CONTROLLER:
            return ControllerClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.EVENT:
            return ModuleClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.FILE:
            return FileClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.JOB:
            return JobClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.MODULE:
            return ModuleClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.STREAM:
            return StreamClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, parent.timeout_interval_milliseconds)
        elif info.object_type == ORiN3ObjectType.VARIABLE:
            return VariableClient(parent.channel, parent, info.name, id, info.option, info.created_date_time, ORiN3ValueType(info.extra), parent.timeout_interval_milliseconds)
