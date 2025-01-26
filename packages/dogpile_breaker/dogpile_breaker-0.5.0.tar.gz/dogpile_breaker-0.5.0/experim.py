import asyncio
import functools
import threading
from collections.abc import Awaitable, Callable, Hashable, Mapping
from contextlib import asynccontextmanager
from typing import AbstractSet, Any, NewType, ParamSpec, TypeAlias, TypeVar, cast

from async_timeout import timeout

TParams = ParamSpec("TParams")
R = TypeVar("R")
ArgId: TypeAlias = int | str
CacheKey = NewType("CacheKey", tuple[Hashable, ...])


class CountTask:
    task: asyncio.Task | None = None
    count: int = 0


def _get_local(local: threading.local, name: str) -> dict[CacheKey, Any]:
    try:
        return getattr(local, name)
    except AttributeError:
        container: dict[CacheKey, Any] = {}
        setattr(local, name, container)
        return container


def build_key(
    args: tuple[Any, ...],
    kwargs: Mapping[str, Any],
    ignored_args: AbstractSet[ArgId] | None = None,
) -> CacheKey:
    if not ignored_args:
        return CacheKey((args, tuple(sorted(kwargs.items()))))
    return CacheKey(
        (
            tuple(value for idx, value in enumerate(args) if idx not in ignored_args),
            tuple(item for item in sorted(kwargs.items()) if item[0] not in ignored_args),
        )
    )


def herd(fn: Callable[TParams, Awaitable[R]] | None = None, *, ignored_args: AbstractSet[ArgId] | None = None):
    print(f"Called herd with {fn=} and {ignored_args=}")

    def decorator(fn: Callable[TParams, Awaitable[R]]) -> Callable[TParams, Awaitable[R]]:
        print(f"Called with {fn=}")
        local = threading.local()

        @functools.wraps(fn)
        async def wrapped(*args: TParams.args, **kwargs: TParams.kwargs) -> R:
            # print(f'Called with {args=} and {kwargs=}')

            pending = cast(dict[CacheKey, CountTask], _get_local(local, "pending"))
            # print(pending)
            request = build_key(tuple(args), kwargs, ignored_args)
            count_task = pending.setdefault(request, CountTask())
            count_task.count += 1

            task = count_task.task
            if task is None:
                count_task.task = task = asyncio.create_task(fn(*args, **kwargs))

            try:
                return await asyncio.shield(task)
            except asyncio.CancelledError:
                print("Canceled by CancelledError after shield")
                if count_task.count == 1:
                    # await cancel(task)
                    task.cancel()
                    # try:
                    #     await task
                    # except asyncio.CancelledError:
                    #     if task.done():
                    #         return
                    #     if asyncio.current_task().cancelling() > 0:
                    #         raise
                raise

            finally:
                count_task.count -= 1
                if count_task.count == 0 or not task.cancelled():
                    if request in pending and pending[request] is count_task:
                        del pending[request]

        return wrapped

    if fn and callable(fn):
        return decorator(fn)
    return decorator


@asynccontextmanager
def herd_ctx(ignored_args: AbstractSet[ArgId] | None = None):
    local = threading.local()

    async def inner(*args, **kwargs):
        pending = cast(dict[CacheKey, CountTask], _get_local(local, "pending"))
        # print(pending)
        request = build_key(tuple(args), kwargs, ignored_args)
        count_task = pending.setdefault(request, CountTask())
        count_task.count += 1

        task = count_task.task
        if task is None:
            count_task.task = task = asyncio.create_task(fn(*args, **kwargs))

        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            print("Canceled by CancelledError after shield")
            if count_task.count == 1:
                # await cancel(task)
                task.cancel()
                # try:
                #     await task
                # except asyncio.CancelledError:
                #     if task.done():
                #         return
                #     if asyncio.current_task().cancelling() > 0:
                #         raise
            raise

        finally:
            count_task.count -= 1
            if count_task.count == 0 or not task.cancelled():
                if request in pending and pending[request] is count_task:
                    del pending[request]


@herd
async def hello(text):
    try:
        print(text)
        await asyncio.sleep(10)
        return 42
    except asyncio.CancelledError:
        print("CancelledError")
        raise


async def main():
    tasks = [hello("hello") for _ in range(10)]
    try:
        async with timeout(0.2):
            results = await asyncio.gather(*tasks)
    except asyncio.TimeoutError:
        print("Timed out")
    # result = await hello('Hello')
    # print(results)


if __name__ == "__main__":
    asyncio.run(main())
