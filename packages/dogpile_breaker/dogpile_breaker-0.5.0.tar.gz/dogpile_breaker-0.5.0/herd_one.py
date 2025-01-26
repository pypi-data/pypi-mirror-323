import asyncio
import sys

if sys.version_info >= (3, 11):
    from asyncio import timeout
else:
    from async_timeout import timeout


class Answer:
    def __init__(self):
        self.count = 0
        self.answer = ""


ANSWER = Answer()


async def check_backend_for_data(key: str, timeout_sec: int) -> str | None:
    global ANSWER

    try:
        async with timeout(timeout_sec):
            while True:
                ANSWER.count += 1
                if not ANSWER.answer:
                    print(f"Нет ответа для {key}, спим дальше")
                    await asyncio.sleep(timeout_sec / 4)
                else:
                    return ANSWER.answer
    except asyncio.TimeoutError:
        print("Таймаут, не ждём дальше")
        return None


async def main():
    tasks = [check_backend_for_data("dima-key", 5) for _ in range(10)]
    results = await asyncio.gather(*tasks)
    print(results)
    # await check_backend_for_data('dima-key', 5)
    print(ANSWER.count)


if __name__ == "__main__":
    asyncio.run(main())
