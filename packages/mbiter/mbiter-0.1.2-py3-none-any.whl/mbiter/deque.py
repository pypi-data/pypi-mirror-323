
import asyncio
from collections import deque
from asyncio.mixins import _LoopBoundMixin
from asyncio import locks


class AsyncDeque(_LoopBoundMixin):
    """
    An asyncio-compatible deque implementation with left-specific versions
    of all asyncio.Queue methods.
    """

    def __init__(self, maxsize=0):
        self._maxsize = maxsize
        self._queue = deque()
        self._getters = deque()
        self._putters = deque()
        self._unfinished_tasks = 0
        self._finished = locks.Event()
        self._finished.set()

    def __len__(self):
        """Return the current size of the deque."""
        return len(self._queue)

    def full(self):
        """Return True if the deque is full."""
        return 0 < self._maxsize <= len(self._queue)

    def empty(self):
        """Return True if the deque is empty."""
        return not self._queue

    def qsize(self):
        """Return the size of the deque."""
        return len(self._queue)

    def _wakeup_next(self, waiters):
        """Wake up the next waiter that isn't canceled."""
        while waiters:
            waiter = waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                break

    async def put(self, item):
        """Add an item to the right end of the deque asynchronously."""
        await self._put(item, to_left=False)

    async def put_left(self, item):
        """Add an item to the left end of the deque asynchronously."""
        await self._put(item, to_left=True)

    def put_nowait(self, item):
        """Add an item to the right end of the deque without blocking."""
        self._put_nowait(item, to_left=False)

    def put_left_nowait(self, item):
        """Add an item to the left end of the deque without blocking."""
        self._put_nowait(item, to_left=True)

    async def get(self):
        """Remove and return an item from the right end of the deque asynchronously."""
        return await self._get(from_left=False)

    async def get_left(self):
        """Remove and return an item from the left end of the deque asynchronously."""
        return await self._get(from_left=True)

    def get_nowait(self):
        """Remove and return an item from the right end of the deque without blocking."""
        return self._get_nowait(from_left=False)

    def get_left_nowait(self):
        """Remove and return an item from the left end of the deque without blocking."""
        return self._get_nowait(from_left=True)

    async def _put(self, item, to_left=False):
        """Internal method to handle async put operations."""
        loop = self._get_loop()
        while self.full():
            putter = loop.create_future()
            self._putters.append(putter)
            try:
                await putter
            except:
                putter.cancel()
                self._putters.remove(putter)
                raise
        if to_left:
            self._queue.appendleft(item)
        else:
            self._queue.append(item)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)

    def _put_nowait(self, item, to_left=False):
        """Internal method to handle non-blocking put operations."""
        if self.full():
            raise RuntimeError("Queue full")
        if to_left:
            self._queue.appendleft(item)
        else:
            self._queue.append(item)
        self._unfinished_tasks += 1
        self._finished.clear()
        self._wakeup_next(self._getters)

    async def _get(self, from_left=True):
        """Internal method to handle async get operations."""
        loop = self._get_loop()
        while self.empty():
            getter = loop.create_future()
            self._getters.append(getter)
            try:
                await getter
            except:
                getter.cancel()
                self._getters.remove(getter)
                raise
        return self._get_nowait(from_left)

    def _get_nowait(self, from_left=True):
        """Internal method to handle non-blocking get operations."""
        if self.empty():
            raise RuntimeError("Queue empty")
        if from_left:
            item = self._queue.popleft()
        else:
            item = self._queue.pop()
        self._wakeup_next(self._putters)
        return item

    def task_done(self):
        """Indicate that a dequeued task is complete."""
        if self._unfinished_tasks <= 0:
            raise ValueError('task_done() called too many times')
        self._unfinished_tasks -= 1
        if self._unfinished_tasks == 0:
            self._finished.set()

    async def join(self):
        """Block until all items in the deque have been processed."""
        if self._unfinished_tasks > 0:
            await self._finished.wait()



    # Define the test again
    async def test_async_deque_left_right():
        """Test AsyncDeque with left and right operations."""
        deque = AsyncDeque(maxsize=5)

        async def producer_left():
            for i in range(5):
                await deque.put_left(f"Left Item {i}")
                print(f"Produced to left: Left Item {i}")
                await asyncio.sleep(0.1)

        async def producer_right():
            for i in range(5):
                await deque.put(f"Right Item {i}")
                print(f"Produced to right: Right Item {i}")
                await asyncio.sleep(0.1)

        async def consumer_left():
            for _ in range(5):
                item = await deque.get_left()
                print(f"Consumed from left: {item}")
                deque.task_done()
                await asyncio.sleep(0.2)

        async def consumer_right():
            for _ in range(5):
                item = await deque.get()
                print(f"Consumed from right: {item}")
                deque.task_done()
                await asyncio.sleep(0.2)

        # Create producers and consumers
        producers = [
            asyncio.create_task(producer_left()),
            asyncio.create_task(producer_right()),
        ]
        consumers = [
            asyncio.create_task(consumer_left()),
            asyncio.create_task(consumer_right()),
        ]

        # Run all producers and consumers
        await asyncio.gather(*producers)
        await deque.join()
        for c in consumers:
            c.cancel()

    # Execute the test
    await test_async_deque_left_right()