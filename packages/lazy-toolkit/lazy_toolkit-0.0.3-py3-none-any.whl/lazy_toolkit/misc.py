import asyncio
from time import time
from typing import Any, Awaitable


def list_chunk(lst: list, chunk: int):
    """Loop in a list in chunks
    """
    for i in range(0, len(lst), chunk):
        yield lst[i:i + chunk]


async def cgather(n: int,
                  *tasks: Awaitable,
                  report_interval: int | None = None) -> list[Any]:
    """
    asyncio.gather with a concurrency limit and optional system load reporting.

    Binance API throttle will ban the IP
    - Too much request weight used; Please use WebSocket Streams for live updates to avoid polling the API.
    - API request limits: 6000 per minute -> 100rps
    - Futures API request limits: 2400 per minute -> 40rps
    - Set concurrent requests to 6 will get a rough RPS of 35 ~ 40, which is safe

    Args:
        n (int): The number of tasks to run concurrently.
        report_interval (Optional[int]): If set, interval in seconds for reporting load info, this simply prints the info to stdout
    """
    semaphore = asyncio.Semaphore(n)
    total_tasks: int = len(tasks)
    completed_tasks: int = 0
    start_time: float = time()

    async def sem_task(task: Awaitable) -> Any:
        nonlocal completed_tasks
        async with semaphore:
            result = await task
            completed_tasks += 1
            return result

    async def reporter():
        """Periodically reports system load info."""
        previous_completed: int = 0
        while completed_tasks < total_tasks:
            await asyncio.sleep(report_interval)  # type: ignore
            report_data = {
                'elapsed_time': time() - start_time,
                'progress': f'{completed_tasks}/{total_tasks}',
                'rps': (completed_tasks - previous_completed) / report_interval,  # type: ignore
            }
            print(f'{report_data}')
            previous_completed = completed_tasks

    # Start reporting if requested
    reporter_task = None
    if report_interval and report_interval > 0:
        reporter_task = asyncio.create_task(reporter())

    # Run tasks with the concurrency limit
    results = await asyncio.gather(*(sem_task(task) for task in tasks), return_exceptions=True)

    # Clean up reporter if it was started
    if reporter_task:
        reporter_task.cancel()
        try:
            await reporter_task
        except asyncio.CancelledError:
            pass

    return results
