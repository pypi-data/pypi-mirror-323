import asyncio
import json
from datetime import timezone, datetime
from typing import Any

from dogpile_breaker import CacheRegion, RedisStorageBackend, StorageBackendMiddleware
from dogpile_breaker.redis_backend import RedisSentinelBackend


def json_serializer(obj: Any) -> bytes:
    return json.dumps(obj).encode("utf-8")


def json_deserializer(data: bytes) -> Any:
    return json.loads(data.decode("utf-8"))


cache_region = CacheRegion(serializer=json_serializer, deserializer=json_deserializer)
cache_region_regular_redis = CacheRegion(serializer=json_serializer, deserializer=json_deserializer)


@cache_region.cache_on_arguments(
    ttl_sec=10,
    lock_period_sec=2,
    function_key_generator=lambda fn, *args, **kwargs: f"key:{args[0]}",
)
async def expensive_func(sleep_for: int) -> dict[str, str]:
    await asyncio.sleep(sleep_for)
    return {"generated at": datetime.now(tz=timezone.utc).isoformat()}


@cache_region_regular_redis.cache_on_arguments(
    ttl_sec=10,
    lock_period_sec=2,
    function_key_generator=lambda fn, *args, **kwargs: f"key:{args[0]}",
)
async def expensive_func_normal_redis(sleep_for: int) -> dict[str, str]:
    await asyncio.sleep(sleep_for)
    return {"generated at": datetime.now(tz=timezone.utc).isoformat()}


async def main_normal_redis():
    await cache_region_regular_redis.configure(
        backend_class=RedisStorageBackend,
        backend_arguments={
            "host": "127.0.0.1",
            "port": 7480,
            "db": 0,
            "max_connections": 200,
            "timeout": 20,
        },
    )
    while True:
        result = await expensive_func_normal_redis(1)
        print(result)
        await asyncio.sleep(0.5)


async def main():
    await cache_region.configure(
        backend_class=RedisSentinelBackend,
        backend_arguments={
            "sentinels": [
                ("127.0.0.1", 26379),
                ("127.0.0.1", 26380),
                ("127.0.0.1", 26381),
            ],
            "master_name": "mymaster",
            "max_connections": 200,
            "db": 0,
        },
    )
    while True:
        result = await expensive_func(1)
        print(result)
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
