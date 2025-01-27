from typing import List
from enum import IntEnum
import grpc

from orin3_grpc.message.orin3.remoteengine.v1 import orin3_remote_engine_pb2
from orin3_grpc.message.orin3.remoteengine.v1 import orin3_remote_engine_pb2_grpc
from orin3_grpc.message.orin3.remoteengine_ex.v1 import orin3_remote_engine_ex_pb2
from orin3_grpc.message.orin3.remoteengine_ex.v1 import orin3_remote_engine_ex_pb2_grpc

from orin3_remote_engine_client.v1.error import RemoteEngineClientError
from orin3_remote_engine_client.v1.result_validator import validate_response


class TelemetryTypeFlag(IntEnum):
    LOG = 0x0001
    METRIC = 0x0002
    TRACE = 0x0004


class TelemetryProtocolType(IntEnum):
    GRPC = 0
    HTTP_PROTOBUF = 1

class ProxySetting(IntEnum):
    USE_SYSTEM_PROXY = 0
    EXPLICIT_PROXY = 1
    DO_NOT_USE_PROXY= 2


class LogLevel(IntEnum):
    TRACE = 0
    DEBUG = 1
    INFORMATION = 2
    WARNING = 3
    CRITICAL = 5
    ERROR = 4
    NONE = 6


class ProviderPathType(IntEnum):
    NONE = 0
    DEFAULT_ROOT = 1
    ATTACHED_ROOT = 2
    ATTACHED_FILE = 3


class GetAvailableProvidersOption(IntEnum):
    ALL = 0
    DEFAULT_ONLY = 1
    ATTACHED_ONLY = 2


class ProtocolType(IntEnum):
    HTTP = 0
    HTTPS = 1


class OsPlatform(IntEnum):
    UNKNOWN_OS = 0
    WINDOWS = 1
    LINUX = 2
    FREE_BSD = 3
    OSX = 4


class CommonResponse:
    def __init__(self, src: orin3_remote_engine_pb2.CommonResponse):
        self.__result_code = src.resultCode
        self.__detail = src.detail
    
    @property
    def result_code(self) -> int:
        return self.__result_code
    
    @property
    def detail(self) -> str:
        return self.__detail


class ProviderEndpoint:
    def __init__(self, protocol_type: ProtocolType, host: str, port: int):
        self.__protocol_type = protocol_type
        self.__host = host
        self.__port = port

    @property
    def protocol_type(self) -> int:
        return self.__protocol_type
    
    @property
    def host(self) -> str:
        return self.__host
    
    @property
    def port(self) -> int:
        return self.__port


class ProviderEndpointResult:
    def __init__(self, index: int, ip_address: str, port: int, uri: str, protocol_type: ProtocolType):
        self.__index = index
        self.__ip_address = ip_address
        self.__port = port
        self.__uri = uri
        self.__protocol_type = protocol_type
    
    @property
    def index(self) -> int:
        return self.__index
    
    @property
    def ip_address(self) -> str:
        return self.__ip_address

    @property
    def port(self) -> int:
        return self.__port

    @property
    def uri(self) -> str:
        return self.__uri
    
    @property
    def protocol_type(self) -> ProtocolType:
        return self.__protocol_type
    


class ProviderInformation:
    def __init__(self, provider_information: orin3_remote_engine_pb2.ProviderInformation):
        endpoints = [ProviderEndpointResult(src_ep.index, src_ep.ip_address, src_ep.port, src_ep.uri, src_ep.protocol_type) for src_ep in provider_information.endpoints]
        self.__endpoints = endpoints
    
    @property
    def endpoints(self) -> List[ProviderEndpointResult]:
        return self.__endpoints


class WakeupProviderAsyncResult:
    def __init__(self, response: orin3_remote_engine_pb2.WakeupProviderResponse):
        self.__id = response.id
        self.__provider_information = ProviderInformation(response.provider_information)
    
    @property
    def id(self) -> bytes:
        return self.__id
    
    @property
    def provider_information(self) -> ProviderInformation:
        return self.__provider_information


class ProviderPackageInfo:
    def __init__(self, package_info: orin3_remote_engine_ex_pb2.PackageInfo):
        self.__id = package_info.id
        self.__version = package_info.version
        self.__description = package_info.description
        self.__authors = package_info.authors
        self.__title = package_info.title
        self.__project_url = package_info.project_url
        self.__license = package_info.license
        self.__icon = package_info.icon
        self.__release_notes = package_info.release_notes
        self.__copyright = package_info.copyright
        self.__tags = package_info.tags

    @property
    def id(self) -> str:
        return self.__id

    @property
    def version(self) -> str:
        return self.__version

    @property
    def description(self) -> str:
        return self.__description

    @property
    def authors(self) -> str:
        return self.__authors

    @property
    def title(self) -> str:
        return self.__title

    @property
    def project_url(self) -> str:
        return self.__project_url

    @property
    def license(self) -> str:
        return self.__license

    @property
    def icon(self) -> str:
        return self.__icon

    @property
    def release_notes(self) -> str:
        return self.__release_notes

    @property
    def copyright(self) -> str:
        return self.__copyright

    @property
    def tags(self) -> str:
        return self.__tags


class GetAvailableProvidersAsyncResult:
    def __init__(self, response: orin3_remote_engine_ex_pb2.GetAvailableProvidersResponse):
        common = response.common
        provider_config_info = response.provider_config_info
        self.__provider_config_data = provider_config_info.json
        self.__provider_path_type = provider_config_info.path_type
        self.__result_code = common.result_code
        self.__detail = common.detail
        self.__provider_package_info = ProviderPackageInfo(response.package_info)

    @property
    def provider_config_data(self) -> str:
        return self.__provider_config_data
    
    @property
    def provider_path_type(self) -> ProviderPathType:
        return self.__provider_path_type
    
    @property
    def result_code(self) -> int:
        return self.__result_code
    
    @property
    def detail(self) -> str:
        return self.__detail
    
    @property
    def provider_package_info(self) -> ProviderPackageInfo:
        return self.__provider_package_info


class GetRemoteEngineStatusAsyncResult:
    def __init__(self, response: orin3_remote_engine_pb2.GetRemoteEngineStatusResponse):
        self.__status = response.status
        self.__host = response.host
        self.__addresses = response.addresses
        self.__version = response.version
        self.__os_platform = response.os_platform
        self.__os_description = response.os_description
    
    @property
    def status(self) -> int:
        return self.__status
    
    @property
    def host(self) -> str:
        return self.__host
    
    @property
    def addresses(self) -> List[str]:
        return self.__addresses
    
    @property
    def version(self) -> str:
        return self.__version

    @property
    def os_platform(self) -> OsPlatform:
        return self.__os_platform
    
    @property
    def os_description(self) -> str:
        return self.__os_description


class TelemetryEndpoint:
    def __init__(self, uri: str, telemetry_type_flag: TelemetryTypeFlag, proxy_setting: ProxySetting, proxy_uri: str="", protocol_type: TelemetryProtocolType=TelemetryProtocolType.GRPC, reserved: bytes=None):
        self.__uri = uri
        self.__telemetry_type_flag = telemetry_type_flag
        self.__proxy_setting = proxy_setting
        self.__proxy_uri = proxy_uri
        self.__reserved = reserved
        self.__protocol_type = protocol_type
    
    @property
    def uri(self) -> str:
        return self.__uri
    
    @property
    def telemetry_type_flag(self) -> TelemetryTypeFlag:
        return self.__telemetry_type_flag
    
    @property
    def proxy_setting(self) -> int:
        return self.__proxy_setting

    @property
    def proxy_uri(self) -> str:
        return self.__proxy_uri

    @property
    def protocol_type(self) -> TelemetryProtocolType:
        return self.__protocol_type

    @property
    def reserved(self) -> bytes:
        return self.__reserved


class TelemetryOption:
    def __init__(self, attributes: dict, use_remote_engine_telemetry_setting: bool, telemetry_endpoints: List[TelemetryEndpoint]):
        self.__attributes = attributes
        self.__use_remote_engine_telemetry_setting = use_remote_engine_telemetry_setting
        self.__telemetry_endpoints = telemetry_endpoints

    @property
    def attributes(self) -> dict:
        return self.__attributes
    
    @property
    def use_remote_engine_telemetry_setting(self) -> bool:
        return self.__use_remote_engine_telemetry_setting

    @property
    def telemetry_endpoints(self) -> List[TelemetryEndpoint]:
        return self.__telemetry_endpoints


class ListProviderProcessAsyncResult:
    def __init__(self, response: orin3_remote_engine_ex_pb2.ListProviderProcessResponse):
        self.__id = response.id
        self.__name = response.name
        self.__version = response.version
        self.__pid = response.pid
        self.__created_time = response.createdTime
        self.__end_points = [end_point for end_point in response.endPoints]
        self.__install_path = response.installPath
        self.__provider_id = response.providerId
        self.__actual_end_points = [end_point for end_point in response.actualEndPoints]
    
    @property
    def id(self) -> bytes:
        return self.__id

    @property
    def name(self) -> str:
        return self.__name
    
    @property
    def version(self) -> str:
        return self.__version
    
    @property
    def pid(self) -> int:
        return self.__pid
    
    @property
    def created_time(self) -> str:
        return self.__created_time
    
    @property
    def end_points(self) -> List[str]:
        return self.__end_points
    
    @property
    def install_path(self) -> str:
        return self.__install_path
    
    @property
    def provider_id(self) -> str:
        return self.__provider_id
    
    @property
    def actual_end_points(self) -> List[str]:
        return self.__actual_end_points


class RemoteEngineClient:
    def __init__(self, ip: str, port: int, is_https: bool = False, root_certificates: bytes = None, private_key: bytes = None, certificate_chain: bytes = None) -> None:
        if is_https:
            self.__async_channel = grpc.aio.secure_channel(ip + ':' + str(port), grpc.ssl_channel_credentials(root_certificates, private_key, certificate_chain))
        else:
            self.__async_channel = grpc.aio.insecure_channel(ip + ':' + str(port))
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_async()
    
    async def init_async(self):
        None

    async def exit_async(self):
        await self.__async_channel.close()

    def __convert_endpoint(self, endpoint: ProviderEndpoint) -> orin3_remote_engine_pb2.ProviderCoreStartupArgumentEndpointInfo:
        return orin3_remote_engine_pb2.ProviderCoreStartupArgumentEndpointInfo(
            protocol_type=endpoint.protocol_type, host=endpoint.host, port=endpoint.port, reserved=None)

    def __convert_telemetry_endpoint(self, telemetry_endpoint: TelemetryEndpoint) -> orin3_remote_engine_pb2.TelemetryEndpoint:
        return orin3_remote_engine_pb2.TelemetryEndpoint(
            uri=telemetry_endpoint.uri,
            telemetry_type_flag=int(telemetry_endpoint.telemetry_type_flag),
            proxy_setting=telemetry_endpoint.proxy_setting,
            proxy_uri=telemetry_endpoint.proxy_uri,
            protocol_type=telemetry_endpoint.protocol_type,
            reserved=telemetry_endpoint.reserved)

    def __convert_telemetry_option(self, telemetry_option: TelemetryOption) -> orin3_remote_engine_pb2.TelemetryOption:
        telemetry_endpoints = [self.__convert_telemetry_endpoint(it) for it in telemetry_option.telemetry_endpoints]
        return orin3_remote_engine_pb2.TelemetryOption(
            attributes=telemetry_option.attributes,
            telemetry_endpoints=telemetry_endpoints)

    async def wakeup_provider_async(
        self,
        id: str,
        version: str,
        thread_safe_mode: bool,
        endpoints: List[ProviderEndpoint],
        log_level: LogLevel,
        telemetry_option: TelemetryOption,
        extension: dict = {},
        ) -> WakeupProviderAsyncResult:
        try:
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            converted_endpoints = [self.__convert_endpoint(it) for it in endpoints]
            converted_telemetry_information = self.__convert_telemetry_option(telemetry_option)
            provider_core_startup_argument = orin3_remote_engine_pb2.ProviderCoreStartupArgument(
                thread_safe_mode=thread_safe_mode,
                provider_core_startup_argument_endpoint_infos=converted_endpoints,
                log_level=log_level,
                telemetry_option=converted_telemetry_information,
                extension=extension)
            request = orin3_remote_engine_pb2.WakeupProviderRequest(
                common=common,
                id=id,
                version=version,
                provider_startup_argument=provider_core_startup_argument)
            stub = orin3_remote_engine_pb2_grpc.RemoteEngineServiceStub(self.__async_channel)
            result = await stub.WakeupProvider(request)
            validate_response(result)
            return WakeupProviderAsyncResult(result)
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def install_provider_async(
        self,
        force: bool,
        data: bytes
        ) -> None:
        try:
            send_size = 1024 * 1024
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineExServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            cursor = 0
            request_list = []
            while (cursor < len(data)):
                request = orin3_remote_engine_ex_pb2.InstallProviderRequest(
                    common=common,
                    force=force,
                    data=data[cursor:cursor + send_size]
                )
                request_list.append(request)
                cursor += send_size
            result = await stub.InstallProvider(iter(request_list))
            validate_response(result)
        except Exception as err:
            raise RemoteEngineClientError() from err
        
    async def unisntall_provider_async(self, id: str, version: str) -> None:
        try:
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineExServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_ex_pb2.UninstallProviderRequest(
                common=common,
                id=id,
                version=version
            )
            result = await stub.UninstallProvider(request)
            validate_response(result)
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def get_available_providers_async(self, option: GetAvailableProvidersOption) -> List[GetAvailableProvidersAsyncResult]:
        try:
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineExServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_ex_pb2.GetAvailableProvidersRequest(
                common=common,
                option=option
            )
            stream_call = stub.GetAvailableProviders(request)
            results = []
            while (True):
                response = await stream_call.read()
                if (response == grpc.aio.EOF):
                    break
                results.append(GetAvailableProvidersAsyncResult(response))
            return results
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def restart_async(self) -> None:
        try:
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineExServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_ex_pb2.RestartRequest(
                common = common
            )
            result = await stub.Restart(request)
            validate_response(result)
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def terminate_provider_async(self, id: bytes) -> None:
        try:
            stub = orin3_remote_engine_pb2_grpc.RemoteEngineServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_pb2.TerminateProviderRequest(
                common = common,
                id = id
            )
            result = await stub.TerminateProvider(request)
            validate_response(result)
        except Exception as err:
            raise RemoteEngineClientError() from err
        
    async def get_remote_engine_status_async(self) -> GetRemoteEngineStatusAsyncResult:
        try:
            stub = orin3_remote_engine_pb2_grpc.RemoteEngineServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_pb2.GetRemoteEngineStatusRequest(
                common = common
            )
            result = await stub.GetRemoteEngineStatus(request)
            validate_response(result)
            return GetRemoteEngineStatusAsyncResult(result)
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def ping_async(self, host: str) -> int:
        try:
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineExServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_ex_pb2.PingRequest(
                common = common,
                host = host
            )
            result = await stub.Ping(request)
            validate_response(result)
            return result.result
        except Exception as err:
            raise RemoteEngineClientError() from err

    async def list_provider_process_async(self, name_filter: str) -> List[ListProviderProcessAsyncResult]:
        try:
            stub = orin3_remote_engine_ex_pb2_grpc.RemoteEngineServiceStub(self.__async_channel)
            common = orin3_remote_engine_pb2.CommonRequest(reserved=0)
            request = orin3_remote_engine_ex_pb2.ListProviderProcessRequest(
                common = common,
                name_filter = name_filter
            )
            stream_call = stub.ListProviderProcess(request)
            results = []
            while (True):
                response = await stream_call.read()
                if (response == grpc.aio.EOF):
                    break
                results.append(ListProviderProcessAsyncResult(response))
            return results
        except Exception as err:
            raise RemoteEngineClientError() from err