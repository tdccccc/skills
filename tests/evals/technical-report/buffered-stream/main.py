import asyncio

from gateway import Gateway
from http_adapter import BufferedHttpAdapter


async def main() -> None:
    gateway = Gateway(BufferedHttpAdapter())
    print(await gateway.generate("summarize"))


if __name__ == "__main__":
    asyncio.run(main())
