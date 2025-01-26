import asyncio
import json
from typing import Any

from dogpile_breaker import CacheRegion
from dogpile_breaker.redis_backend import RedisSentinelBackend


def json_serializer(obj: Any) -> bytes:
    return json.dumps(obj).encode("utf-8")


def json_deserializer(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


cache_region = CacheRegion(
    serializer=json_serializer,
    deserializer=json_deserializer,
)


@cache_region.cache_on_arguments(
    ttl_sec=5,
    lock_period_sec=2,
    function_key_generator=lambda fn, *args, **kwargs: f"key:{args[0]}",
)
async def funk_one(index: int) -> dict[str, int | str]:
    await asyncio.sleep(1)
    return {"result": index, "status": "ok"}


async def funk_two(index: int) -> dict[str, int | str]:
    await asyncio.sleep(1)
    return {"status": f" HEHE FUNC {index}"}


async def main():
    await cache_region.configure(backend_class=RedisSentinelBackend, backend_arguments={""})
