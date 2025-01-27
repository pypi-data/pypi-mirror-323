from typing import Callable
import asyncio
import datetime
import grpc

from orin3_provider_client.v1.binary_converter import BinaryConverter
from orin3_provider_client.v1.client_base import ChildClient
from orin3_provider_client.v1.client_base import ParentClient
from orin3_provider_client.v1.common import ORiN3ObjectType


class EventInfo:
    def __init__(self, src: any):
        self.__id = src.id
        self.__args = BinaryConverter.from_bytes_to_object(src.args).data
        self.__end = src.end
    
    @property
    def id(self) -> bytes:
        return self.__id
    
    @property
    def args(self) -> dict:
        return self.__args
    
    @property
    def end(self) -> bool:
        return self.__end


class EventClient(ChildClient):
    __subscription_key: int
    __handlers: dict
    __lock: asyncio.Lock

    def __init__(self, channel: grpc.Channel, parent: ParentClient, name: str, id: bytes, option: str, created_date_time: datetime, timeout_interval_milliseconds: int):
        super().__init__(channel, parent, name, ORiN3ObjectType.EVENT, id, option, created_date_time, timeout_interval_milliseconds)
        self.__subscription_key = 0
        self.__handlers = {}
        self.__lock = asyncio.Lock()

    async def publish_async(self, event_info: EventInfo) -> None:
        async with self.__lock:
            for key in self.__handlers:
                self.__handlers[key](event_info.args)
    
    async def subscribe_async(self, handler: Callable[[dict], None]) -> int:
        async with self.__lock:
            key = self.__subscription_key + 1
            self.__handlers[key] = handler
            self.__subscription_key = key
            return key

    async def unsubscribe_async(self, subscription_key: int) -> None:
        async with self.__lock:
            self.__handlers.pop(subscription_key)
    
    async def unsubscribe_all_async(self) -> None:
        async with self.__lock:
            self.__handlers.clear()
