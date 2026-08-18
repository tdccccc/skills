import asyncio
import os
from pathlib import Path

from quota import FileKV, QuotaGate
from routes import admin_request, public_request


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    gate: QuotaGate,
) -> None:
    route, tenant = (await reader.readline()).decode("utf-8").strip().split(maxsplit=1)
    if route == "public":
        status = await public_request(tenant, gate)
    elif route == "admin":
        status = await admin_request(tenant)
    else:
        status = 404
    writer.write(f"{status}\n".encode("utf-8"))
    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def serve() -> None:
    kv = FileKV(Path(os.environ.get("QUOTA_FILE", "/data/quota.json")))
    gate = QuotaGate(kv)
    server = await asyncio.start_server(
        lambda reader, writer: handle_client(reader, writer, gate),
        host="0.0.0.0",
        port=8080,
    )
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(serve())
