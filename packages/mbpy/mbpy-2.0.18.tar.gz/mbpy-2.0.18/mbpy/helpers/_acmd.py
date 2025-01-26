import asyncio
from typing import AsyncGenerator, Coroutine, TypeVar
from typing_extensions import Any

ConsT = TypeVar("ConsT")
RetT = TypeVar("RetT")
async def as_completed(*functions: AsyncGenerator[Any,RetT] | Coroutine[Any,Any,RetT]) -> AsyncGenerator[Any,RetT]:
    """Run any number of async generator functions or coroutines concurrently
    and stream results as they are produced.
    
    Parameters:
        *functions: List of async generator functions or coroutines to execute.

    Behavior:
        - Yields results as each task completes.
    """  # noqa: D205
    # Wrap each function or coroutine in a generator if it's not already
    async def wrap_function(func):
        if asyncio.iscoroutinefunction(func):
            result = await func() 
            yield result
        else:
            async for item in func():
                yield item

    # Create tasks for all wrapped functions
    generators = [wrap_function(func) for func in functions]
    tasks = {generator: asyncio.create_task(generator.__anext__()) for generator in generators}

    print("Streaming Results:")
    while tasks:
        # Wait for any generator to yield a result
        done, _ = await asyncio.wait(tasks.values(), return_when=asyncio.FIRST_COMPLETED)

        for completed_task in done:
            try:
                # Get the completed result and print it
                result = completed_task.result()
                print(result)

                # Find the generator corresponding to the completed task
                for generator, task in tasks.items():
                    if task == completed_task:
                        # Schedule the next item from this generator
                        tasks[generator] = asyncio.create_task(generator.__anext__())
                        break
            except StopAsyncIteration:
                # Remove the generator if it is exhausted
                to_remove = [gen for gen, task in tasks.items() if task == completed_task]
                for gen in to_remove:
                    tasks.pop(gen, None)
    return