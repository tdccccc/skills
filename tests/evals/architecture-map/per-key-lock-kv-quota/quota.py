import asyncio
import json
from collections import defaultdict
from pathlib import Path


class FileKV:
    def __init__(self, path: Path) -> None:
        self.path = path

    async def get(self, key: str) -> int:
        if not self.path.exists():
            return 0
        values = json.loads(self.path.read_text(encoding="utf-8"))
        return int(values.get(key, 0))

    async def set(self, key: str, value: int) -> None:
        values: dict[str, int] = {}
        if self.path.exists():
            values = json.loads(self.path.read_text(encoding="utf-8"))
        values[key] = value
        self.path.write_text(json.dumps(values), encoding="utf-8")


class QuotaGate:
    def __init__(self, kv: FileKV, limit: int = 10) -> None:
        self.kv = kv
        self.limit = limit
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def allow(self, tenant: str) -> bool:
        try:
            async with self._locks[tenant]:
                current = await self.kv.get(tenant)
                if current >= self.limit:
                    return False
                await self.kv.set(tenant, current + 1)
                return True
        except OSError:
            return True
