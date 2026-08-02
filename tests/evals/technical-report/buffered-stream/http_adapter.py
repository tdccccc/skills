class Response:
    async def read(self) -> bytes:
        return b"first chunk\nsecond chunk\n"


class BufferedHttpAdapter:
    async def post_json(self, path: str, payload: dict[str, object]) -> str:
        response = await self._send(path, payload)
        complete_body = await response.read()
        return complete_body.decode("utf-8")

    async def _send(self, path: str, payload: dict[str, object]) -> Response:
        return Response()
