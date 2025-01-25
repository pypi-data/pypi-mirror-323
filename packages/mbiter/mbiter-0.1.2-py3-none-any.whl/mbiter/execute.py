from __future__ import annotations

from threading import RLock
from rich import console
from rich_click import Command
from typing_extensions import TYPE_CHECKING, Any, Callable, Literal, TypeVar, Union, overload
import signal
def smart_import(module_name: str):
    """Import a module and return it."""
    return __import__(module_name, fromlist=[""])

R = TypeVar("R")
T = TypeVar("T")
_AnyCallable = Callable[..., Any]
FC = TypeVar("FC", bound=_AnyCallable | Command)

import asyncio
import logging
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed  # noqa: F401
from functools import lru_cache

import rich_click as click
from typing_extensions import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    Literal,
    TypeVar,
    Union,
    overload,
)


def get_process_executor() -> "ProcessPoolExecutor":
    """Get an optimized ProcessPoolExecutor."""
    import atexit
    import os
    import signal
    if TYPE_CHECKING:
        import multiprocessing as mp
        import os
        import sys
        from concurrent.futures import ProcessPoolExecutor
        

    else:
        ProcessPoolExecutor = smart_import('concurrent.futures.ProcessPoolExecutor')
        mp = smart_import('multiprocessing')
        ctx = mp.get_context('fork')
        os = smart_import('os')
        signal = smart_import('signal')
        atexit = smart_import('atexit')
        T = TypeVar("T")


    ctx = mp.get_context('fork')
    # Calculate optimal workers based on CPU cores and task type
    cpu_count = os.cpu_count() or 1
    max_workers = min(cpu_count * 2, 32) # Double CPU count but cap at 32

    executor = ProcessPoolExecutor(
        max_workers=max_workers,
        mp_context=ctx,
        initializer=_process_initializer,
    )

    def _cleanup():
        executor.shutdown(wait=False, cancel_futures=True)
    atexit.register(_cleanup)

    # Improved signal handling
    def _signal_handler(signum, frame):
        executor.shutdown(wait=False, cancel_futures=True)
        sys.exit(128 + signum)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    return executor

def _process_initializer():
    """Initialize process worker."""

    signal.signal(signal.SIGINT, signal.SIG_IGN)

async def process_tasks(tasks: "Iterable[Awaitable[T]]") -> "AsyncIterator[T]":
    """Process tasks and yield as they complete.
    
    Example:
        Process multiple async tasks concurrently with error handling:

        ```python
        async def example():
            # Create some example tasks
            async def task1():
                await asyncio.sleep(1)
                return "Task 1 done"
                
            async def task2():
                await asyncio.sleep(2) 
                raise ValueError("Task 2 failed")
                
            async def task3():
                await asyncio.sleep(3)
                return "Task 3 done"

            # Process tasks
            tasks = [task1(), task2(), task3()]
            async for result in process_tasks(tasks):
                print(f"Got result: {result}")
                
            # Output:
            # Got result: Task 1 done
            # Task failed: Task 2 failed 
            # Got result: Task 3 done
        ```
    
    Args:
        tasks: An iterable of awaitable tasks to process concurrently

    Yields:
        Results from completed tasks, skipping failed ones

    Raises:
        asyncio.CancelledError: If processing is cancelled
    """

    async def worker(task: Awaitable[T]) -> T | None:
        try:
            return await asyncio.shield(task)
        except asyncio.CancelledError:
            return None
        except Exception as e:
            logging.error(f"Task failed: {e}")
            return None

    pending = {asyncio.create_task(worker(task)) for task in tasks}

    while pending:
        done, pending = await asyncio.wait(
            pending,
            return_when=asyncio.FIRST_COMPLETED,
        )
        for task in done:
            try:
                result = await task
                if result is not None:
                    yield result
            except Exception as e:
                console.print(f"Task failed: {e}", style="bold red")
                logging.error(f"Failed to process result: {e}")


@overload
def get_executor(kind: 'Literal["process"]')-> "ProcessPoolExecutor":...
@overload
def get_executor(kind: 'Literal["thread"]')-> "ThreadPoolExecutor":...
@overload
def get_executor(kind: 'Literal["as_completed"]') -> "Iterable[Coroutine[Any, Any, Any]]":...
@lru_cache(None)
def get_executor(kind: 'Literal["process", "thread", "as_completed"]') -> "ThreadPoolExecutor | ProcessPoolExecutor | Callable[...,Iterable[Awaitable[Any]]]":
    """Get cached executor instance."""


    if kind == "thread":
        return ThreadPoolExecutor(
            max_workers=min(12, (os.cpu_count() or 1) * 4),
        )
    if kind == "process":
        return get_process_executor()
    if kind == "as_completed":
        return as_completed
    raise ValueError(f"Invalid executor kind: {kind}")

async def main():
    async def worker(func: Callable[[], Any]) -> Any:
        print(f"{func()=}")
    
    exec = process_tasks([worker(lambda: 1), worker(lambda: 2)])
    async for result in exec:
        print(f"{result=}")

if __name__ == "__main__":
    asyncio.run(main())