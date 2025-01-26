import asyncio
import json
import logging
from typing import Any

from dogpile_breaker import CacheRegion, RedisStorageBackend
from dogpile_breaker.middleware import StorageBackendMiddleware

log = logging.getLogger(__name__)


class LoggingProxy(StorageBackendMiddleware):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        pass

    async def get_serialized(self, key: str) -> bytes | None:
        log.error(f"get_serialized LoggingProxy: {key}")
        result = await self.proxied.get_serialized(key)
        log.error(f"LoggingProxy processing result: {result}")
        return result


class AnotherProxy(StorageBackendMiddleware):
    def __init__(self, text: str, sleep_sec: int) -> None:
        self.text = text
        self.sleep_sec = sleep_sec

    async def get_serialized(self, key: str) -> bytes | None:
        log.error(f"[{self.text}]get_serialized AnotherProxy: {key}")
        await asyncio.sleep(self.sleep_sec)
        return await self.proxied.get_serialized(key)


class LoggingProxy2(StorageBackendMiddleware):
    async def get_serialized(self, key: str) -> bytes | None:
        log.error(f"get_serialized LoggingProxy2: {key}")
        return await self.proxied.get_serialized(key)


def serialize(data: dict[str, Any]) -> bytes:
    return json.dumps(data).encode()


def deserialize(data: bytes) -> dict[str, Any]:
    return json.loads(data.decode())


async def generate_stuff(sleep: int) -> dict[str, str]:
    print("Running expensive")
    await asyncio.sleep(sleep)
    return {"slept_for": sleep}


async def main() -> None:
    region = CacheRegion(
        serializer=serialize,
        deserializer=deserialize,
    )
    another_prxy = AnotherProxy(text="Another Proxy", sleep_sec=1)
    await region.configure(
        backend_class=RedisStorageBackend, backend_arguments={}, middlewares=[LoggingProxy, LoggingProxy2, another_prxy]
    )
    for _ in range(10):
        result = await region.get_or_create(
            key="hello",
            ttl_sec=5,
            lock_period_sec=2,
            generate_func=generate_stuff,
            generate_func_args=(),
            generate_func_kwargs={"sleep": 1},
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
