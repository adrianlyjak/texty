import asyncio
from typing import Any, AsyncGenerator, Callable, Iterator


def async_gen_to_blocking_iterator(
    async_gen_func: Callable[..., AsyncGenerator[Any, None]], *args, **kwargs
) -> Iterator[Any]:
    async def run_async_gen():
        async_gen = async_gen_func(*args, **kwargs)
        async for item in async_gen:
            queue.put(item)
        queue.put(None)  # Sentinel value to indicate end of the generator

    queue = asyncio.Queue()
    asyncio.run(run_async_gen())

    while True:
        item = queue.get()
        if item is None:  # Sentinel value to indicate end of the generator
            break
        yield item


# Example usage:


async def async_gen_example():
    for i in range(5):
        await asyncio.sleep(1)
        yield i
