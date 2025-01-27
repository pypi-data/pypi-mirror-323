import datetime
from typing import Dict, List
import grpc

from orin3_grpc.message.orin3.provider.v1.orin3_common_type_pb2 import CommonRequest
from orin3_grpc.message.orin3.provider.v1 import orin3_job_pb2_grpc
from orin3_grpc.message.orin3.provider.v1 import orin3_job_pb2

from orin3_provider_client.v1.common import ORiN3ObjectType, ORiN3Value
from orin3_provider_client.v1.client_base import ChildClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.client_base import ResourceOpenerClient
from orin3_provider_client.v1.error import ProviderClientError
from orin3_provider_client.v1.result_validator import validate_response


class GetResultAsyncResult:
    def __init__(self, src: orin3_job_pb2.GetResultResponse):
        self.__result = src.result
        self.__is_null_result = src.is_null_result
    
    @property
    def result(self) -> bytes:
        return self.__result

    @property
    def is_null_result(self) -> bool:
        return self.__is_null_result


class JobClient(ChildClient):
    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: datetime, timeout_interval_milliseconds: int):
        super().__init__(channel, parent, name, ORiN3ObjectType.JOB, id, option, created_date_time, timeout_interval_milliseconds)
        self.__resource_opener = ResourceOpenerClient(channel)

    async def __get_standard_output_async(self) -> orin3_job_pb2.GetStandardOutputResponse:
        common = CommonRequest(reserved=0)
        request = orin3_job_pb2.GetStandardOutputRequest(common=common, id=self.id)
        stub = orin3_job_pb2_grpc.JobServiceStub(self.channel)
        return await stub.GetStandardOutput(request)

    async def get_standard_output_async(self) -> str:
        try:
            get_standard_output_result = await self.__get_standard_output_async()
            validate_response(get_standard_output_result)
            return get_standard_output_result.output
        except Exception as err:
            raise ProviderClientError() from err

    async def __get_standard_error_async(self) -> orin3_job_pb2.GetStandardErrorResponse:
        common = CommonRequest(reserved=0)
        request = orin3_job_pb2.GetStandardErrorRequest(common=common, id=self.id)
        stub = orin3_job_pb2_grpc.JobServiceStub(self.channel)
        return await stub.GetStandardError(request)

    async def get_standard_error_async(self) -> str:
        try:
            get_standard_error_result = await self.__get_standard_error_async()
            validate_response(get_standard_error_result)
            return get_standard_error_result.error
        except Exception as err:
            raise ProviderClientError() from err

    async def __get_result_async(self) -> orin3_job_pb2.GetResultResponse:
        common = CommonRequest(reserved=0)
        request = orin3_job_pb2.GetResultRequest(common=common, id=self.id)
        stub = orin3_job_pb2_grpc.JobServiceStub(self.channel)
        return await stub.GetResult(request)

    async def get_result_async(self) -> GetResultAsyncResult:
        try:
            get_result_result = await self.__get_result_async()
            validate_response(get_result_result)
            return GetResultAsyncResult(get_result_result)
        except Exception as err:
            raise ProviderClientError() from err
    
    async def start_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.open_async(self.id, argument)

    async def stop_async(self, argument: Dict[str, ORiN3Value | List[ORiN3Value] | list] = {}) -> None:
        await self.__resource_opener.close_async(self.id, argument)
