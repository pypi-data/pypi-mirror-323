# MB ITER

## Install
```bash

pip install mbiter
```

## Example

```python

from mbiter import process_tasks

async def main():
    async def worker(func: Callable[[], Any]) -> Any:
        print(f"{func()=}")
    
    exec = process_tasks([worker(lambda: 1), worker(lambda: 2)])
    async for result in exec:
        print(f"{result=}")

if __name__ == "__main__":
    asyncio.run(main())

```